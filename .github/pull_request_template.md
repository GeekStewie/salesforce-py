<!--
Thanks for contributing to salesforce-py! A clear PR description speeds up review.
Keep the title short (<70 chars) and conventional: "fix(connect): ...", "feat(data360): ...",
"docs: ...", "chore(ci): ...", etc.
-->

## Summary

<!-- One to three sentences describing *what* this PR changes and *why*. -->

## Type of change

<!-- Tick all that apply. -->

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing behaviour to change)
- [ ] Refactor / internal cleanup (no user-facing behaviour change)
- [ ] Documentation
- [ ] Build / CI / tooling
- [ ] Dependency bump

## Area(s) affected

<!-- Tick all that apply. -->

- [ ] `salesforce_py.sf` (CLI wrapper)
- [ ] `salesforce_py.connect` (Connect REST API)
- [ ] `salesforce_py.data360` (Data 360 / CDP)
- [ ] `salesforce_py.models` (Einstein Models)
- [ ] `salesforce_py.utils`
- [ ] Shared (`_retry`, `_defaults`, exceptions)
- [ ] Tests
- [ ] Docs / README
- [ ] CI / workflows / tooling

## Motivation & context

<!--
Why is this change needed? Link the issue it closes ("Closes #123") or the Salesforce
documentation / API change it tracks. If this is a refactor, explain what pain it removes.
-->

Closes #

## Changes

<!-- Bulleted, reviewer-oriented list of what changed. Focus on *intent*, not a git-log dump. -->

-

## Breaking changes

<!--
If you ticked "Breaking change" above, describe:
  1. What breaks
  2. The migration path for existing users
  3. Whether this warrants a major version bump
Delete this section if not applicable.
-->

## Test plan

<!--
How did you verify the change? Tick the boxes that apply and add any extra detail.
-->

- [ ] Added or updated unit tests covering the change
- [ ] `uv run pytest` passes locally
- [ ] `uv run ruff check src/ tests/` passes
- [ ] `uv run ruff format --check src/ tests/` passes
- [ ] `uv run ty check src/` passes
- [ ] `uv run bandit -r src/ -c pyproject.toml` passes
- [ ] Exercised against a real Salesforce org (describe org type + scenario below)

<!-- Optional: paste commands run, curl examples, screenshots of output, etc. -->

## Documentation

- [ ] Updated `README.md` / sub-package `README.md` where relevant
- [ ] Updated docstrings on new / changed public APIs
- [ ] Updated `CLAUDE.md` architecture notes if the change affects contributor workflow
- [ ] No documentation change needed

## Checklist

- [ ] PR title follows the conventional-commit style (e.g. `fix(connect): ...`)
- [ ] Commits are logically grouped and have descriptive messages
- [ ] No secrets, tokens, org URLs, or customer data appear in the diff
- [ ] Public API changes are additive, or the breaking-changes section above is filled in
- [ ] I have read and followed the contributing guidance in `CLAUDE.md`
