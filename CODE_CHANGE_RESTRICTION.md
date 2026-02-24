# Code Change Restriction

All code changes in this project must follow these rules to keep changes small, traceable, and reviewable via Git.

---

## Principle

**Small, traceable changes.** Each logical change = one commit. Every commit should be understandable in isolation and safe to revert.

---

## Commit Rules

- **One concern per commit**: Fix one bug, add one feature, or refactor one module. Do not mix unrelated changes.
- **Descriptive messages**: Use clear, imperative commit messages (e.g. `Add leasingmarkt adapter for /deals page`, not `fix` or `wip`).
- **No placeholder messages**: Avoid `fix`, `wip`, `updates`, `changes` without context.
- **Submit to Git**: Every change must be committed and pushed. No long-lived uncommitted work.

---

## Branching

- **main**: Stable, deployable state.
- **Feature branches**: Create a branch for each feature or fix (e.g. `feature/leasingmarkt-adapter`, `fix/excel-sheet-naming`).
- **Merge**: Prefer pull requests or squash merge. Ensure `main` stays clean.

---

## Size Limits

- **Prefer changes < 200 lines** per commit. Split large features into logical steps.
- **Large refactors**: Break into smaller commits (e.g. rename, then move, then update callers).
- **New features**: Implement in stages; each stage should be a separate commit.

---

## Review

- **Self-review**: Run `git diff` before committing. Ensure the diff matches your intent.
- **Tests**: Ensure existing tests pass before committing. Add tests for new behavior.
- **Linting**: Fix any lint errors before commit.

---

## Scope

Applies to all code under `src/` and `tests/`. Config and docs may follow looser rules but should still be traceable.
