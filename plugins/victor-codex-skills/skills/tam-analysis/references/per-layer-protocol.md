# Per-Layer Protocol

The 7-step walk for sizing a single layer. The skill repeats this for every layer in the analysis. Conversation runs per-anchor confirm by default — each step is one or more turns with the user.

The seven steps are sequential. Do not skip ahead. Do not pre-pick scope (step 4) before pool-sizing (steps 1-3). Do not size with confidence (step 6) before scope is set (step 5).

## Step 1 — Plain-English Brief, Then Pin the Demand Unit

Open every layer with a **structured plain-English brief**, then propose the demand unit. The brief makes the business intuitive *before* the math starts, gives the user a clean object to push back on, and forces the agent to articulate the layer in operator / practitioner language instead of vendor marketing.

**Always output exactly this template.** One short paragraph per block (1-3 sentences). No skipping blocks, no reordering, no merging.

```
Layer N: <Layer Name>

Plain English: this is <COMPANY>'s "<one-line everyday description of what this business does>" business. <One or two sentences expanding what the product actually does for the customer, in practitioner language.>

Buyer: <primary purchaser role(s) + adjacent influencers — title, function, segment>.

Job-to-be-done: <the outcome the buyer is hiring this product to achieve — verb-led list, not feature list>.

Proposed demand unit: <what is counted>, measured as <count driver> × <intensity driver>.

Monetization: <pricing model — subscription, take rate, sale, attach, service, ad load — and the primary pricing axis(es)>.

Confirm this demand unit, or reframe.
```

**Jobs-to-be-Done framing (Christensen)**: the buyer isn't buying the product, they're hiring it to make progress on a job. Phrase Job-to-be-done as outcomes the buyer wants, not features the product ships.

**Plain-English rules:**
- No marketing copy ("industry-leading," "best-in-class," "platform of choice," "next-generation").
- No internal product names unless they're industry-standard vocabulary.
- Use the buyer's words, not the vendor's.
- If you can't explain the business to a smart outsider in one paragraph, the layer is mis-scoped — surface that.

**Worked example (PANW, Layer 3 — Security Operations Platform):**

> Layer 3: Security Operations Platform
>
> Plain English: this is PANW's "help the security team find and respond to attacks" business. It's the software a security operations center uses to collect signals, triage alerts, investigate suspicious activity, coordinate response, and automate repetitive steps.
>
> Buyer: CISO, SOC leader, detection/response team, security engineering. CIO/IT ops may matter if replacing legacy log-management or SIEM tools.
>
> Job-to-be-done: reduce alert overload, detect threats faster, investigate across endpoint/network/cloud/email/identity data, automate response, and replace fragmented SIEM, SOAR, XDR, and attack-surface tools.
>
> Proposed demand unit: security-operations platform spend by organizations that run in-house or hybrid SOC/detection-response programs, measured as SOC-active organizations × average annual SecOps platform spend.
>
> Monetization: recurring software subscription, often priced by data volume, endpoints/users/assets, modules, or enterprise platform contract.
>
> Confirm this demand unit, or reframe.

**Worked example (AMZN, Layer 1 — US online retail):**

> Layer 1: US Online Retail
>
> Plain English: this is Amazon's "ship stuff people order online" business — its core 1P inventory plus the 3P marketplace where outside sellers list goods Amazon fulfills or facilitates. The customer hits a search box, picks an item, and a box arrives in 1-2 days.
>
> Buyer: US consumer households, with Prime subscribers driving disproportionate share of frequency and basket size. Small-business and procurement buyers are a growing adjacent segment.
>
> Job-to-be-done: get the thing I want fast and cheap, without having to drive somewhere, comparison-shop across stores, or worry about returns.
>
> Proposed demand unit: US online retail spend, measured as US households × annual online retail spend per household × Amazon's captured share (1P revenue + 3P GMV × take rate).
>
> Monetization: 1P retail margin on own-inventory sales + 3P take rate on marketplace GMV + ad-yield overlay on the search surface.
>
> Confirm this demand unit, or reframe.

