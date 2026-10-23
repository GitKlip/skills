#!/usr/bin/env python3
"""GitHub mechanics for the create-story skill.

The repo is the current one (gh repo view). The board and area tags come from
.claude/board.json at the repo root:
  {"owner": "<org-or-user>", "project": <number>, "tags": {"CORE": "what it covers", ...}}

  story.py lint --title T --body-file F       check the format; exit 1 on errors
  story.py permalink <path>[:<start>[-<end>]]  link to a file pinned to a pushed commit
  story.py create --title T --body-file F [--tag CORE] [--type Feature] [--priority High] [--status Backlog]
  story.py verify <issue>                      re-check the issue as GitHub stored it

create runs lint first, and reuses an issue with the exact same title instead of
duplicating it, so a bulk run is safe to re-run. It prints one line of JSON:
  {"created": bool, "title": str, "issue_number": int, "issue_url": str}
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SECTIONS = ["## User story", "## Intent", "## Acceptance criteria"]
DETAILS = "## Details"
CODE_HINTS = [
    (r"`", "backtick"),
    (r"\b[\w/-]+\.(ts|tsx|js|jsx|py|md|json|css|sql)\b", "file name"),
    (r"\b\w+\(\)", "function call"),
    (r"\b[a-z]+[A-Z]\w*\b", "camelCase identifier"),
    (r"\b[a-z]+_[a-z_]+\b", "snake_case identifier"),
]


# ---------- helpers ----------

def run(*args, check=True):
    result = subprocess.run(args, capture_output=True, text=True)
    if check and result.returncode != 0:
        sys.exit(f"$ {' '.join(args)}\n{result.stderr.strip()}")
    return result.stdout.strip()


def warn(message):
    sys.stderr.write(f"warning: {message}\n")


def config():
    path = Path(run("git", "rev-parse", "--show-toplevel")) / ".claude" / "board.json"
    if not path.exists():
        sys.exit(f'missing {path} — create it as {{"owner": "...", "project": <number>, "tags": {{...}}}}')
    return json.loads(path.read_text())


def repo():
    return run("gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner")


# ---------- lint ----------

def lint(title, body, tags):
    errors, warnings = [], []

    match = re.match(r"^\[([A-Z]+)\] (.+)$", title)
    if not match:
        errors.append('title must be "[TAG] three to five words"')
    else:
        tag, words = match.group(1), match.group(2).split()
        if tags and tag not in tags:
            warnings.append(f"tag [{tag}] is new (known: {', '.join(tags)}) — confirm it with the user")
        if not 3 <= len(words) <= 5:
            errors.append(f"title has {len(words)} words after the tag; use 3 to 5")

    lines = body.splitlines()
    try:
        rule = next(i for i, line in enumerate(lines) if line.strip() == "---")
    except StopIteration:
        return errors + ["body needs a --- rule between the top half and Details"], warnings
    top, bottom = "\n".join(lines[:rule]), "\n".join(lines[rule + 1:])

    positions = [top.find(s) for s in SECTIONS]
    for section, pos in zip(SECTIONS, positions):
        if pos < 0:
            errors.append(f'missing "{section}" above the rule')
    if all(p >= 0 for p in positions) and positions != sorted(positions):
        errors.append("top-half sections must be in order: " + ", ".join(SECTIONS))
    if not bottom.lstrip().startswith(DETAILS):
        errors.append(f'the rule must be followed by "{DETAILS}"')

    def section_text(name):
        start = top.find(name)
        if start < 0:
            return ""
        rest = top[start + len(name):]
        nxt = min([rest.find(s) for s in SECTIONS if rest.find(s) >= 0] or [len(rest)])
        return rest[:nxt].strip()

    story = section_text("## User story")
    if story and not re.match(r"^As (a|an|the) ", story):
        warnings.append('user story should read "As a <real role>, I want …, so that …"')

    sentences = [s for s in re.split(r"(?<=[.!?])\s+", section_text("## Intent")) if s.strip()]
    if sentences and not 2 <= len(sentences) <= 5:
        warnings.append(f"intent has {len(sentences)} sentences; aim for 2 to 5")

    criteria = [l for l in section_text("## Acceptance criteria").splitlines() if re.match(r"^\s*- ", l)]
    if not 3 <= len(criteria) <= 6:
        errors.append(f"acceptance criteria has {len(criteria)} items; use 3 to 6")

    for pattern, label in CODE_HINTS:
        hits = sorted(set(m.group(0) for m in re.finditer(pattern, top)))
        if hits:
            message = f"{label} above the rule: {', '.join(hits[:5])} — move code details below the rule"
            (errors if label == "backtick" else warnings).append(message)

    if re.search(r"(?im)^\**depends on", top):
        errors.append('"Depends on" belongs in Details, below the rule')
    return errors, warnings


def report(errors, warnings):
    for w in warnings:
        warn(w)
    for e in errors:
        sys.stderr.write(f"error: {e}\n")
    return not errors


# ---------- permalink ----------

def permalink(spec):
    path, _, lines = spec.partition(":")
    default = run("gh", "repo", "view", "--json", "defaultBranchRef", "-q", ".defaultBranchRef.name")
    run("git", "fetch", "--quiet", "origin", default)
    sha = run("git", "rev-parse", f"origin/{default}")
    if subprocess.run(["git", "cat-file", "-e", f"{sha}:{path}"], capture_output=True).returncode != 0:
        sys.exit(f"{path} does not exist on origin/{default} ({sha[:7]}) — only link pushed code")
    anchor = ""
    if lines:
        start, _, end = lines.partition("-")
        anchor = f"#L{start}" + (f"-L{end}" if end else "")
    return f"https://github.com/{repo()}/blob/{sha}/{path}{anchor}"


# ---------- create ----------

def find_existing(repo_name, title):
    # Search on the words without the [TAG] (GitHub tokenizes brackets oddly), then match exactly.
    term = re.sub(r"^\[[A-Z]+\]\s*", "", title)
    items = json.loads(run("gh", "issue", "list", "--repo", repo_name, "--state", "all", "--search",
                           f'"{term}" in:title', "--json", "number,title,url", "--limit", "100") or "[]")
    return next((i for i in items if i["title"] == title), None)


def ensure_label(repo_name, label):
    existing = json.loads(run("gh", "label", "list", "--repo", repo_name, "--json", "name", "--limit", "500"))
    if label not in {l["name"] for l in existing}:
        run("gh", "label", "create", label, "--repo", repo_name, "--description", "Story area (create-story)")


def set_issue_type(repo_name, owner, number, type_name):
    # Issue Types are org-level; a user-owned repo has none, so this only warns.
    result = subprocess.run(["gh", "api", f"orgs/{owner}/issue-types"], capture_output=True, text=True)
    if result.returncode != 0:
        return warn(f"no issue types for {owner}; leaving Type unset")
    match = next((t for t in json.loads(result.stdout)
                  if t["is_enabled"] and t["name"].lower() == type_name.lower()), None)
    if not match:
        return warn(f"no enabled issue type {type_name!r}; leaving Type unset")
    node = run("gh", "issue", "view", str(number), "--repo", repo_name, "--json", "id", "-q", ".id")
    run("gh", "api", "graphql", "-f",
        "query=mutation($id: ID!, $t: ID!) { updateIssue(input: {id: $id, issueTypeId: $t}) { issue { id } } }",
        "-f", f"id={node}", "-f", f"t={match['node_id']}")


def set_field(cfg, project_id, item_id, field_name, option_name):
    fields = json.loads(run("gh", "project", "field-list", str(cfg["project"]), "--owner", cfg["owner"],
                            "--format", "json"))["fields"]
    field = next((f for f in fields if f["name"] == field_name), None)
    option = next((o for o in (field or {}).get("options", []) if o["name"].lower() == option_name.lower()), None)
    if not option:
        return warn(f"no {field_name} option {option_name!r} on the board; leaving it unset")
    run("gh", "project", "item-edit", "--id", item_id, "--project-id", project_id,
        "--field-id", field["id"], "--single-select-option-id", option["id"])


def create(args):
    cfg, repo_name = config(), repo()
    body = Path(args.body_file).read_text()
    if not report(*lint(args.title, body, cfg.get("tags", {}))):
        sys.exit(1)

    existing = find_existing(repo_name, args.title)
    if existing:
        print(json.dumps({"created": False, "title": args.title,
                          "issue_number": existing["number"], "issue_url": existing["url"]}))
        return

    tag = args.tag or re.match(r"^\[([A-Z]+)\]", args.title).group(1)
    label = f"area:{tag.lower()}"
    ensure_label(repo_name, label)
    url = run("gh", "issue", "create", "--repo", repo_name, "--title", args.title,
              "--body-file", args.body_file, "--label", label).splitlines()[-1]
    number = int(url.rstrip("/").rsplit("/", 1)[-1])

    if args.type:
        set_issue_type(repo_name, cfg["owner"], number, args.type)
    project_id = json.loads(run("gh", "project", "view", str(cfg["project"]), "--owner", cfg["owner"],
                                "--format", "json"))["id"]
    item_id = json.loads(run("gh", "project", "item-add", str(cfg["project"]), "--owner", cfg["owner"],
                             "--url", url, "--format", "json"))["id"]
    set_field(cfg, project_id, item_id, "Status", args.status)
    if args.priority:
        set_field(cfg, project_id, item_id, "Priority", args.priority)

    print(json.dumps({"created": True, "title": args.title, "issue_number": number, "issue_url": url}))


# ---------- verify ----------

def verify(number):
    cfg, repo_name = config(), repo()
    issue = json.loads(run("gh", "issue", "view", str(number), "--repo", repo_name, "--json",
                           "title,body,labels,url,issueType,projectItems"))
    ok = report(*lint(issue["title"], issue["body"], cfg.get("tags", {})))
    on_board = [p for p in issue.get("projectItems", [])]
    labels = [l["name"] for l in issue["labels"]]
    print(json.dumps({
        "url": issue["url"],
        "format_ok": ok,
        "labels": labels,
        "type": (issue.get("issueType") or {}).get("name"),
        "board": [{"project": p.get("title"), "status": (p.get("status") or {}).get("name")} for p in on_board],
    }, indent=1))
    if not ok or not on_board:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_lint = sub.add_parser("lint")
    p_lint.add_argument("--title", required=True)
    p_lint.add_argument("--body-file", required=True)

    p_link = sub.add_parser("permalink")
    p_link.add_argument("spec", help="path[:start[-end]], relative to the repo root")

    p_create = sub.add_parser("create")
    p_create.add_argument("--title", required=True)
    p_create.add_argument("--body-file", required=True)
    p_create.add_argument("--tag", help="area tag; defaults to the title's [TAG]")
    p_create.add_argument("--type", default="", help="native Issue Type, e.g. Feature or Spike")
    p_create.add_argument("--priority", default="", help="Priority option, if the board has one")
    p_create.add_argument("--status", default="Backlog")

    p_verify = sub.add_parser("verify")
    p_verify.add_argument("issue", type=int)

    args = parser.parse_args()
    if args.command == "lint":
        ok = report(*lint(args.title, Path(args.body_file).read_text(), config().get("tags", {})))
        print("format ok" if ok else "format has errors")
        sys.exit(0 if ok else 1)
    elif args.command == "permalink":
        print(permalink(args.spec))
    elif args.command == "create":
        create(args)
    elif args.command == "verify":
        verify(args.issue)


if __name__ == "__main__":
    main()
