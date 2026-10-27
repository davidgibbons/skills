# skills

A Claude Code plugin marketplace.

| Plugin | What it adds |
|---|---|
| `documentation-writing` | The documentation-writing skill, plus a PreToolUse hook that blocks commit messages, PR bodies and docs that break its checkable rules |
| `eyeballs-optional` | A skill that asks a jev model whether a GitHub PR is eyeballs optional (EO) or eyeballs required (ER) |

## Install

```
/plugin marketplace add davidgibbons/skills
/plugin install documentation-writing@davidgibbons-skills
/plugin install eyeballs-optional@davidgibbons-skills
```

## Tests

```bash
python3 plugins/documentation-writing/hooks/doc-writing-context.test.py
cd plugins/eyeballs-optional/skills/eyeballs-optional/scripts && python3 -m unittest test_eyeballs_optional
```
