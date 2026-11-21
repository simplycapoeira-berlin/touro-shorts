# Decisions

One file per decision: why the project looks and works the way it does. Several people change
this repo through Claude, so the history lives in separate files that never conflict.
[STYLE.md](../STYLE.md) always holds the *current* rules.

## Adding a decision

Create `decisions/<yyyy-mm-dd>-<short-slug>.md` in the same pull request as the change:

```markdown
# <short title>

- **Date:** <yyyy-mm-dd>
- **Requested by:** <GitHub handle, or "project owner">
- **Area:** style | video-type | pipeline | archive | process

## Feedback

<what was asked, in the requester's words where possible>

## Decision

<what changed and why: values, edits affected, trade-offs>
```

## Rules

- **Never rewrite an old decision.** To change course, add a new file that says which decision
  it replaces. The old file stays as history.
- **One decision per file.** If a request changes two things, write two files.
- **Keep the rules in sync.** If a decision changes a rule, update the matching STYLE.md
  section in the same pull request. `tests/test_decisions.py` checks the format.
