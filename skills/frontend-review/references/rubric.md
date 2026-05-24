# Four-Lens Review Rubric

Use this as a worksheet during step 3 of the review. Walk every lens. Note findings as you go — don't filter on the first pass.

---

## Lens 1 — Composition

Step back. Look at the surface as a whole.

- [ ] **Rhythm.** Does the layout breathe unevenly? Dense areas balanced against open ones? Or is everything the same density throughout?
- [ ] **Proportions.** Can each major proportion be explained? (Sidebar width, content max-width, card aspect ratios.) Or are they arbitrary?
- [ ] **Focal point.** Is there one clear primary action / primary information per screen? Does it dominate through size, position, contrast, or surrounding space?
- [ ] **Grounding.** Is there navigation, breadcrumb, location indicator, or user context? Or is the surface floating in space?
- [ ] **Visual centre.** When you mentally place a dot at the visual centre of the screen, is something meaningful there?

**Finding triggers:**
- Same-size cards in a uniform grid with no rhythm
- Sidebar proportions that feel arbitrary (270px? 300px? 320px — why?)
- Three primary actions of equal visual weight
- Nav-less screens
- Empty visual centres on screens with a clear primary task

---

## Lens 2 — Craft

Move close. Pixel-close.

### Spacing
- [ ] Every spacing value traces to the base unit
- [ ] No magic numbers (`17px`, `13px`, `padding: 24px 16px 12px 16px`)
- [ ] Symmetrical padding unless asymmetry is intentional

### Surfaces
- [ ] Surfaces use the token system, not hard-coded values
- [ ] Elevation differences are whisper-quiet (a few % lightness)
- [ ] No dramatic surface jumps
- [ ] Same hue across elevations (no blue card on gray base)
- [ ] Sidebar shares canvas background with subtle border, not a different colour

### Borders
- [ ] Borders use rgba / low-opacity colour, not solid hex
- [ ] A progression exists (default / subtle / strong / focus)
- [ ] No single border is the first thing you notice

### Typography
- [ ] Hierarchy works through weight + size + tracking, not size alone
- [ ] At least three text contrast levels appear (primary / secondary / tertiary)
- [ ] Headlines have tighter tracking; body is comfortable; labels work at small sizes
- [ ] Data uses monospace + `tabular-nums`

### Depth strategy
- [ ] One depth approach (borders / single shadow / layered shadow / surface shifts) applied consistently
- [ ] No accidental mixing across cards

### States
- [ ] Hover state on every interactive element
- [ ] Focus state on every interactive element (and `outline: none` has a replacement)
- [ ] Active / pressed state where it matters
- [ ] Disabled state defined
- [ ] Loading state for async data
- [ ] Empty state with guidance, not just "No items"
- [ ] Error state with useful information

### Radius
- [ ] A scale exists (small inputs, medium cards, large modals)
- [ ] No random radius mixing

### Iconography
- [ ] One icon set used throughout
- [ ] Decorative icons removed (those that add no meaning)
- [ ] Standalone icons sit in a subtle container

### Animation
- [ ] Micro-interactions feel instant (~150ms)
- [ ] Easing is deceleration-based
- [ ] No spring / bounce in a serious tool

**Finding triggers:**
- Hex colours hard-coded in component files
- Tailwind utility classes overriding theme values
- Solid 1px gray borders everywhere
- `outline: none` with no focus replacement
- Native `<select>` or `<input type="date">` in a styled surface
- Three different button heights across the file
- One card with a shadow, another with a border, a third with neither

---

## Lens 3 — Content

Read every visible string as a user would.

- [ ] Page title, body, and sidebar all describe the same product / domain
- [ ] No lorem ipsum or placeholder strings
- [ ] No AI-flavoured copy ("Unlock the power of…", "Seamlessly…", "Effortlessly…")
- [ ] Number formatting is consistent (currency, dates, large numbers, percentages)
- [ ] Date formats are consistent across the surface
- [ ] Sentence vs title case is applied consistently
- [ ] Action labels are verb-first ("Approve payment" vs "Payment approval")
- [ ] Plurals are handled (no "1 items")
- [ ] Empty states say something useful, not just "No data"
- [ ] Error messages help the user act, not just acknowledge the error

**Finding triggers:**
- Sample data inside production code (`name: "John Doe"`)
- Mixed `Mar 5, 2026` and `2026-03-05` on the same surface
- A dashboard about widgets with copy about "your tasks"
- Buttons named after nouns instead of verbs

---

## Lens 4 — Structure

Open the styling code. Find the lies.

- [ ] No negative margins undoing parent padding
- [ ] No `calc()` workarounds (calc is fine when it's an expression of intent, not when it's hiding a problem)
- [ ] No `position: absolute` to escape layout flow where flex / grid would work
- [ ] No magic spacing numbers in style files
- [ ] No `!important` in component-level styles
- [ ] No inline styles for values that have tokens
- [ ] Hex / rgb colours all map to tokens
- [ ] No duplicated "almost the same" components — one Card primitive, not three
- [ ] Layout primitives composed cleanly (Stack, Inline, Grid — not nested divs with margins)
- [ ] No commented-out CSS

**Finding triggers:**
- `margin-top: -16px` undoing a parent's padding
- `calc(100% - 47px)` with no comment
- `position: absolute; top: 12px; left: 9px;` to nudge an icon
- `padding: 17px`
- `!important` on a colour
- Three `Card.tsx`-like components with 80% overlap
- Inline `style={{ color: '#3b82f6' }}` when the theme has a brand token
