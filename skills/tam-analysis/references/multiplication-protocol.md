# Multiplication Protocol

Once every layer is pool-sized — and ONLY then — turn pools into revenue. Four sub-steps per layer per scenario (bear / base / bull).

The order is non-negotiable:

```
mature share × monetization (today's $, today's mix) × real pricing compounding → inflation overlay → nominal $ at maturity
```

Apply inflation last. Real pricing first. Math-checker validates every layer's compounding plus the final inflation conversion.

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

Bear / base / bull spread for share:
- **Bear**: share is challenged by named substitute or commoditization mechanism. Often 30-50% below base.
- **Base**: evidence-weighted from precedents and current trajectory.
- **Bull**: precedents from the strongest comparable, plus any incremental moat-strengtheners (e.g., data feedback loops, switching costs, regulatory).

## Sub-Step 2 — Mature Monetization in Today's $, Today's Mix

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

Bear / base / bull spread for monetization:
- **Bear**: monetization compresses (take-rate competition, mix shift to cheaper tiers, ARPU regression).
- **Base**: today's metric × explicit mix shift, in today's $.
- **Bull**: explicit upsell / cross-sell mechanism, mix shift to higher tiers, premium positioning.

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

Bear / base / bull:
- **Bear**: pricing power below the implied tier (commoditization, regulatory price caps, new entrants).
- **Base**: tier-appropriate.
- **Bull**: tier-up because the moat strengthens (network effects deepen, switching cost rises, brand premium grows).

## Sub-Step 4 — Inflation Overlay (Apply LAST)

Convert today's-$ output → nominal $ at the per-layer maturity year. Apply only at the final step.

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
revenue_at_maturity_nominal = revenue_at_maturity_today_$
    × (1 + inflation) ^ years_to_maturity
```

Math-checker validates the conversion per layer and the final aggregation.

## Aggregation

Total revenue at maturity = sum over layers of (layer revenue at maturity, post-overlap-haircut).

Overlap haircut applied here, not at sizing. The haircut accounts for double-counted units:
- Same household using both core retail and adjacent retail (count household once across both layers).
- Same enterprise customer buying core SaaS and an adjacent SaaS module (count customer once).
- Same payment volume routed through both core flows and value-added services (account for what's pure-take-rate vs incremental).

Per-layer maturity differences: at the chosen hand-off horizon, some layers are mature, others are still ramping. Each layer's contribution at the hand-off horizon is:

- If layer-maturity ≤ hand-off-horizon: full mature revenue.
- If layer-maturity > hand-off-horizon: still-ramping projection at the hand-off year.

Math-checker validates both cases.

## Growth Path Declaration (Per Scenario)

After aggregation, declare the **per-scenario period CAGRs** that compound from current revenue to each scenario's endpoint. These CAGRs are the contract the downstream DCF consumes. They are user-confirmed inputs, not generated from layer ramps.

### Y1-3 Anchor — Mandatory

Before declaring per-scenario CAGRs, dispatch anchor-researcher for management guidance + consensus analyst expectations on Y1-3 revenue growth. The dispatch is mandatory — Y1-3 cannot be picked without this anchor in `aggregated.y1_3_guidance_anchor`.

Dispatch payload:

> "For `<TICKER>`, fetch: (a) latest official management guidance for next-FY revenue (range + midpoint, with source: 10-K, latest 10-Q, latest earnings press release, latest investor-day deck); (b) 2-3 year consensus analyst revenue estimates (median or mean, source: Bloomberg, Refinitiv, or whatever public aggregator is accessible — Yahoo Finance, Seeking Alpha summary, Koyfin). Express both as implied YoY growth rates from the last reported FY. Return midpoint + range + source URLs + retrieval date."

The skill then offers the user this anchor as the default Y1-3 base-case CAGR. Bear and bull get reasoned spreads (typical bear: -3 to -5pp below midpoint with named mechanism; typical bull: +1 to +3pp above midpoint with named catalyst).

**Tolerance**: Y1-3 CAGRs per scenario must fall within `±3pp of guidance midpoint`. Out-of-tolerance picks require a named override mechanism logged in `sources.md` (same pushback discipline as any other anchor). Common legitimate overrides: turnaround company where guidance lags catalyst; post-IPO company where guidance is sandbagged; pre-revenue or hyper-cyclical company where guidance is meaningless.

### Per-Period Declaration

Walk through each scenario (bear / base / bull). For each, declare:

1. **Y1-3** — anchored on guidance (above). Same number for all 3 years within the period.
2. **Y4-5** — first adjacency / first new layer starts contributing if the layer thesis is stacked. User declares; math-checker validates against activation schedule.
3. **Y6-10** — multi-layer compounding phase. For stay-elevated theses (adjacency layers contributing materially through this period), often elevated vs Y1-3. For smooth-fade theses, fading.
4. **Y11-20** — layer maturities unfold; core saturates while later-stage adjacencies still contribute. Typically below Y6-10.
5. **Y21-maturity** — speculative layers finishing their ramp; core in pricing-only growth. Typically the lowest period CAGR (approaches terminal nominal growth = real terminal + inflation).

### Validation by Math-Checker

Three checks, all mandatory:

1. **Hand-off contract test (compound-to-endpoint).** For each scenario, the declared period CAGRs must compound to the scenario's stated endpoint within 2%. If not, halt — force user to revise CAGRs, revise endpoint, or revise interpretation. No silent rescaling.
2. **Y1-3 anchor test.** Each scenario's Y1-3 CAGR must be within ±3pp of `y1_3_guidance_anchor.midpoint`, OR carry a named `override_reason` logged in `sources.md`.
3. **Layer-schedule consistency test.** For each scenario, given the per-layer `activation_schedule` and per-scenario endpoint contribution per layer:
   - If a layer activates in period P, contributes ≥15% of scenario endpoint, the CAGR in period P (and in the period containing `peak_contribution_year`) must be ≥ Y1-3 CAGR − 1pp. Otherwise the layer is invisible in the path — flag.
   - If NO layer activates after Y3 contributing ≥15%, the post-Y3 CAGRs (Y4-5, Y6-10, Y11-20, Y21-maturity) must be monotonically decreasing. Otherwise the user has declared elevation with no layer behind it — flag.
   - Violations surface to the main thread; user resolves by revising CAGRs, revising the layer schedule, or naming an offsetting mechanism.

## Annual Revenue Series (Derived)

For each scenario, the annual revenue series Y0 → Y_maturity is **derived** from the declared period CAGRs by linear interpolation in **growth-rate space**, anchored on the last reported FY YoY growth at Y0. This eliminates kinks at period boundaries while preserving the stated period CAGRs exactly.

Math-checker computes this with the following recipe:

```python
def annual_series_from_period_cagrs(rev_y0, last_year_growth, period_cagrs, maturity_year):
    # period_cagrs keys: y1_3, y4_5, y6_10, y11_20, y21_maturity
    # Step 1: place rate-anchors at period midpoints
    anchors = {
        0: last_year_growth,
        2: period_cagrs["y1_3"],
        4.5: period_cagrs["y4_5"],
        8: period_cagrs["y6_10"],
        15.5: period_cagrs["y11_20"],
        (21 + maturity_year) / 2: period_cagrs["y21_maturity"],
    }
    # Step 2: interpolate growth rate per year (linear between consecutive anchors)
    series = [rev_y0]
    for y in range(1, maturity_year + 1):
        g = interpolate_linear(anchors, y)
        series.append(series[-1] * (1 + g))
    # Step 3: renormalize each period so the stated CAGR matches exactly
    series = renormalize_periods(series, period_cagrs, maturity_year)
    return series
