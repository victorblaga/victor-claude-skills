# Craft Principles — The Rubric

The quality floor a frontend review checks against. These apply regardless of product type, visual direction, or stack.

---

## Surface & Token Architecture

Professional interfaces don't pick colours randomly — they build systems. The difference between "looks okay" and "feels like a real product" is whether every visible value traces back to a named primitive.

### The Primitive Foundation

Every colour should trace to a small set:

- **Foreground** — text colours (primary, secondary, tertiary, muted)
- **Background** — surface colours (base, elevated, overlay)
- **Border** — edge colours (default, subtle, strong, focus)
- **Brand** — the primary accent
- **Semantic** — destructive, warning, success, info

No raw hex values in component code. If a colour can't be named in token terms, the system is incomplete.

### Surface Elevation

Surfaces stack: a dropdown sits above a card which sits above the page. Build a numbered scale:

```
Level 0 — base canvas
Level 1 — cards, panels (same visual plane as base)
Level 2 — dropdowns, popovers (floating above)
Level 3 — nested overlays, stacked menus
Level 4 — highest elevation (rare)
```

In dark mode, higher elevation = slightly lighter. In light mode, higher elevation = slightly lighter or uses shadow.

**The subtlety principle.** Each elevation jump should be a few percentage points of lightness — not a dramatic shift. Surface-100 might be 7% lighter than base, surface-200 might be 9%, surface-300 might be 12%. You can barely see the difference in isolation. But when surfaces stack, the hierarchy emerges.

**The squint test for surfaces.** Blur your eyes at the interface. You should still perceive what's above what. But no surface should jump out. If a card looks like it's sitting on top of a different-coloured rug instead of the same surface a little lighter, the jump is too dramatic.

**Common defaults that fail this:**
- Going from dark to almost-white between elevations
- Using different hues for different surfaces (gray card on blue base)
- Surfaces all on the same level so layering disappears
- Sidebars with a different base colour than the canvas — fragments visual space into "sidebar world" and "content world." Use the same base + a subtle border.

### Borders

Borders should disappear when you're not looking, and be findable when you need structure. Low-opacity rgba (0.05–0.12 alpha for dark mode, slightly higher for light) blends with the background. Solid hex (`1px solid #e5e5e5`) looks harsh next to rgba.

Build a progression — not binary:

- **Default** — standard regions
- **Subtle / muted** — softer separation
- **Strong** — emphasis, hover states
- **Stronger** — focus rings, maximum emphasis

Match border intensity to the importance of the boundary. Every divider at the same weight is the same as every divider at no weight.

### Text Hierarchy

Don't just have "text" and "gray text." Build four levels:

- **Primary** — default body text, highest contrast
- **Secondary** — supporting text, slightly muted
- **Tertiary** — metadata, timestamps
- **Muted** — disabled, placeholder, lowest contrast

If only two levels appear in the code, the hierarchy is too flat — secondary information is competing with primary.

### Dedicated Control Tokens

Form controls (inputs, checkboxes, selects) have specific needs distinct from layout surfaces:

- **Control background** — often slightly darker than the surrounding surface; signals "inset"
- **Control border** — needs to read as interactive
- **Control focus** — clear, accessible focus indication

Don't reuse surface tokens for controls. The needs differ.

### Context-Aware Bases

Different areas of an app may need different base surfaces — marketing pages might use richer backgrounds, the dashboard a neutral working canvas, the sidebar the same canvas as content. The hierarchy works the same way; it just starts from a different base.

### Alternative Backgrounds for Depth

Beyond shadows and borders, contrasting backgrounds create recession. An "alternative" or "inset" background reads as recessed. Useful for empty states, code blocks, inset panels, and visual grouping without borders.

---

## Spacing

Pick a base unit (4px or 8px are common) and use multiples throughout. The specific number matters less than consistency — every spacing value should be explainable as "X times the base unit."

Build a scale for different contexts:

- **Micro** — icon gaps, tight element pairs (4–8px)
- **Component** — within buttons, inputs, cards (12–16px)
- **Section** — between related groups (24–32px)
- **Major** — between distinct sections (48–64px)

Random values like `padding: 17px` are the clearest sign of no system.

### Symmetrical Padding

TLBR matches unless the asymmetry is doing work. Asymmetric horizontal padding on a pill button (`padding: 6px 12px`) is fine because horizontal text needs more breathing room than vertical. Asymmetric padding on a card with no reason is a default.

```css
/* Good */
padding: 16px;
padding: 12px 16px;   /* asymmetric for a deliberate reason */

/* Bad */
padding: 24px 16px 12px 16px;
```

---

## Border Radius

Sharper corners feel technical. Rounder corners feel friendly. Pick a scale that fits the product's personality and use it consistently.

Typical scale:

- **Small** — inputs, buttons, tags (4–6px)
- **Medium** — cards, panels (8–12px)
- **Large** — modals, sheets (16–24px)
- **Full** — pills, avatars

Mixing sharp and soft randomly is as jarring as inconsistent spacing.

---

## Depth & Elevation Strategy

Match the depth approach to the design direction. Choose **one** and commit:

- **Borders-only (flat)** — clean, technical, dense. Linear and Raycast use almost no shadows. Best for utility-focused tools.
- **Subtle single shadows** — soft lift without complexity. A simple `0 1px 3px rgba(0,0,0,0.08)`. Best for approachable products.
- **Layered shadows** — rich, dimensional. Multiple shadow layers create realistic depth. Stripe and Mercury use this. Best for cards that need to feel like physical objects.
- **Surface colour shifts** — background tints establish hierarchy without any shadow.

