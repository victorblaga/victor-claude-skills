# Multiplication Protocol

Once every layer is pool-sized — and ONLY then — turn pools into revenue. Four sub-steps per layer per scenario (bear / low / base / high / bull).

The order is non-negotiable:

```
mature share × monetization (today's $, today's mix) × real pricing compounding → inflation overlay → nominal $ at layer maturity year
```

Apply inflation last (within the per-layer flow). Real pricing first. After the per-layer inflation overlay, every number that feeds aggregation and the hand-off contract is **nominal**. Math-checker validates every layer's compounding plus the per-layer inflation conversion.

**Unit convention — read first.** TAM stores and emits aggregated revenue, period CAGRs, and the annual series in **nominal $**. Today's-$ appears only inside per-layer sizing math (sub-steps 1-3) as an intuitive unit; the per-layer inflation overlay rolls it to nominal before aggregation. External anchors that arrive nominal (management guidance, consensus analyst estimates, last reported YoY growth, peer historical CAGRs) feed the nominal contract directly — no real/nominal stripping. The downstream `/tam-dcf` consumes the nominal series as-is and never re-inflates.

## Sub-Step 1 — Mature Share / Penetration

Anchor on real category-leader patterns. Don't pick a number without citing precedent.

| Pattern | Mature share | Examples |
|---------|--------------|----------|
| Platform with moat in fragmented category | 20-35% | Costco in warehouse retail (~20% of warehouse-club, much lower of total grocery); Home Depot in DIY (~30% with Lowe's) |
| Category-defining platform in narrow vertical | 40-60% | Copart in US salvage auctions (~50%); Auto Trader in UK car listings (~70% by traffic) |
| One of many in commodity category | 5-15% | Generic apparel retailers, mid-tier banks, mid-tier insurers |
| Regional retailer at saturation (rural-density model) | 30-50% of catchment | Tractor Supply in rural US; Dollar General in low-density US |
| Marketplace with strong network effects | >50% in core geography | Mercado Libre in Latam categories; Adyen in card-not-present EU; classifieds incumbents |
| Premium brand in luxury category | 20-40% of category, but with high real pricing | Hermès, LVMH brand-specific |
| Regulated infrastructure | 30-60% of regulated zone | Local utilities, regulated rail, regulated airports |
| Two-sided platform with network effects + economies of scale | 40-70% | Visa+MA together ~60% global card volume |
| Loss-leading consumer subscription chasing engagement | 10-30% household penetration | Streaming services in mature markets |

When picking, write the precedent in `sources.md`: "Set mature share for `<layer>` at `<X>%` because `<comparable company> reached <Y>% in <category>, citing <source>`." Don't pick precedent that's structurally weaker than the layer's actual dynamics (don't anchor a moat-protected layer on a commodity precedent).

Five-scenario spread for share. Pick all five per layer. Math-checker enforces monotonicity `bear ≤ low ≤ base ≤ high ≤ bull` (equality allowed where the layer is share-insensitive in that direction).

- **Bear** — absolute worst plausible: share is challenged by named substitute or commoditization mechanism in full force. Often 30-50% below base.
- **Low** — realistic adverse: partial materialization of the bear mechanism (e.g., some segments compress but core holds). Typically 15-30% below base.
- **Base** — evidence-weighted from precedents and current trajectory.
- **High** — realistic upside: partial realization of bull catalysts (e.g., adjacencies start contributing meaningfully but full saturation not reached). Typically 10-20% above base.
- **Bull** — absolute best plausible: precedents from the strongest comparable, plus any incremental moat-strengtheners (e.g., data feedback loops, switching costs, regulatory) all activating.

## Sub-Step 2 — Mature Monetization in Today's $, Today's Mix

**Unit discipline.** Monetization-today is a **snapshot in today's purchasing-power $**, back-solved from the latest disclosed revenue / unit count. Peer benchmarks must also be **today's-$ snapshots** (latest reported actual), NEVER forward analyst projections. Pasting a forward ARPU/ASP CAGR onto today's-$ monetization would double-count the real-pricing fade in sub-step 3 AND the inflation overlay in sub-step 4 — silent 4-6%/yr drift.

The anchor-researcher dispatch for monetization anchors (ARPU, ASP, take rate, sales/store, NIM, etc.) must request the **latest reported actual** with a `basis: "today_dollar_snapshot"` tag, not a forward projection. Mix shift is a separate explicit input here — declared by the user at sub-step 2, not implicitly built into the metric.

