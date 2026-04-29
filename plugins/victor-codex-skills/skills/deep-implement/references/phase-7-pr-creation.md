# Phase 7: PR Creation

Final validation and documentation reconciliation passed. Time to ship.

## Standard Mode

1. **Decide what to do with working docs**:
   - If repository norms or user preference say workflow docs should stay local-only, run `git rm --cached` on files in `.docs/plans/<feature-name>/`, commit the removal, and keep the files on disk
   - If the repo treats these docs as useful review artifacts, keep them in the branch
2. **Rebase onto latest base branch**: Pull the latest base branch and rebase. If conflicts arise, resolve straightforward ones yourself and escalate complex ones to the user.
3. **Push the branch** to origin
4. **Create the PR** using `gh pr create`:
   - Title: derived from the feature name / proposal title
   - Body: summary of what was implemented and why (drawn from the proposal). If Phase 5 flagged any consciously descoped items, mention them in the PR description. If Phase 6 updated project docs or knowledge artifacts, include a "Documentation updates" section listing which files were changed and why, using `.docs/plans/<feature-name>/doc-reconciliation.md` as the source of truth.
   - Target: the base branch (dev/main)
5. **Wait for CI** — check the PR's CI status
6. **If CI fails**: Read the CI output, diagnose, fix, push. Max 3 attempts — after that, present the full diagnostic to the user and let them decide.
7. Tell the user the PR is ready and provide the URL
8. Update `status.md` to `Current phase: 7`, `Current step: complete`, and `Next action: Monitor PR / respond to review or CI feedback`.

## Review-Driven Mode

1. **Handle working docs the same way as standard mode**: keep them if repo norms support that, or `git rm --cached` them if they should remain local-only.
2. **Check for existing PR**: Run `gh pr view` to detect if a PR already exists on this branch.
3. **If PR exists**:
   - Push the fix commits to origin
   - Optionally update the PR description to note which mega-review findings were addressed (append a section, don't overwrite the original description)
   - If Phase 6 ran, use `doc-reconciliation.md` to append the documentation updates section consistently
   - Wait for CI, fix cycle if needed (same as standard)
   - Tell the user the fixes have been pushed to the existing PR and provide the URL
4. **If no PR exists**: Follow the standard mode steps 2-7 above.

## Common

Do **not** merge the PR — that's always the user's action via the GitHub web UI.
