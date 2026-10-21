## Summary
<!-- 1 to 3 sentences: what this PR changes and why. Lead with the user-visible outcome. -->

## Type of change
<!-- Keep the ones that apply (Conventional Commits types). -->
- [ ] `feat`: new feature or content
- [ ] `fix`: bug fix
- [ ] `refactor`: code change with no behavior change
- [ ] `docs`: documentation only
- [ ] `chore` / `ci` / `build`: tooling, CI, dependencies or config
- [ ] Breaking change (URL, config or contract that something else depends on)

## Changes
<!-- Bullet list of what changed, grouped by area. Facts, not narrative. -->
-

## Motivation and context
<!-- Why is this needed? Link the issue or decision record: Closes #123, docs/adr/000X. -->

## How has this been tested?
<!-- Commands actually run and their result. Anything not tested goes under "Not tested". -->
| Check | Result |
|---|---|
| `uv run ruff check` | |
| `uv run ruff format --check` | |
| `uv run pytest` | |

**Not tested:**

## Verification (QA / staging)
<!-- What was validated on a running build: local preview, Workers Builds preview URL or production after deploy.
     Pages, languages (EN/PT), themes (light/dark), viewports (desktop/mobile), browsers. -->

## Screenshots
<!-- Required for visual changes. Before / after, desktop and mobile. -->

## Risk and rollback
- **Risk:** low / medium / high, and why
- **Rollback:** revert this PR; production redeploys automatically from `main`

## Checklist
- [ ] PT and EN updated together (site texts)
- [ ] No raw FIPE data (per-model prices) committed; only aggregates (docs/adr/0001)
- [ ] No secrets, personal data (phone, address, personal email) or image metadata
- [ ] Accessibility: `alt` text, contrast in both themes, keyboard focus
- [ ] Site: CSP still holds (`npm run build && npm run preview` in `web/`, no console violations)
- [ ] `CLAUDE.md` / `docs/adr/` updated if a convention or decision changed
