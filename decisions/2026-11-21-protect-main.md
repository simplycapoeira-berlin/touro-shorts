# protect main

- **Date:** 2026-11-21
- **Requested by:** project owner
- **Area:** process

## Feedback

Make the branch + pull request workflow binding, not just written down: nobody (and no Claude
session) should be able to push to `main` directly or merge with failing tests.

## Decision

GitHub branch protection on `main`:

- every change arrives through a pull request (0 approvals required, so a single maintainer
  can still merge their own reviewed work);
- the `pytest` CI check must pass, and the branch must be up to date with `main` before merging
  (the second of two parallel pull requests re-runs the tests against the first);
- open review conversations must be resolved before merging;
- the rules apply to admins too: Claude sessions run under someone's account, often an admin;
- no force pushes and no deleting `main`.

Raising the required approvals later is a one-line settings change. Record it as a new decision.
