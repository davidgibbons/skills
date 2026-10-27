---
name: documentation-writing
description: Rules for writing and reviewing documentation, READMEs, runbooks, PR descriptions, and code comments. Use when writing new docs, editing existing docs, reviewing docs in a PR, or writing comments and docstrings.
---

# Documentation Writing

Write for the reader, not for the writer. Every line earns its place or gets deleted.

## Rules

### 1. Does this need to exist at all?

Before writing a new file, check whether the content belongs somewhere that already exists: a section in an existing doc, a code comment, a docstring — or nowhere, because a sibling doc already covers it. Most redundant docs are born, not edited into existence. Only write a new document when nothing already serves the reader's need.

### 2. Plain, direct, scannable

Simple words over complex ones. A sentence over a paragraph when both deliver the same content. Active voice over passive. Headers, lists, tables, and images over several paragraphs in a row — numbered lists for ordered steps, bullets for unordered sets.

- Don't: "It's often the case that users who are attempting a migration will wish to keep a copy of the old configuration as according to their organization's business continuity manual."
- Do: "Save a copy of your configuration before migrating."

### 3. Define a complex word once, properly

If a term is unavoidable, define it on first use:

> In this documentation, **cohort** means a group of users who are advertised to.

Then use it consistently. Don't redefine it, don't swap in synonyms.

### 4. Focus on the reader

Before writing, answer:

- Why would someone open this document? What do they want?
- Is the reader highly technical, or an average end user?
- What do they already know how to do? Don't re-explain concepts standard to their role — a paragraph defining a tool or service the reader uses daily is background, not information, no matter how well written.
- Do they need code samples? Screenshots?

Write for that reader only. Cut anything that serves a different one, including anything they already know. When judging whether a passage is "appropriately thorough" or "just wordy," assume wordy — most technical documentation errs toward over-explaining, not under-explaining.

### 5. Stick to consistent terminology

- American English, consistently — unless the doc set you're editing is already British.
- Capitalize product and technology names the same way every time (SQL, PostgreSQL, GitHub) — no exceptions.
- One name per thing. Don't alternate between "job", "task", and "run" for the same concept.

### 6. Delete anything that doesn't earn its place

If the document still achieves its goal with a line gone, the line goes. This includes:

- Restating the header in the first sentence
- "This document will explain..." preambles
- Background nobody asked for, including explanations of concepts the target reader already knows
- Warnings about things that can't happen
- Commentary about the document's own history ("this corrects an earlier draft", "updated from...") — the reader needs the current state, not its editing history
- Anything a sibling document already covers — link to it instead of restating it

Never cut in the name of brevity: a safety or irreversibility warning ("this command deletes data", "this cannot be undone"), a prerequisite the reader needs to avoid getting stuck, or a known limitation/edge case — if it's genuinely out of scope, say so in one line rather than let the reader discover it the hard way.

## Comments and docstrings

The same rules apply, plus:

- Comment why, not what. The code already says what.
- One line by default, two at most. Longer means you are explaining
  background or history; cut it.
- State the reason itself. "Same pattern as X" or "same reason as X" is not a
  reason; the reader shouldn't have to open X.
- Copied a sibling file? Rewrite or delete its comments; don't rename them.
- Revising a comment must leave it no longer than before.
- No comment is better than a comment that restates the line below it.
- Keep comments true. A stale comment is worse than none.

## Don't document the debugging session

The commonest failure when writing about code you just fixed: the comment
records how you found the problem instead of what the reader needs. The
incident is fresh for you and never happened to them.

Cut what the old system did, which error appeared, how many attempts it took,
what you tried first. Keep the constraint that still binds and why the code is
shaped around it.

- Don't: "act_runner gave us bash, but GitHub defaults container jobs to sh,
  so `set -o pipefail` died with 'Illegal option' on the first real run after
  the migration. Declared here so a new step cannot reintroduce it."
- Do: "GitHub defaults container jobs to `sh`, which lacks `set -o pipefail`."

Two tells that you are doing it: a comment longer than the thing it explains,
and the same explanation pasted into several files.

## Runbooks and PR descriptions

Same rules, different reader:

- **Runbook** — the reader is mid-incident and scanning, not studying. Exact copy-pasteable commands first, explanation after. Mark an irreversible step before its command, not below it.
- **PR description** — why the change exists, what changed, and what the reviewer needs to check. Summarize the change in a line or two; don't replay the diff file by file. Where the repo mandates narrative sections, fill them.

## Code samples and commands

Validate every command and code sample before publishing it — a stale sample is worse than none, because the reader trusts it and pastes it as-is. Run it in a safe environment that stands in for the real one, never against production.

Validate a destructive or production-only step *without* running it: a dry run (`--dry-run`, `--check`, a plan or diff), a run against a scratch resource, or review by someone who has done it for real. Publishing a doc is never a reason to execute a command that deletes data or takes a service down.

## Review checklist

Run the rules above over the document, then check the two things they don't cover:

1. Fixing a wrong or stale fact? Check whether it's duplicated in other docs and fix it at the source, not just where it was flagged.
2. Are the commands and code samples still correct? Validate them the same way — safe environment, and dry run or peer review for anything destructive.

## Applying this skill

When editing or reviewing someone else's doc, don't narrate the pass. State each cut in one line — `cut: <what> (<why>)` — not a walkthrough of your reasoning. The same economy this skill asks of documentation applies to describing the edit.
