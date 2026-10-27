#!/usr/bin/env python3
"""Self-check for doc-writing-context.py. Run it directly; no framework.

The staged-diff cases cover YAML comments written through a `python3 - <<PY`
heredoc, which neither the path checks nor the heredoc checks can see.
"""
import json
import pathlib
import subprocess
import tempfile

HOOK = str(pathlib.Path(__file__).with_name("doc-writing-context.py"))

PR_WITH_TABLE = """\
The config map is read in exactly one place.

| call | full dump | filtered |
| --- | --- | --- |
| /api/items | 23-44s | 0.2s |
"""

PR_WITH_NARRATION = """\
Pointing the API at the Service skips the proxy.

## Verification

Timing needed a second attempt worth recording.
"""

PR_CLEAN = """\
API calls looped back through the shared proxy, which rejected
every call.

## What to check

Whether routing around the proxy is the call you want here.
"""


def run(tool_input):
    p = subprocess.run(
        [HOOK], input=json.dumps({"tool_input": tool_input}),
        capture_output=True, text=True,
    )
    if not p.stdout.strip():
        return "SILENT"
    out = json.loads(p.stdout)["hookSpecificOutput"]
    return "DENY" if out.get("permissionDecision") == "deny" else "ADVISE"


def pr(body):
    return {"command": "cat > /tmp/b.md <<'MSG'\n" + body + "\nMSG\n"
            "forgejo api POST /repos/OWNER/REPO/pulls -f body=\"$(cat /tmp/b.md)\""}


def staged(name, text):
    """A commit in a throwaway repo with `text` staged as `name`."""
    repo = tempfile.mkdtemp()
    subprocess.run(["git", "init", "-q", repo], check=True)
    for k, v in (("user.email", "t@t"), ("user.name", "t")):
        subprocess.run(["git", "-C", repo, "config", k, v], check=True)
    pathlib.Path(repo, name).write_text(text)
    subprocess.run(["git", "-C", repo, "add", name], check=True)
    return {"command": f"cd {repo} && git commit -m 'chore: x'"}


ABSENCE_CATALOGUE = "k: v\n" + "\n".join(
    ["    # Deliberately absent from the overrides below, keeping the default:"]
    + [f"    #   RuleName{i}  why this rule is not in this file." for i in range(21)]
)
LOAD_BEARING = "k: v\n" + "\n".join(
    [f"    # etcd override rationale line {i}, load-bearing." for i in range(18)]
)


def commit(body):
    return {"command": "git commit -F - <<'MSG'\n" + body + "\nMSG"}


CASES = [
    ("PR body with a table", pr(PR_WITH_TABLE), "DENY"),
    ("PR body with narration", pr(PR_WITH_NARRATION), "DENY"),
    ("PR body over the line cap", pr("why\n" * 40), "DENY"),
    ("PR body that is clean", pr(PR_CLEAN), "ADVISE"),
    ("commit message with narration", commit(PR_WITH_NARRATION), "DENY"),
    ("commit message that is clean", commit(PR_CLEAN), "ADVISE"),
    # Some forges reject `pr create`, so the API form must be caught too.
    ("api form is matched", pr(PR_WITH_TABLE), "DENY"),
    ("python heredoc is not prose",
     {"command": "python3 - <<'PYEOF'\nimport os\ndef f(): pass\nPYEOF\n"
                 "git commit -m 'fix(x): y'"}, "ADVISE"),
    ("tables are fine in a doc file",
     {"file_path": "docs/x.md", "content": "| a | b |\n| --- | --- |\n"}, "ADVISE"),
    ("narration is not fine in a doc file",
     {"file_path": "docs/x.md", "content": "This corrects an earlier attempt.\n"},
     "DENY"),
    # A long annotated index of overrides, written via a python heredoc.
    ("staged absence catalogue", staged("values.yaml", ABSENCE_CATALOGUE), "DENY"),
    ("staged narration in a YAML comment",
     staged("v.yaml", "k: v\n    # I verified this and it turns out fine.\n"), "DENY"),
    ("staged narration in Markdown, any editor",
     staged("d.md", "# D\n\nTiming needed a second attempt worth recording.\n"), "DENY"),
    # A long comment that earns its length must still get through.
    ("staged load-bearing comment", staged("v.yaml", LOAD_BEARING), "ADVISE"),
    ("staged clean short comment",
     staged("v.yaml", "k: v\n    # Re-tiering re-keys the group.\n"), "ADVISE"),
    ("unrelated command stays silent", {"command": "kubectl get pods -A"}, "SILENT"),
]

if __name__ == "__main__":
    failed = 0
    for name, tool_input, want in CASES:
        got = run(tool_input)
        if got != want:
            failed += 1
            print(f"FAIL {name}: want {want}, got {got}")
    print(f"{len(CASES) - failed}/{len(CASES)} pass")
    raise SystemExit(1 if failed else 0)
