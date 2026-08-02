---
name: simplify
description: >
  Simplify code in the requested scope without changing behavior. Trigger only when the
  user invokes /simplify or explicitly says "run simplify". Do not trigger automatically
  after routine code changes, during review, while writing comments, or when the user is
  discussing or configuring the skill.
---

# Simplify

Review changes in the scope the user specifies. If no scope is given, review the current
branch against its merge base and include uncommitted changes. Only touch code in that scope.
Preserve behavior, public APIs, performance characteristics, and externally visible text. Run
the relevant existing checks after making changes.

Apply a criterion only when the result is plainly simpler and still fits the project's
conventions. Do not chase fewer lines, force a preferred structure, or replace clear code with
clever code.

## Words and names

Names and comments are prose. Make them short, concrete, and consistent.

1. **One word per concept, one concept per word.** Keep a stable vocabulary. If `sync` means
   "pull remote changes," do not also use it for "flush edits to disk."
2. **Cut context the surrounding code already carries.** In a module named `workspaceWatcher`,
   `watchWorkspace` is clearer than `startNativeWorkspaceWatcher`.
3. **Use the shortest name that stays unambiguous in its scope.** Prefer a precise technical or
   domain term when a shorter everyday word would lose meaning. Follow established codebase
   vocabulary before inventing a synonym.

## Comments

State the constraint the code cannot show: why the non-obvious behavior exists.

- Add a comment when a necessary constraint or surprising choice is not evident from the code.
- Add a doc comment when the project requires one or a public contract or side effect needs it.
- Delete comments that narrate the conversation or change history.
- Delete comments that merely restate self-evident code.

## Code structure

1. **Lead with the significant code.** Put exported or primary functions before helpers when
   that matches the language and project conventions.
2. **Separate concepts with real boundaries.** Split a large file only when each resulting
   module owns a clear concept and the split lowers the reader's mental load.
3. **Combine duplicate concepts.** Merge functions, types, or constants that express the same
   invariant. Do not collapse concepts that merely look similar.
4. **Reuse existing code.** Check for a suitable project utility before writing another one. Do
   not create a generic abstraction for a single caller.
5. **Derive instead of synchronize.** Do not pass or store a value that is cheaply and reliably
   computed from values already in scope. Keep it only when cost, consistency, or time-sensitive
   behavior requires stored state.

## Overfitting

Code must stand on its own for a reader who did not see the conversation or pull request.

- Rewrite names and comments that depend on session history to make sense.
- Remove backwards compatibility for signatures, aliases, or data shapes that existed only on
  the current unshipped branch. Update every caller and delete the replaced path.
