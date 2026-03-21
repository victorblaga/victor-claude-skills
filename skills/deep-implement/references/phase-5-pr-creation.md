# Phase 5: PR Creation

Final validation passed. Time to ship.

## Standard Mode

1. **Clean up working docs**: Remove from git but keep local copies
   - `git rm --cached` all files in `docs/plans/<feature-name>/` (proposal, review findings, plan, validation, final-validation docs)
   - Commit with a message like "Remove working docs before PR"
   - The files remain on disk for local reference but won't appear in the PR diff
2. **Rebase onto latest base branch**: Pull the latest base branch and rebase. If conflicts arise, resolve straightforward ones yourself and escalate complex ones to the user.
3. **Push the branch** to origin
4. **Create the PR** using `gh pr create`:
   - Title: derived from the feature name / proposal title
   - Body: summary of what was implemented and why (drawn from the proposal). If Phase 4 flagged any consciously descoped items, mention them in the PR description. If Phase 4c updated project docs or memories, include a "Documentation updates" section listing which files were changed and why.
   - Target: the base branch (dev/main)
5. **Wait for CI** — check the PR's CI status
6. **If CI fails**: Read the CI output, diagnose, fix, push. Max 3 attempts — after that, present the full diagnostic to the user and let them decide.
7. Tell the user the PR is ready and provide the URL

## Review-Driven Mode

1. **Clean up working docs**: Same as standard — `git rm --cached` the plan directory, commit.
2. **Check for existing PR**: Run `gh pr view` to detect if a PR already exists on this branch.
3. **If PR exists**:
   - Push the fix commits to origin
   - Optionally update the PR description to note which mega-review findings were addressed (append a section, don't overwrite the original description)
   - Wait for CI, fix cycle if needed (same as standard)
   - Tell the user the fixes have been pushed to the existing PR and provide the URL
4. **If no PR exists**: Follow the standard mode steps 2-7 above.

## Common

Do **not** merge the PR — that's always the user's action via the GitHub web UI.
