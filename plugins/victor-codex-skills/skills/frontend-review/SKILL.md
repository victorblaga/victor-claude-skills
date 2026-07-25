---
name: frontend-review
description: >
  Design-quality audit of already-implemented frontend code against composition / craft /
  content / structure rubrics, surfacing every place a default was reached for instead of a
  decision, then walking fixes with the user one at a time. Built for dashboards, admin
  panels and SaaS tools, not marketing sites. Trigger only when the user explicitly says
  "frontend-review" or invokes $frontend-review — not on generic UI feedback.
---

# Frontend Review

Audit implemented frontend code for craft, then walk the fixes with the user one at a time.

This is the review counterpart to a build skill. You point it at code that already runs. It does not propose a new design — it diagnoses the design that exists.

## Scope

**Use for:** dashboards, admin panels, SaaS apps, tools, settings pages, data interfaces, internal apps. Implemented code that the user has shipped or is about to ship.

**Do not use for:**
- Building new UI from scratch → use `frontend-design`
- General correctness/bug review → use `mega-review`
- Copy or content quality → use `long-form-article`
- Marketing sites and landing pages (different rubric — high-conviction visual identity over consistent system craft)

## Invocation

```
/frontend-review <path-or-route>
```

Examples:
- `/frontend-review src/pages/dashboard.tsx`
- `/frontend-review the settings page`
- `/frontend-review app/(workspace)/projects/*`
- `/frontend-review` (no arg → ask what to review)

If the user gives a running URL instead of files, ask them to point at the source files for the surface (the review reads code, not just rendered pixels).

## The Problem This Skill Solves

The interface compiles. The grid aligns. The colors don't clash. It works.

It also feels like every other dashboard the user has seen this week. That's the gap between **correct** and **crafted** — and it's almost always invisible to whoever shipped it, because they were optimising for "does this work?" not "would I put my name on this?"

The reason it's hard to see: intent lives in prose, but code generation pulls from patterns. Defaults are invisible because they don't announce themselves. They hide in the parts that feel structural — typography choices, surface elevations, token names, navigation scaffolding. Every default reached for is a decision that wasn't made.

This skill's job is to catch the defaults, name them out loud, and propose what a real choice would look like instead.

## Workflow

```
1. Scope         — confirm what code to review and the surface's intent
2. Read          — pull the relevant files into context
3. Four lenses   — composition, craft, content, structure
4. Diagnostics   — swap test, squint test, signature test, token test
5. Report        — findings ranked by severity, each with proposed fix
6. Triage        — walk the user through findings one at a time, accept / reject / defer
7. Apply         — implement accepted fixes, one commit per logical group
```

Steps 1–5 are fully read-only. No code changes happen until the user has accepted findings in step 6.

## Step 1 — Scope and Intent

Confirm three things before reading any code:

1. **What is the surface?** A component, a route, a page, a flow. Bound the review.
2. **Who uses it and what for?** Recover intent. If the user doesn't know, that itself is a finding — an interface built without intent will feel generic by construction.
3. **What feel was being aimed for?** Warm like a notebook? Cold like a terminal? Dense like a trading floor? Calm like a reader? If the user can't name it, mark intent as "undefined" and check the code against itself for internal consistency.

If intent is unrecoverable, the review shifts from "does the code match the intent?" to "does the code make any coherent choice at all?"

## Step 2 — Read

Read the files in scope. Also read enough of the surrounding system to know:
- Where design tokens / theme live (CSS variables, Tailwind config, theme provider, etc.)
- Which components are local to this surface vs shared from a library
- Whether there's a documented design system or style guide in the repo

Note (do not flag yet) every place where a pattern is repeated across files — those are the candidates for consistency findings.

## Step 3 — The Four Lenses

Walk the code through each lens. For each lens, the question is not "does it work?" but "where did a default win?"

### Lens 1 — Composition

Step back. Look at the surface as a whole.