Use the metric appropriate to the business model:

| Business model | Pool unit | Monetization metric |
|----------------|-----------|---------------------|
| SaaS / telecom / streaming | Seats, subscribers | ARPU |
| Retailer | Stores at saturation, sqm | Sales / store, sales / sqm, basket |
| Marketplace / auction | Transactions, GMV | Take rate, revenue / transaction |
| Industrial / hardware | Units, installed base | ASP, attach rate × service |
| Bank / financial services | Accounts, AUM, loans | Revenue / account, NIM, fee rate |
| Insurance | Policies in force | Premium / policy, take rate on premium |
| Payments | Transactions, volume | Take rate (bps), revenue / transaction |
| Consumer subscription | Households, members | ARPU |

Build from:

- **Current actuals**, back-solved from disclosed revenue / unit count.
- **Peer benchmarks** — best-in-class for the category, plus median.
- **Mix shift** — explicit assumption about how product / segment / geography mix changes by maturity.

Show the mix explicitly in `sources.md`. Don't paste a today's-blended-ARPU into a maturity calculation where the mix is meaningfully different.

Five-scenario spread for monetization. Pick all five per layer. Monotonicity enforced.

- **Bear** — absolute worst: monetization compresses fully (take-rate competition, mix shift to cheaper tiers, ARPU regression).
- **Low** — realistic adverse: partial compression (e.g., new entrants take some volume, but pricing power on core holds).
- **Base** — today's metric × explicit mix shift, in today's $.
- **High** — realistic upside: some upsell / cross-sell catalysts hit; mix shift toward higher tiers partial.
- **Bull** — absolute best: explicit upsell / cross-sell mechanism, mix shift to higher tiers, premium positioning all realized.

## Sub-Step 3 — Real Pricing Power Per Year (Above Inflation)

Per layer. Express as a fading profile in REAL %.

```
0% real = pricing matches inflation
+2% real = pricing exceeds inflation by 2% / year
```

Fading is critical: pricing power decays as the layer matures. Apply higher real % in early decades, lower in later decades.

| Pricing power | Examples | Decade 1 / 2 / 3 (real %) |
|---------------|----------|----------------------------|
| High | Narrow-vertical SaaS, dominant marketplace, premium brand, regulated infra | +2.5% / +2% / +1.5% |
| Medium | Most enterprise software, premium retail, regulated infra in competitive geos | +1.5% / +1% / +0.5% |
| Low | Commodity goods retail, mature staples, low-end consumer | ~0% (just inflation) |
| Negative | Commoditizing tech, deflationary categories | -1% to -3% |

Real pricing compounds the monetization metric over the horizon **before inflation is applied**.

Math-checker validates the compounding. Formula:

```
monetization_at_maturity_today_$ = monetization_today
    × Π over years (1 + real_pricing_CAGR_in_that_year)
```

Five-scenario spread:
- **Bear** — absolute worst: pricing power well below the implied tier (commoditization, regulatory price caps, new entrants).
- **Low**: pricing power partially below tier (some segments commoditize).
- **Base** — tier-appropriate.
- **High**: pricing power partially above tier (moat strengthens on some axes).
- **Bull** — absolute best: tier-up across the board because the moat strengthens broadly (network effects deepen, switching cost rises, brand premium grows).

## Sub-Step 4 — Inflation Overlay (Apply LAST, Within Per-Layer Flow)

Convert today's-$ output → nominal $ at the per-layer maturity year. Apply once per layer, only at this step. After this step, the layer's contribution to the aggregate is nominal — no further inflation overlay anywhere downstream (DCF consumes nominal, does not re-inflate).

Anchor inflation on the **long-run expectation for the reporting currency**:

| Currency | Long-run inflation anchor | Source |
|----------|---------------------------|--------|
| USD | ~2% (Fed target) | FOMC long-run projections |
| EUR | ~2% (ECB target) | ECB monetary policy strategy |
| GBP | ~2% (BoE target) | BoE remit |
| JPY | ~2% (BoJ target, often undershoots) | BoJ outlook |
| CHF | ~1% (SNB target, often undershoots) | SNB monetary policy |
| EM currencies | Country-specific — 4-8% common, higher for fragile EMs | IMF World Economic Outlook |

