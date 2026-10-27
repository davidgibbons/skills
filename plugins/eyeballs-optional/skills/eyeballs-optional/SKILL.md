---
name: eyeballs-optional
description: Recommend whether a GitHub pull request is eyeballs optional (EO, safe to merge without close human review) or eyeballs required (ER), using a jev model through a SystemOne endpoint. Use when the user asks "is this PR eyeballs optional", "EO or ER", "does this PR need review", or invokes /eyeballs-optional with a PR URL.
---

# Eyeballs optional

Run the bundled script against the PR. It never changes the PR.

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/eyeballs_optional.py" https://github.com/OWNER/REPO/pull/NUMBER
```

| Setting | Required | Default |
|---|---|---|
| `SYSTEMONE_URL` or `--endpoint` | yes | none; the complete POST URL, e.g. `http://localhost:8000/v1/systemone` |
| `SYSTEMONE_API_KEY` | no | none |
| `SYSTEMONE_MODEL` or `--model` | no | `jev-latest` |
| `--repo PATH` | no | a temporary clone |

GitHub access comes from `GITHUB_API_KEY`, `GITHUB_TOKEN` or `GH_TOKEN`, then `gh` auth.

If `SYSTEMONE_URL` is unset, ask the user for it. Don't guess one.

## Reporting the result

Relay the `Verdict:` line and the model's choice and confidence. EO is a candidate, not approval: the script only reports EO when the policy gates passed, the path is enabled, and confidence is at least 0.9. Say so, and leave the merge decision to the user.

Exit code 2 means the run failed (bad URL, gate error, PR moved mid-run). Report the error; don't retry with a different verdict path.

The policy and guidance are pinned to a `droctothorpe/skills` commit (`SKILL_COMMIT` in the script). Change that SHA only when the user asks.