```

The renormalization step applies a small constant adjustment per period so that `(series[period_end] / series[period_start])^(1/period_years) - 1` matches the stated period CAGR exactly. This preserves smoothness within periods while honoring the stated CAGRs at period boundaries.

Saved to `aggregated.annual_revenue_today_$_per_scenario` with a `_provenance` key recording that the series is derived and regenerable from the CAGRs. The CAGRs are the contract.

## Three-Error Check (Run Before Hand-Off)

1. **Did we pass the Fermi output through as actual revenue at maturity, or silently haircut?** Compare summary numbers to the aggregated layer table. They must match.
2. **Did we account for real pricing AND inflation separately?** Check `state.json` — both fields populated per layer, neither one folded into the other.
3. **Does the declared per-scenario growth path match the layer activation schedule?** A stacked-thesis (adjacencies activating Y4+ contributing ≥15% of endpoint) must show CAGR elevation in the activation period — not fade. A smooth-fade thesis (no late activators) must show post-Y3 CAGRs monotonically decreasing. Verified by `layer_schedule_consistency_test` in math-checker.
4. **Is there exactly ONE base case, not two?** Search the state and any draft hand-off for a "conservative alternative base," "analyst-haircut base," "haircut to X%," or similar parallel scenario. If found, it's an error. Either the underlying numbers were revised (and the old ones should be gone) or the disagreement got folded into bear/bull (and the alternative scenario should be gone). Never carry both.

Math-checker runs all four. Any failure must be surfaced to user and resolved before emitting the hand-off block.

## Handling Expert / Analyst Disagreement (Without Magic Haircuts)

When a domain-expert subagent or analyst review pushes back on the bottom-up base, the resolution path is strict:

1. Identify the **specific layer + specific number** the expert disagrees with (e.g., "SP-A mature monetization $8.1B is overstated by ~50%").
2. Present to user: "Expert recommends `<layer>.<field>` go from `<old>` to `<new>`. Reasoning: `<one line>`. Three options: (a) accept revision — layer numbers update, old value disappears; (b) reject — keep current, log rejection reasoning; (c) move into bear mechanism — base stays, but bear absorbs the concern."
3. Apply the user's choice. State must end with one of: revised number, recorded rejection, or strengthened bear. Never all three. Never a parallel scenario.

The handoff.md output never contains both the original number and a "haircut alternative." If the user changes their mind later, they revise the state again — they don't accumulate alternatives.

The discipline reasoning: a TAM with two bases is undefined. Downstream DCF can't choose; the analyst (and the future self) can't remember which number was the "real" base; the bear-bull spread becomes meaningless because the conservative case is already baked into a parallel base. The whole point of the bear/base/bull structure is that the bear absorbs adverse paths — it should not need a haircut overlay.