For EM-heavy or multi-currency companies, use the reporting currency's inflation rate (translated revenue is what the DCF receives). Note any large divergence between operating-currency inflation and reporting-currency inflation in `sources.md`.

Formula:

```
layer_revenue_nominal_at_layer_maturity = layer_revenue_today_$_at_layer_maturity
    × (1 + inflation) ^ years_to_layer_maturity
```

For layers maturing **before** the hand-off horizon, post-maturity revenue is assumed flat in today's-$ (mature category — no real growth) and grows at inflation in nominal terms. The roll to hand-off horizon nominal $:

```
layer_revenue_nominal_at_horizon = layer_revenue_today_$_at_layer_maturity
    × (1 + inflation) ^ horizon_years
```

(Equivalent to `nominal_at_layer_maturity × (1+inflation)^(horizon − layer_maturity)`.)

For layers maturing **after** the hand-off horizon, the layer is still ramping at the horizon — use the still-ramping today's-$ projection at the horizon year, then apply inflation to nominal.

Math-checker validates the conversion per layer and the aggregation to nominal at the hand-off horizon.

## Aggregation

Total revenue at hand-off horizon = sum over layers of `layer_revenue_nominal_at_horizon` (post-overlap-haircut), computed per scenario (bear / low / base / high / bull). **This is the contract endpoint.**

