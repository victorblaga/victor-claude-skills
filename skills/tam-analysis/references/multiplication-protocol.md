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

## Growth Path Shape (Feeds DCF)

After aggregation, derive the period-by-period CAGRs for the hand-off block:

| Period | CAGR meaning |
|--------|--------------|
| Y1-3 | Near-term ramp; should reconcile to consensus / guidance. Discrepancies flagged. |
| Y4-5 | First adjacency starting to contribute |
| Y6-10 | Multi-layer compounding peak |
| Y11-20 | Layered maturity unfolds — different layers saturate at different times |
| Y21-maturity | Speculative layers finishing their ramp; core layers in pricing-only growth |

If the layer thesis is stacked S-curves (sequential: core saturates → adjacent compounds → international → speculative), the growth path stays elevated longer than a smooth geometric fade. Surface this explicitly to the user.

Math-checker validates the period CAGRs against the aggregated revenue path.

## Three-Error Check (Run Before Hand-Off)

1. **Did we pass the Fermi output through as actual revenue at maturity, or silently haircut?** Compare summary numbers to the aggregated layer table. They must match.
2. **Did we account for real pricing AND inflation separately?** Check `state.json` — both fields populated per layer, neither one folded into the other.
3. **Does the growth path reflect stacked S-curves matching the layer thesis, or did we force a smooth fade?** Plot or tabulate the per-year revenue from the aggregated layers. If it's smooth where the thesis is layered, the math is wrong.

Math-checker runs all three. Any failure must be surfaced to user and resolved before emitting the hand-off block.