Wait for user confirmation. Common reframes the user might raise:
- **Demand unit too broad / too narrow** (e.g., split fiction vs reference vs textbook; or include e-books and audiobooks).
- **Buyer wrong** (e.g., it's actually developer-led bottom-up, not CISO top-down).
- **JTBD missing the dominant outcome** (e.g., compliance-driven, not attack-driven spend).
- **Monetization wrong** (e.g., consumption-based, not seat-based; or marketplace take rate, not own-inventory margin).

Reframe accordingly. Save the confirmed framing to `state.json` under the layer:
- `plain_english`: string
- `buyer`: string
- `jtbd`: string
- `demand_unit`: string
- `monetization`: string (high-level model here; numeric components filled in at the multiplication step)

## Step 2 — Build the Pool Today, Top-Down, from Authoritative Sources

Anchor by anchor. Each anchor goes through the anchor-research subagent.

For consumer / retail layers, ground in regional demographic decomposition before aggregating:

```
total_pool_today = Σ over regions of (population × per-capita usage × addressable share)
```

For enterprise layers:

```
total_pool_today = number of target accounts × per-account potential × addressable share
```

Anchors to confirm (consumer-retail example):

1. **Population in geography**. From census / UN.
2. **Per-capita usage**. From industry surveys, trade bodies, government statistics.
3. **Addressable share**. What fraction of population is realistically a customer for this layer (age, income, urbanicity). Cite a comparable's penetration.

Each anchor:
- State what's being sized: "now sizing per-capita books read per year in the US."
- Dispatch anchor-researcher.
- Present value + cited range + URL + confidence.
- User confirms or pushes back (soft block triggers on out-of-range).
- Save to `sources.md`.

Show ranges, not point estimates. Authoritative sources often disagree; flag where definitions vary because that's where errors hide.

Confidence labels per anchor:
- **High** — official statistics, recent, well-defined.
- **Moderate** — peer disclosure or industry research with explicit method.
- **Low** — inferred from indirect data, or estimated from older or partial sources.
- **Unknown** — no defensible source; pure assumption flagged as such.

## Step 3 — Project the Pool's Growth Path to Maturity

Pool growth = population growth × per-capita usage shift × structural shifts.

Drivers to source (with anchor-researcher):

- **Population projection** — UN World Population Prospects, national statistics.
- **Per-capita usage shift** — secular trend in usage, citing recent CAGR or directional research. Don't extrapolate a temporary trend.
- **Structural shifts** — digital adoption, regulation, urbanization, electrification, demographic transitions. Anchor each on a source.

Show the pool size:
- Today
- Y10
- Y20
- At this layer's maturity

The layer's maturity year is set here. Different layers mature at different times — see `layer-protocols.md` for calibration. Don't default to a global horizon.

Math-checker dispatched after this step to validate compounding:

```
pool_at_year_N = pool_today
    × (1 + population_CAGR_in_period) per period
    × (1 + per_capita_usage_CAGR) per period
    × (1 + structural_shift_CAGR) per period
```

If the compounding produces a number that surprises the user, that's a feature — it surfaces the mechanism. Don't smooth or pre-haircut.

## Step 3.5 — Layer Activation Schedule

Each layer carries metadata describing **when** it contributes meaningful revenue. This is discipline metadata only — the consolidated company-level revenue path is declared per scenario at the multiplication step (Y1-3 / Y4-5 / Y6-10 / Y11-20 / Y21-maturity CAGRs per scenario, anchored on management guidance). The layer activation schedule feeds a downstream **consistency check** that flags when the declared CAGRs are incompatible with the layer thesis.

### Fields per layer

- **`activation_year`**: year revenue begins contributing meaningfully (≥1% of layer maturity revenue). Core layers already shipping: `0` (today). Speculative or to-be-launched: typically Y2-Y10.
- **`peak_contribution_year`**: year the layer contributes the most to consolidated *%-growth*. For S-shaped layer ramps this is roughly the midpoint between activation and maturity, but the user picks it based on the layer thesis (e.g., AWS peak-contribution year is when its still-growing revenue × its share of total parent revenue is highest — not necessarily when the layer's own growth rate is highest).
- **`maturity_year`** (already in Step 3): when the layer's revenue is mostly built out and growth slows toward terminal pace.

### Per-scenario differences

Most layers share the same schedule across bear / low / base / high / bull — endpoint differences drive the scenario spread, not timing. A handful of layers may have scenario-specific schedules:

- **Speculative layer**: never activated in bear by hard rule (`bear.activation_year = null`; layer revenue = 0 in bear). May activate later in `low` than in `base` if the catalyst is delayed under adverse conditions.
- Layer arriving earlier in bull / high due to a specific catalyst (e.g., regulatory unlock): `bull.activation_year < base.activation_year`.

Share the schedule by default. Only differentiate when there's a named catalyst.

### Why the schedule is metadata, not a generator

The consolidated company-level revenue path is **declared per scenario** at the multiplication step (Y1-3 / Y4-5 / Y6-10 / Y11-20 / Y21-maturity CAGRs per scenario), anchored on management guidance + consensus for Y1-3 and on the layer thesis for later periods. The path is not algorithmically derived from per-layer ramps.

The activation schedule's job is to enforce *consistency* between the declared path and the layer thesis. If a layer activates Y4 contributing ≥15% of scenario endpoint but the user's declared Y4-5 CAGR is below Y1-3 CAGR, the layer is invisible in the path — math-checker flags this and the user resolves (revise CAGRs, revise the layer contribution, or name an offsetting mechanism). Conversely: if no layer activates after Y3 contributing ≥15%, post-Y3 CAGRs must be monotonically decreasing (smooth fade); a user who declares mid-cycle elevation with no layer behind it gets flagged.

The path itself comes from the user, anchored on guidance + thesis. The layer schedule keeps the thesis honest.

### What this skill captures in state.json

```json
"activation_schedule": {
  "shared_across_scenarios": true,
  "activation_year": 0,
  "peak_contribution_year": 5,
  "maturity_year": 18,
  "per_scenario_overrides": {
    "bear": null,
    "low": null,
    "base": null,
    "high": null,
    "bull": null
  }
}
```

When `shared_across_scenarios = true`, `per_scenario_overrides` is null. When a scenario has a specific catalyst, the override block carries the per-scenario fields.

## Step 4 — Propose 2-3 Plausible Scopes

Tight / plausible / aggressive. Explain the **structural difference**, not just the number.

Example:

> Agent: Three scopes for the international expansion layer:
>
> - **Tight**: English-speaking developed markets only (UK, Australia, Canada). Pool similar in structure to US, ~120M households. Localization cost low. Mature share comparable.
> - **Plausible**: Adds EU + Japan. Pool ~250M households, but localization, regulation, and last-mile fulfillment differ materially. Mature share lower than US.
> - **Aggressive**: Adds China + India + Latam. Pool ~1.5B households, but competitive density is severe (local incumbents with stronger network effects); margin structure differs.
>
> Which scope feels right for this layer?

Do NOT pick. Wait for user.

If the user picks aggressive, push back on the realistic share / monetization for the harder markets (silent conservatism is bad; silent generosity is worse).

## Step 5 — Wait for User Scope

Geography, segment, product breadth, and adjacency inclusion are user judgment calls. The skill is not authorized to pick — these decisions shape the analysis fundamentally and depend on what the user finds plausible after seeing the structural differences between scopes.

If the user is genuinely undecided, propose a base-case scope to anchor on, then offer scenario branches in the multiplication step. Don't lock scope without explicit user input.

Confirmed scope goes into `state.json`.

## Step 6 — Size with Explicit Confidence Labels

Now size the layer at the chosen scope:

```
layer_pool_at_maturity = chosen_scope_pool_today × pool_growth_to_maturity
```

Confidence label per driver. Push back when user is too generous AND when user is too conservative.

Common pushback patterns:

| User stance | Pushback |
|-------------|----------|
| "Penetration will plateau at current level" in a still-growing category | "Penetration was X 5 years ago, Y now. What stops the trajectory?" |
| "Mature share will be very low because competition" | "Which competitor specifically, and what's their wedge? If there's no named threat, the haircut isn't defensible." |
| "Mature share will be very high because moat" | "Strongest comparable in the category reached <Y>%. What's the structural reason this layer reaches higher?" |
| "Real pricing will be flat" in a moat-protected category | "Comparable companies in this category sustained +1-2% real pricing for decades. Why does this one not?" |

Each pushback ends in either: user names a mechanism (accept their number, log mechanism) or revises (accept revised number).

## Step 7 — Check Overlap with Adjacent Layers, Apply Explicit Haircuts

Before declaring the layer pool-sized, check overlap with already-sized layers:

- **Customer overlap**: same household / customer counted across multiple layers? If yes, the multi-product customer is one customer.
- **Spend overlap**: same dollar of spend captured across layers? E.g., a marketplace's GMV from category X is also captured in the category-X retail layer.
- **Capacity overlap**: same physical / digital asset serving multiple layers? E.g., a fulfillment network serving both core retail and a marketplace logistics service.

Apply explicit haircut. Document in `state.json` under `overlap_haircuts`. Don't double-apply at the multiplication step.

Common haircut sizes (anchor; not prescriptive):
- Adjacent retail categories serving same household: 10-25% haircut on the smaller layer.
- Marketplace overlapping core inventory: 30-50% haircut on the marketplace layer for the overlap region.
- Speculative adjacency reusing core infrastructure: less overlap on revenue, more on capex (which doesn't affect TAM but matters for DCF later).

## Per-Layer Dialogue Pattern Example

For a single layer, expect roughly 6-10 conversational turns under per-anchor pacing:

1. Define demand unit, get user confirmation.
2. Build pool — anchor 1 (e.g., population). Subagent fetch, present, confirm.
3. Build pool — anchor 2 (e.g., per-capita usage). Subagent fetch, present, confirm.
4. Build pool — anchor 3 (e.g., addressable share). Subagent fetch, present, confirm. Aggregate pool today.
5. Project to maturity — propose drivers, get user confirmation, dispatch math-checker.
6. Propose 2-3 scopes, get user pick.
7. Size with confidence, push back if needed.
8. Overlap check.
9. (Optional) Revise if pushback resolved differently than expected.

In `faster` mode: skill collapses steps 2-4 into one anchor presentation per layer and steps 6-8 into one summary. ~3-4 turns per layer.

In `autopilot` mode: skill runs the whole layer and saves to `state.json`; user reviews at the end. 1 turn per layer (acknowledgment).

## Saving After Each Step

Every step writes to `state.json`:

```json
{
  "layers": [
    {
      "name": "us-online-book-retail",
      "speculative": false,
      "demand_unit": "...",
      "pool_today": {"value": "...", "range": "...", "confidence": "..."},
      "pool_at_maturity": {"value": "...", "year": "Y15", "confidence": "..."},
      "scope": "...",
      "share": {"bear": "...", "low": "...", "base": "...", "high": "...", "bull": "..."},
      "monetization": {...},
      "real_pricing_cagr": {"d1": "...", "d2": "...", "d3": "..."},
      "overlap_haircut": "...",
      "sources": ["url1", "url2"]
    }
  ]
}
```

Schema: `state-schema.md`.

Dialogue continuously appended to `dialogue.md` so the session is recoverable after compaction.