- **Rhythm.** Does the layout breathe unevenly, with dense tooling areas giving way to open content? Or is every region the same density — same card size, same gaps, same proportions everywhere? Monotone layouts are the sound of no one deciding.
- **Proportions doing work.** A 280px sidebar next to full-width content says "navigation serves content." A 360px sidebar says "these are peers." If you can't articulate what your proportions are saying, they aren't saying anything.
- **Focal point.** Every screen has one thing the user came to do. That thing should dominate — through size, position, contrast, or surrounding space. If everything competes equally, nothing wins and the surface feels like a parking lot.
- **Navigation grounds the surface.** A page floating in space with no nav, breadcrumb, or location indicator is a component demo, not software.

### Lens 2 — Craft

Move close. Pixel-close.

- **Spacing grid.** Every value should trace to a base unit (4px or 8px). Find the offenders — 17px paddings, 13px gaps, ad-hoc margins. Symmetrical padding unless the asymmetry is doing work.
- **Surface elevation.** Surfaces should stack with whisper-quiet shifts in lightness, not dramatic jumps. If you can name two surfaces that should feel layered but don't, that's a finding. If you can name two that feel jarringly different, that's also a finding.
- **Borders.** Should disappear when you're not looking, findable when you need structure. Solid hex borders (e.g. `1px solid #e5e5e5`) look harsh next to low-opacity rgba borders. Build a progression — default / subtle / strong / focus — not binary.
- **Typography hierarchy.** Distinguishable at a glance via weight + size + tracking, not size alone. If headline → body → label only differs in font-size, the hierarchy is too weak. Look for four levels of text colour (primary / secondary / tertiary / muted) — flatter hierarchies signal a thin system.
- **Depth strategy.** One approach committed to: borders-only, subtle single shadow, layered shadow, or surface-color shifts. Mixed approaches (some cards with shadows, others with borders only) read as accidental.
- **Interactive states.** Every clickable region should respond to hover, focus, and active. Missing states make the interface feel like a photograph of software instead of software. Data needs loading / empty / error states too.
- **Border radius scale.** Inputs and buttons one size, cards another, modals another. Random radius mixes feel as bad as random spacing.
- **Iconography.** Decorative icons (icons that add no information) are clutter. Standalone icons should sit on a subtle background container, not float bare.
- **Animation.** Micro-interactions ~150ms with ease-out. Spring/bounce in a serious tool feels wrong. Missing transitions on hover/focus feels broken.

### Lens 3 — Content

Read every visible string as a user would. Not for typos — for truth.

- **Coherence.** Does the surface tell one story? Could a real person at a real company be looking at exactly this data right now? Or does the page title belong to one product, the body to another, and the sidebar to a third? Content incoherence breaks the illusion faster than any visual flaw.
- **Lorem ipsum, "Item 1 / Item 2", "User Name", or AI-flavoured copy** ("Unlock the power of...", "Seamlessly...") in a finished surface — all findings.
- **Number formatting.** Currency, dates, large numbers, percentages — consistent locale and precision. Mixed formats signal no system.
- **Labels.** Verb-first action labels ("Approve payment") read sharper than noun labels ("Payment approval"). Sentence case vs title case applied consistently.

### Lens 4 — Structure

Open the CSS / styling code. Find the lies — the places that look right but are held together with tape.

- **Negative margins** undoing a parent's padding.
- **`calc()`** values that exist as workarounds rather than expressions of intent.
- **Absolute positioning** to escape layout flow when a layout primitive would do.
- **Magic numbers** with no token reference (`marginTop: 17`).
- **`!important`** in component-level styles.
- **Inline styles** when the system has tokens for the same value.
- **Duplicated patterns** — three slightly different "Card" implementations across the file. Each shortcut is a place where a clean primitive exists and wasn't reached for.
- **Token bypassing** — hex colours hard-coded when a CSS variable / theme token exists.

The correct answer is almost always simpler than the hack.

## Step 4 — Diagnostic Checks

Run all four. They are quick and they catch what the lenses miss.

