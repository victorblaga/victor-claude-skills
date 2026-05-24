# Where Defaults Hide

Defaults don't announce themselves. They disguise themselves as infrastructure — parts of the interface that feel like they just need to work, not be designed.

A frontend review's job is to drag those parts back into the design conversation. This file is the diagnostic framework — the load-bearing decisions where defaults most commonly win, and what defaulting looks like in each.

---

## Typography Feels Like A Container

Pick something readable, move on. That's the default trap.

Typography isn't holding the design — it **is** the design. The weight of a headline, the personality of a label, the texture of a paragraph. These shape how the product feels before anyone reads a word.

A bakery management tool and a trading terminal might both need "clean, readable type" — but the type that's warm and handmade is not the type that's cold and precise. If the codebase reaches for Inter, system-ui, or the framework default without naming why, that's a default.

**Signs of a typography default:**
- Inter / system-ui chosen with no stated reason
- One typeface for everything; no contrast between display and text
- Hierarchy built only on size (no weight or tracking variation)
- "Looks readable" used as justification

**What a non-default looks like:** A typeface chosen for what the product is. Display-text pairing where the contrast does work. Tracking adjusted on headlines for presence. Specific weights chosen for specific roles.

---

## Navigation Feels Like Scaffolding

Build the sidebar, add the links, get to the real work. Default.

Navigation isn't around the product — it **is** the product. Where you are, where you can go, what matters most. The navigation teaches people how to think about the space they're in.

**Signs of a navigation default:**
- Generic sidebar with `Home / Settings / Help` even when the product has nothing to do with home, settings, or help
- Icons-only nav for items that benefit from labels
- Labels for items that work better as icons
- Same nav for every screen even when context differs
- No active state, no current-location indication

**What a non-default looks like:** Nav items named in the product's vocabulary, not generic labels. A signature element specific to this product's space. Active state that does more than colour a background — that earns the user's sense of "I am here."

---

## Data Feels Like Presentation

You have numbers, show numbers. Default.

A number on screen is not design. The question is: what does this number mean to the person looking at it? What will they do with it?

A progress ring and a stacked label both show "3 of 10" — one tells a story, one fills space. Reaching for number-on-label every time isn't designing.

**Signs of a data default:**
- Every metric rendered as `BIG NUMBER` over `small label`
- KPI cards in a uniform 4-column grid regardless of what the metrics mean
- Numbers with no comparison (no delta, no benchmark, no trend)
- Data visualisations chosen for "looks pro" rather than what the data is doing
- Charts with all defaults from the charting library

**What a non-default looks like:** A metric rendered the way its meaning wants to be rendered — a sparkline for trend, a ring for progress, a comparison delta for movement, a hero number when it really is the headline.

---

## Token Names Feel Like Implementation Detail

`--gray-700`, `--surface-2`, `--primary`. Default.

CSS variable names are design decisions. `--ink` and `--parchment` evoke a world. `--gray-700` and `--surface-2` evoke a template. Someone reading only the token file should be able to guess what product this is.

**Signs of a token default:**
- Token names from a popular framework convention (`--surface-1`, `--surface-2`, …)
- Colour tokens named after their hex value (`--blue-500`)
- No domain vocabulary in the token system
- The same token names that appear in five other repos

**What a non-default looks like:** Token names that belong to this product's world. Domain-specific vocabulary. Reading the tokens out loud gives a sense of what the product is for.

---

## Surface System Feels Like A Default Tailwind Config

Three grays, one accent, ship it. Default.

The surface system is the backbone of craft. Subtle elevation, low-opacity borders, considered control backgrounds — these are the parts that read as "professional" without anyone being able to name why.

**Signs of a surface default:**
- Only two surface levels (background + card)
- Solid hex borders (`#e5e5e5`)
- Inputs with the same background as the surface they sit on
- Sidebar in a different colour than the main canvas with no border separation
- Dropdowns at the same elevation as the card they emerged from

**What a non-default looks like:** A numbered elevation scale, low-opacity rgba borders, dedicated control tokens, the sidebar grounded in the canvas with subtle separation, dropdowns clearly one level above their origin.

---

## Spacing Feels Like Padding

Pick a number, ship the component. Default.

Spacing is a system. Every spacing value should be explainable as N × base-unit. Random padding values, asymmetric padding for no reason, inconsistent gaps — these are the loudest tell of "no system."

**Signs of a spacing default:**
- `padding: 17px`, `padding: 13px`, `margin-top: 23px`
- Asymmetric padding (`padding: 24px 16px 12px 16px`) with no reason
- Tailwind padding utility classes used inconsistently (`p-3` here, `p-4` there, `p-5` on a similar element)
- No discernible base unit

**What a non-default looks like:** Every spacing value on the grid. Symmetrical padding by default. A scale that distinguishes micro, component, section, and major spacing.

---

## Depth Feels Like A Shadow

Add a shadow, ship the card. Default.

Depth strategy is a commitment. Borders-only, subtle single shadow, layered shadow, or surface colour shifts — pick one and apply it everywhere. Mixed strategies read as accidental.

**Signs of a depth default:**
- Some cards have shadows, others have borders, others have neither
- Drop shadows on a flat-system interface
- No shadows at all in a system that wants premium depth
- Library defaults imported wholesale (Material-style shadows on a Linear-style app)

**What a non-default looks like:** A named depth strategy applied consistently. Shadow tokens if shadow is the strategy. Border progression if borders are the strategy. No accidental mixes.

---

## States Feel Like Extra Work

Default state, ship. Default.

States are not extras. Hover, focus, active, disabled, loading, empty, error — these are the difference between "a photograph of software" and "software."

**Signs of state defaults:**
- `outline: none` on buttons with no replacement focus
- No hover state on clickable rows
- Empty states that just say "No items"
- Loading states that fall back to a blank screen
- Error states that surface stack traces

**What a non-default looks like:** Every interactive element answers to hover, focus, active, and disabled. Async data has loading, empty, and error states designed.

---

## Copy Feels Like Filler

Lorem ipsum, "John Doe", "Item 1 / Item 2" — and on the way to production, "Welcome to your dashboard." Default.

Content incoherence breaks the illusion faster than any visual flaw. A beautifully designed interface with nonsensical content is a movie set with no script.

**Signs of a copy default:**
- Sample names, sample emails, sample dates in shipped surfaces
- AI-flavoured marketing phrasing inside utility software
- Generic actions ("Submit", "Save", "OK") where verb-specific labels would be sharper
- Empty states with no guidance
- Mixed locales / number formats on the same surface

**What a non-default looks like:** Copy belongs to one product, one user, one moment. Action labels are verb-specific. Empty states say what to do next. Numbers and dates follow one convention.

---

## The Diagnostic Move

For every load-bearing decision in the surface, ask:

> Could another AI, given a similar prompt, produce substantially the same choice here?

If yes — it's a default. Name it as a finding. Propose a non-default alternative grounded in the product's intent.

If the intent is unknown, that itself is the upstream finding — without intent, every decision is a default by construction.