Overlap haircut applied here, not at sizing. The haircut accounts for double-counted units:
- Same household using both core retail and adjacent retail (count household once across both layers).
- Same enterprise customer buying core SaaS and an adjacent SaaS module (count customer once).
- Same payment volume routed through both core flows and value-added services (account for what's pure-take-rate vs incremental).

Per-layer maturity differences: at the chosen hand-off horizon, some layers are mature (already at their layer-maturity year), others are still ramping. Each layer's nominal contribution at the hand-off horizon is computed per the rule above.

Math-checker validates both cases and verifies scenario monotonicity (`bear < low < base < high < bull`) at the aggregated **nominal** level.

## Growth Path Declaration (Per Scenario)

After aggregation, declare the **per-scenario nominal period CAGRs** that compound from Y0 nominal revenue to each scenario's nominal endpoint. These nominal CAGRs are the contract the downstream DCF consumes. They are user-confirmed inputs, not generated from layer ramps.

### Y1-3 Anchor — Mandatory

Before declaring per-scenario CAGRs, dispatch anchor-researcher for management guidance + consensus analyst expectations on Y1-3 revenue growth. The dispatch is mandatory — Y1-3 cannot be picked without this anchor in `aggregated.y1_3_guidance_anchor`.

Dispatch payload:

> "For `<TICKER>`, fetch: (a) latest official management guidance for next-FY revenue (range + midpoint, with source: 10-K, latest 10-Q, latest earnings press release, latest investor-day deck); (b) 2-3 year consensus analyst revenue estimates (median or mean, source: Bloomberg, Refinitiv, or whatever public aggregator is accessible — Yahoo Finance, Seeking Alpha summary, Koyfin). Express both as implied YoY growth rates from the last reported FY. These are **nominal** growth rates as reported by management/consensus — do not strip inflation, do not convert to real. Return midpoint + range + source URLs + retrieval date."

The skill then offers the user this anchor as the default Y1-3 **base-case nominal** CAGR. The base Y1-3 nominal CAGR is compared to the nominal guidance midpoint **directly** — no real/nominal conversion, since mgmt guidance is already nominal. The other four scenarios take reasoned spreads from base, each with a named mechanism:

- **Bear** (absolute worst plausible): typically -4 to -6pp below guidance midpoint. Full bear-mechanism materialization.
- **Low** (realistic adverse): typically -2 to -3pp below guidance midpoint. Partial bear-mechanism materialization.
- **Base** — guidance midpoint (±3pp tolerance).
- **High** (realistic upside): typically +1 to +2pp above guidance midpoint. Partial bull-catalyst realization.
- **Bull** (absolute best plausible): typically +3 to +5pp above guidance midpoint. Full bull-adjacency activation.

**Tolerance**: only the **base** scenario's Y1-3 CAGR is hard-anchored to guidance (within ±3pp). The other scenarios are not tolerance-checked against guidance — they're checked against base for direction and magnitude, with each non-base scenario carrying a named `override_reason` logged in `sources.md` describing the mechanism driving the spread.

Common legitimate base-override scenarios: turnaround company where guidance lags catalyst; post-IPO company where guidance is sandbagged; pre-revenue or hyper-cyclical company where guidance is meaningless.

### Per-Period Declaration

Walk through each scenario (bear / low / base / high / bull). For each, declare:

1. **Y1-3** — anchored on guidance (above). Same number for all 3 years within the period.
2. **Y4-5** — first adjacency / first new layer starts contributing if the layer thesis is stacked. User declares; math-checker validates against activation schedule.
3. **Y6-10** — multi-layer compounding phase. For stay-elevated theses (adjacency layers contributing materially through this period), often elevated vs Y1-3. For smooth-fade theses, fading.
4. **Y11-20** — layer maturities unfold; core saturates while later-stage adjacencies still contribute. Typically below Y6-10.
5. **Y21-maturity** — speculative layers finishing their ramp; core in pricing-only growth. Typically the lowest period CAGR (approaches terminal nominal growth = real terminal + inflation).

### Validation by Math-Checker

Four checks, all mandatory:

1. **Hand-off contract test (compound-to-endpoint).** For each of the 5 scenarios, the declared **nominal** period CAGRs must compound from Y0 nominal revenue to the scenario's stated nominal endpoint within 2%. If not, halt — force user to revise CAGRs, revise endpoint, or revise interpretation. No silent rescaling.
2. **Y1-3 anchor test.** The **base** scenario's Y1-3 nominal CAGR must be within ±3pp of `y1_3_guidance_anchor.midpoint` (which is itself nominal — mgmt guidance is naturally nominal), OR carry a named `override_reason`. The other scenarios (bear / low / high / bull) take reasoned spreads from base with each carrying its own `override_reason` describing the bear-mechanism / bull-adjacency intensity that drives the spread. **Comparison is nominal-on-nominal, no conversion.**
3. **Layer-schedule consistency test.** For each of the 5 scenarios, given the per-layer `activation_schedule` and per-scenario nominal endpoint contribution per layer:
   - If a layer activates in period P, contributes ≥15% of scenario nominal endpoint, the CAGR in period P (and in the period containing `peak_contribution_year`) must be ≥ Y1-3 CAGR − 1pp. Otherwise the layer is invisible in the path — flag.
   - If NO layer activates after Y3 contributing ≥15%, the post-Y3 CAGRs (Y4-5, Y6-10, Y11-20, Y21-maturity) must be monotonically decreasing. Otherwise the user has declared elevation with no layer behind it — flag.
   - Violations surface to the main thread; user resolves by revising CAGRs, revising the layer schedule, or naming an offsetting mechanism.
4. **Scenario monotonicity test.** `aggregated.revenue_at_maturity_nominal_$` must satisfy `bear < low < base < high < bull`. Same check applied to per-layer `layer_revenue_at_horizon_nominal_$` (the aggregation-feeding field). Secondary check on `layer_revenue_at_maturity_nominal_$` (nominal at the layer's own maturity year). Equality is allowed only where the layer is genuinely scenario-insensitive on that boundary (rare; requires justification). Strict violation on the aggregation-feeding fields = halt.

## Annual Revenue Series (Derived) — Nominal

For each scenario, the **nominal** annual revenue series Y0 → Y_horizon is **derived** from the declared nominal period CAGRs by linear interpolation in growth-rate space, anchored on the last reported FY YoY growth (nominal) at Y0. This eliminates kinks at period boundaries while preserving the stated nominal period CAGRs exactly.

Math-checker computes this with the following recipe:

```python
def annual_nominal_series_from_period_cagrs(rev_y0_nominal, last_year_nominal_growth, nominal_period_cagrs, horizon_year):
    # nominal_period_cagrs keys: y1_3, y4_5, y6_10, y11_20, y21_maturity
    # All growth rates are NOMINAL. Y0 anchor is nominal revenue.
    # Step 1: place rate-anchors at period midpoints
    anchors = {
        0: last_year_nominal_growth,
        2: nominal_period_cagrs["y1_3"],
        4.5: nominal_period_cagrs["y4_5"],
        8: nominal_period_cagrs["y6_10"],
        15.5: nominal_period_cagrs["y11_20"],
        (21 + horizon_year) / 2: nominal_period_cagrs["y21_maturity"],
    }
    # Step 2: interpolate growth rate per year (linear between consecutive anchors)
    series = [rev_y0_nominal]
    for y in range(1, horizon_year + 1):
        g = interpolate_linear(anchors, y)
        series.append(series[-1] * (1 + g))
    # Step 3: renormalize each period so the stated nominal CAGR matches exactly
    series = renormalize_periods(series, nominal_period_cagrs, horizon_year)
    return series
```

The renormalization step applies a small constant adjustment per period so that `(series[period_end] / series[period_start])^(1/period_years) - 1` matches the stated nominal period CAGR exactly. This preserves smoothness within periods while honoring the stated CAGRs at period boundaries.

Saved to `aggregated.annual_revenue_nominal_per_scenario` with a `_provenance` key recording that the series is derived and regenerable from the nominal CAGRs. The nominal CAGRs are the contract.

## Pre-Emit Checks (Run Before Hand-Off)

1. **Did we pass the Fermi output through as actual revenue at maturity, or silently haircut?** Compare summary numbers (aggregated nominal $ at horizon, per scenario) to the aggregated layer table. They must match.
2. **Did we apply real pricing and inflation each exactly once, in the right order?** Real pricing compounds today's-$ monetization (sub-step 3); inflation overlay rolls the today's-$ output to nominal at the per-layer maturity (sub-step 4). After sub-step 4 every contract number is nominal — no further inflation. Check `state.json` — both per-layer fields populated; nominal aggregation reflects the overlay applied once per layer.
3. **Are nominal anchors carried as nominal, with no real/nominal stripping?** Mgmt guidance midpoint, consensus midpoint, last reported YoY growth are nominal by construction. They feed nominal Y1-3 CAGRs directly. If any of these were silently converted to real (e.g., guide 10.8% nominal stored as 10.8% real), the period CAGRs are wrong by inflation in every period — surface and fix.
4. **Does the declared per-scenario growth path match the layer activation schedule?** A stacked-thesis (adjacencies activating Y4+ contributing ≥15% of endpoint) must show CAGR elevation in the activation period — not fade. A smooth-fade thesis (no late activators) must show post-Y3 CAGRs monotonically decreasing. Verified by `layer_schedule_consistency_test` in math-checker.
5. **Is there exactly ONE base case, not two?** Search the state and any draft hand-off for a "conservative alternative base," "analyst-haircut base," "haircut to X%," or similar parallel scenario. If found, it's an error. Either the underlying numbers were revised (and the old ones should be gone) or the disagreement got folded into bear/low/high/bull (and the alternative scenario should be gone). Never carry both.
6. **Are headline scenarios monotone?** `bear < low < base < high < bull` for `aggregated.revenue_at_maturity_nominal_$` and per-layer `layer_revenue_at_horizon_nominal_$` (the aggregation-feeding field). Verified by `scenario_monotonicity_test` in math-checker.

Math-checker runs all five. Any failure must be surfaced to user and resolved before emitting the hand-off block.

## Handling Expert / Analyst Disagreement (Without Magic Haircuts)

When a domain-expert subagent or analyst review pushes back on the bottom-up base, the resolution path is strict:

1. Identify the **specific layer + specific number** the expert disagrees with (e.g., "SP-A mature monetization $8.1B is overstated by ~50%").
2. Present to user: "Expert recommends `<layer>.<field>` go from `<old>` to `<new>`. Reasoning: `<one line>`. Three options: (a) accept revision — layer numbers update, old value disappears; (b) reject — keep current, log rejection reasoning; (c) move into bear / low mechanism — base stays, but bear and low absorb the concern at their respective intensities."
3. Apply the user's choice. State must end with one of: revised number, recorded rejection, or strengthened bear (and low). Never all three. Never a parallel scenario.

The handoff.md output never contains both the original number and a "haircut alternative." If the user changes their mind later, they revise the state again — they don't accumulate alternatives.

The discipline reasoning: a TAM with two bases is undefined. Downstream DCF can't choose; the analyst (and the future self) can't remember which number was the "real" base; the bear-low-base-high-bull spread becomes meaningless because the conservative case is already baked into a parallel base. The whole point of the 5-scenario structure is that bear and low absorb adverse paths and high and bull absorb favorable paths — none of them should need a haircut overlay.
