# Per-Layer Protocol

The 7-step walk for sizing a single layer. The skill repeats this for every layer in the analysis. Conversation runs per-anchor confirm by default — each step is one or more turns with the user.

The seven steps are sequential. Do not skip ahead. Do not pre-pick scope (step 4) before pool-sizing (steps 1-3). Do not size with confidence (step 6) before scope is set (step 5).

## Step 1 — Define the Demand Unit Precisely

Open the layer with a short statement of what is being counted and why it's the natural unit for this layer. Confirm with user.

Components:
- **What is counted**: vehicles, seats, transactions, stores, baskets, square meters, kWh, subscribers, parcels, GMV, etc.
- **Who buys it**: consumer demographic, enterprise role, institutional segment.
- **What drives usage**: frequency, attach rate, replacement cycle, density per capita.
- **How it's monetized**: subscription, take rate, sale, attach, service, ad load.

Example dialogue:

> Agent: This layer is "online book retail to US consumers." Demand unit = books sold online to a US consumer. Consumer-side driver: per-capita books read per year × share of those bought (vs library, used, etc.) × share bought online. Monetization: price per book × Amazon's take of the transaction (full retail margin in own-inventory mode). Right framing, or would you split it differently?

Wait for user confirmation. Common reframes the user might raise:
- Demand unit too broad (e.g., split fiction vs reference vs textbook).
- Demand unit too narrow (e.g., include e-books and audiobooks).
- Monetization model wrong (e.g., the layer is actually marketplace take rate, not own-inventory margin).

Reframe accordingly. Save the confirmed framing to `state.json` under the layer.

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

## Step 4 — Propose 2-3 Plausible Scopes

Tight / plausible / aggressive. Explain the **structural difference**, not just the number.

Example:

> Agent: Three scopes for the international expansion layer:
>
> - **Tight**: English-speaking developed markets only (UK, Australia, Canada). Pool similar in structure to US, ~120M households. Localization cost low. Mature share comparable.
> - **Plausible**: Adds EU + Japan. Pool ~250M households, but localization, regulation, and last-mile fulfillment differ materially. Mature share lower than US.
> - **Aggressive**: Adds China + India + Latam. Pool ~1.5B households, but competitive density is severe (local incumbents with stronger network effects); margin structure differs.
>
> Which one fits the thesis?

Do NOT pick. Wait for user.

If the user picks aggressive, push back on the realistic share / monetization for the harder markets (silent conservatism is bad; silent generosity is worse).

## Step 5 — Wait for User Scope

Geography, segment, product breadth, adjacency inclusion are judgment calls dependent on the thesis. The skill is not authorized to pick.

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
      "share": {"bear": "...", "base": "...", "bull": "..."},
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
