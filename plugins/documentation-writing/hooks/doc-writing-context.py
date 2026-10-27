#!/usr/bin/env python3
"""PreToolUse: hold prose a human reads to the documentation-writing rules.

Advises on every commit message, PR body and doc file, and blocks the ones
breaking a rule that can be checked mechanically. Advice alone does not work:
it arrives as one more system-reminder once the prose is already composed in
the heredoc, which is easy to read and ship anyway. A denial is not.

A commit also gets its staged diff read. Guarding only the message let prose
ship inside `values.yaml` comments -- unreachable both because the path was
not `docs/` or `*.md`, and because the edit was a `python3 - <<PY` heredoc,
which carries no `file_path` at all. At commit time the prose is on disk
whatever wrote it, so that is the one checkpoint no editing style routes
around.

Silent (exit 0, no output) for everything else.
"""
import json
import re
import subprocess
import sys

RULES = (
    "documentation-writing (CLAUDE.md requires it) applies to this action. "
    "Prose here is WHY, not WHAT. Commit message: why the change exists and "
    "what breaks without it. PR description: why it exists, plus what the "
    "reviewer must actually check -- the diff already states what changed, so "
    "do not restate it or copy tables and code out of it. Code comments: why, "
    "not what. Cut any line the text still works without."
)

# Match the API form too: some forges only accept PR bodies through it.
PROSE_CMD = re.compile(
    r"git\s+commit"
    r"|(?:gh|forgejo)\s+pr\s+(?:create|edit)"
    r"|(?:gh|forgejo)\s+api\s+(?:POST|PATCH|PUT)\s+\S*/(?:pulls|issues)"
)
PROSE_PATH = re.compile(r"(^|/)docs/|\.md$")

CD_PREFIX = re.compile(r"^\s*cd\s+([^\s&|;]+)\s*&&")
COMMENT = re.compile(r"^\+\s*(?:#|//|--)\s?")
COMMIT = re.compile(r"git\s+commit")
# 22 consecutive added comment lines was an annotated catalogue of five
# overrides the same commit deleted. Prose that long in a config file is a
# document; it belongs in docs/ or an ADR, where length is legitimate.
MAX_COMMENT_RUN = 20

HEREDOC = re.compile(r"<<-?\s*'?([A-Za-z_][A-Za-z0-9_]*)'?\s*\n(.*?)\n\1\b", re.S)
CODE_LINE = re.compile(r"^\s*(?:import |from \S+ import |def |class |#!/)", re.M)

TABLE = (
    re.compile(r"^\s*\|.*\|\s*$", re.M),
    "a Markdown table. Do not copy tables out of the diff or out of your own "
    "probing -- state the conclusion instead.",
)
NARRATION = (
    re.compile(
        r"\b(?:I measured|worth recording|turns? out|"
        r"(?:first|second|earlier|another) attempt)\b",
        re.I,
    ),
    "verification narration or editing history. The reader needs the current "
    "state, not how you arrived at it.",
)
MAX_LINES = 30


def prose_heredocs(cmd):
    """Heredoc bodies that carry prose, skipping ones carrying code."""
    for delim, body in HEREDOC.findall(cmd):
        if "PY" in delim.upper() or CODE_LINE.search(body):
            continue
        yield body


def staged_prose(cmd, cwd):
    """Added prose in the staged diff: Markdown lines, and comment lines.

    Returns (text, longest_comment_run). Silent on any git failure -- this is
    a lint, and a commit outside a repo is git's error to report, not ours.
    """
    match = CD_PREFIX.search(cmd)
    where = match.group(1) if match else cwd
    if not where:
        return "", 0
    try:
        diff = subprocess.run(
            ["git", "-C", where, "diff", "--cached", "--unified=0"],
            capture_output=True, text=True, timeout=10,
        ).stdout
    except Exception:
        return "", 0

    prose, run, longest, markdown = [], 0, 0, False
    for line in diff.splitlines():
        if line.startswith("+++ "):
            markdown = line.endswith(".md")
            run = 0
            continue
        if not line.startswith("+") or line.startswith("+++"):
            run = 0
            continue
        if COMMENT.match(line):
            prose.append(COMMENT.sub("", line))
            run += 1
            longest = max(longest, run)
        elif markdown:
            prose.append(line[1:])
            run = 0
        else:
            run = 0
    return "\n".join(prose), longest


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    tool_input = data.get("tool_input") or {}
    cmd = tool_input.get("command") or ""
    path = tool_input.get("file_path") or ""
    content = tool_input.get("content") or tool_input.get("new_string") or ""

    is_cmd = bool(PROSE_CMD.search(cmd))
    if not is_cmd and not PROSE_PATH.search(path):
        return 0

    problems = []
    if COMMIT.search(cmd):
        text, run = staged_prose(cmd, data.get("cwd") or "")
        if NARRATION[0].search(text):
            problems.append(NARRATION[1])
        if run > MAX_COMMENT_RUN:
            problems.append(
                f"a {run}-line comment block. Prose that long in a config file "
                "is a document -- move it to docs/ or an ADR, or cut it to the "
                "lines that govern the next edit to this file."
            )
    if is_cmd:
        # A commit message or PR body: every check applies.
        for body in prose_heredocs(cmd):
            for pattern, why in (TABLE, NARRATION):
                if pattern.search(body):
                    problems.append(why)
            lines = len(body.splitlines())
            if lines > MAX_LINES:
                problems.append(
                    f"{lines} lines, over the {MAX_LINES} this should need. "
                    "Cut every line the text still works without."
                )
    elif NARRATION[0].search(content):
        # A doc file. Tables and length are legitimate here; narration is not.
        problems.append(NARRATION[1])

    if problems:
        seen = list(dict.fromkeys(problems))
        reason = "Rewrite before running this. It contains " + " It contains ".join(
            seen
        )
        out = {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": f"{reason}\n\n{RULES}",
        }
    else:
        out = {"hookEventName": "PreToolUse", "additionalContext": RULES}

    json.dump({"hookSpecificOutput": out}, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