- **Swap test.** Mentally swap the typeface for the default sans-serif. Mentally swap the layout for a standard dashboard template. Swap the colour palette for the default Tailwind grays. Where would no one notice? Those are the places that defaulted.
- **Squint test.** Blur your eyes (or downsample the rendered output in your head). Can you still perceive hierarchy — what's above what, what's primary vs supporting? Is anything jumping out harshly? Craft whispers.
- **Signature test.** Can you point to five specific elements where this product's signature appears? Not "the overall feel" — actual components. A signature you can't locate doesn't exist.
- **Token test.** Read the CSS variable names / theme token names out loud. Do they sound like they belong to this product's world (`--ink`, `--parchment`, `--ledger`), or could they belong to any project (`--gray-700`, `--surface-2`, `--primary`)? Token names are design decisions.

## Step 5 — Report

Produce a findings report, ranked by severity:

```
## Frontend Review — <surface>

**Intent recovered:** <one sentence — or "undefined">

### Critical  (breaks craft — fix before shipping)
1. <finding> — <location> — <proposed fix>
2. ...

### Major    (defaults visible — fix this pass)
1. ...

### Minor    (polish — fix if time)
1. ...

### Watchlist (pattern drift — track over time)
1. ...

## Diagnostic results
- Swap test:      <where defaults would survive a swap>
- Squint test:    <what jumped out, what disappeared>
- Signature test: <signature elements found, or "none">
- Token test:     <generic vs world-grounded>

## Quick wins
<3–5 changes that punch above their weight>
```

Severity rubric:
- **Critical** — a default in a load-bearing decision (typography hierarchy, surface system, depth strategy, primary nav). Visible at first glance. Cannot be "polished" later — needs to be redecided.
- **Major** — a default in a secondary decision (border progression, state coverage, icon usage, spacing consistency). Visible on inspection. Fix this pass.
- **Minor** — a polish gap (a 17px padding, a missing hover state on one button, inconsistent radius on one component). Fix if cheap.
- **Watchlist** — pattern drift across files (three Card variants, two different button heights). Not urgent per-surface, but compounds. Track and bring up if pattern continues.

Each finding states:
- What the default is
- Where it appears (file + approximate location)
- What a non-default choice would look like — at least one concrete alternative, not just "be more intentional"

## Step 6 — Triage

Do not start applying fixes. Walk the user through findings, one at a time, in severity order:

```
Finding 1/12 — Critical
<finding statement>
<location>
<proposed fix>

Accept / reject / defer? (notes optional)
```

For each:
- **Accept** — add to the implementation queue
- **Reject** — note the reason if useful (e.g. "intentional — this surface wants to feel templated for now")
- **Defer** — move to a follow-up list

Stop and re-check intent if the user rejects several findings in a row in the same area — the rubric may be misaligned with what they're aiming for.

## Step 7 — Apply

Implement accepted fixes. Group by logical area (one commit per area, not per finding) unless the user wants one commit per finding. After each group:

- Run typecheck / lint / build if the project has them wired.
- Run the affected component / route locally if practical, and confirm the change.
- For purely visual changes you cannot verify without browsing, say so explicitly — do not claim "verified" without evidence.

Then return to triage for the next finding.

## What Not To Do

- Do not redesign. This is a review, not a rebuild. Findings should be targeted fixes, not "rethink the whole surface."
- Do not narrate the four lenses to the user as you go. Do the work silently and produce the report.
- Do not invent intent. If the user can't tell you what feel was aimed for, mark intent as undefined and judge the code against itself.
- Do not flag taste preferences as findings. Flag defaults, inconsistencies, and craft gaps — not "I would have used a different accent colour."
- Do not soften findings to be polite. Direct language saves a round trip. "This is a default" reads better than "you might consider whether…"
- Do not apply fixes before the user has accepted them in triage.

## Deep Dives

- `references/principles.md` — full craft rubric (tokens, surfaces, borders, spacing, depth, typography, states)
- `references/rubric.md` — the four-lens checklist in expanded form, usable as a worksheet
- `references/defaults.md` — the "where defaults hide" diagnostic framework, with examples of what defaulting looks like in each load-bearing decision