```css
/* Borders-only */
--border:        rgba(0, 0, 0, 0.08);
--border-subtle: rgba(0, 0, 0, 0.05);
border: 0.5px solid var(--border);

/* Subtle shadow */
--shadow: 0 1px 3px rgba(0, 0, 0, 0.08);

/* Layered shadow */
--shadow-layered:
  0 0 0 0.5px rgba(0, 0, 0, 0.05),
  0 1px 2px   rgba(0, 0, 0, 0.04),
  0 2px 4px   rgba(0, 0, 0, 0.03),
  0 4px 8px   rgba(0, 0, 0, 0.02);
```

Mixed strategies (some cards with shadows, others with borders only, others with surface shifts) read as accidental. Pick one and apply it everywhere.

---

## Typography

Build distinct levels distinguishable at a glance through size + weight + tracking — not size alone.

- **Headlines** — heavier weight, tighter letter-spacing for presence
- **Body** — comfortable weight for readability
- **Labels / UI** — medium weight, works at smaller sizes
- **Data** — monospace with `tabular-nums` for columnar alignment

If you squint and can't tell headline from body, the hierarchy is too weak.

### Monospace for Data

Numbers, IDs, codes, timestamps belong in monospace. Use `tabular-nums` so columns align. Mono signals "this is data."

---

## Card Layouts

A metric card doesn't have to look like a plan card doesn't have to look like a settings card. Design each card's internal structure for its specific content — but keep the surface treatment consistent: same border weight, shadow depth, corner radius, padding scale, typography.

The structure varies. The treatment doesn't.

---

## Controls

Never use native form elements for styled UI. `<select>`, `<input type="date">`, and similar render OS-native dropdowns that cannot be styled — they will break the interface's surface system. Build custom components:

- Custom select: trigger button + positioned dropdown menu
- Custom date picker: input + calendar popover
- Custom checkbox / radio: styled div with state management

Custom select triggers use `display: inline-flex` with `white-space: nowrap` so the chevron and label stay on the same row.

---

## Iconography

Icons clarify, not decorate. If removing an icon loses no meaning, remove it. Choose one icon set and stick with it across the product.

Standalone icons get presence through a subtle background container. Icons inline with text align optically, not mathematically — visual centre, not bounding-box centre.

---

## Animation

Keep it fast and functional:

- **Micro-interactions** (hover, focus) — ~150ms
- **Larger transitions** (modals, panels) — 200–250ms
- **Easing** — smooth deceleration (`ease-out`, custom cubic-bezier with deceleration profile)

Avoid spring / bounce in professional tools — they read as playful, not serious.

---

## States

Every interactive element needs: **default, hover, active, focus, disabled**. Data displays need: **loading, empty, error**. Missing states make an interface feel like a photograph of software instead of software.

The most commonly missed:
- Focus styles on custom controls (especially when `outline: none` is set without a replacement)
- Empty states with no illustration or guidance
- Loading states that fall back to "the page is blank for a second"
- Error states that surface a raw stack trace or a generic "something went wrong"

---

## Contrast Hierarchy

Build a four-level system for text contrast: foreground (primary) → secondary → muted → faint. Apply consistently. Two-level contrast (text + gray) is a thin system tell.

---

## Colour Carries Meaning

Gray builds structure. Colour communicates — status, action, emphasis, identity.

- **Unmotivated colour is noise.** Decorative gradients, accent colours on inactive UI, colour for the sake of "looking less plain" — all clutter.
- **Reinforces the product's world.** A trading terminal's red means "down." A bakery tool's red probably doesn't.
- **One accent, used with intention,** beats five accents used without thought.

---

## Navigation Context

Screens need grounding. A data table floating in space feels like a component demo, not a product. Surfaces should usually include:

- **Navigation** — sidebar or top nav showing where the user is in the app
- **Location indicator** — breadcrumbs, page title, active nav state
- **User context** — who's logged in, what workspace / org

Sidebar surface tip: the same background as the main content with a subtle border separation reads more cohesively than a different sidebar colour.

---

## Dark Mode

Dark interfaces have different needs:

- **Borders over shadows.** Shadows are less visible on dark backgrounds. Lean on borders for definition.
- **Adjust semantic colours.** Status colours (success, warning, error) usually need to be slightly desaturated to sit well on dark surfaces.
- **Same structure, inverted values.** The hierarchy system still applies — just inverted.

---

## Common Anti-Patterns

These are the highest-frequency defaults to flag in a review:

- Harsh borders (solid hex, 1px+, default-coloured)
- Dramatic surface jumps between elevations
- Inconsistent spacing (`17px`, `23px`, `padding: 24px 16px 12px 16px`)
- Mixed depth strategies (some cards shadowed, others bordered)
- Missing interaction states (no hover, no focus, no disabled)
- Dramatic drop shadows on cards in a flat interface
- Large radius on small elements (12px radius on a 24px button)
- Pure white cards on coloured backgrounds with no token connection
- Thick decorative borders
- Gradients used purely for decoration
- Multiple accent colours diluting focus
- Different hues for different surface levels
- Hard-coded hex values where tokens exist
- Native `<select>` / `<input type="date">` inside an otherwise-styled surface
- Lorem ipsum / placeholder strings in shipped code
- `outline: none` with no replacement focus indicator
