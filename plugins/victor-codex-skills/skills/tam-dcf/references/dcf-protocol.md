# DCF Protocol

The mechanical and conceptual rules for the FCFF DCF. These are non-negotiable. Skill must obey them; user can override individual numbers but not the structural identities.

## Core Identity

```
FCFF = NOPAT + D&A − Total Capex − ΔNWC
```

Where:

- **NOPAT** = EBIT × (1 − normalized tax rate). EBIT is GAAP EBIT including SBC as a real expense.
- **D&A** = depreciation + amortization. If lease framework is capitalized, includes ROU depreciation.
- **Total Capex** = tangible capex + intangibles capitalized + (if capitalized lease framework) lease capex. Excludes acquisitions unless they are a recurring growth-driver — then include via a separate "M&A reinvestment" line.
- **ΔNWC** = change in working capital. Typically grows with revenue; for negative-working-capital businesses (e.g., subscription with annual prepay), ΔNWC is negative — a source of cash.

The skill computes FCFF this way. No other definition.

## Growth Engine Taxonomy

Different businesses fund growth differently. The DCF forecast must match the company's actual growth mechanics — applying a single one-size identity (`growth ≈ reinvestment_rate × ROIC`) to every business produces phantom reinvestment for opex-funded companies and misses the M&A engine for serial acquirers. See the Known Failure Mode appendix at the end of this file for a canonical example.

The skill classifies the company's growth engine at Step 3 (DCF-side, not TAM) and picks the forecasting identity that matches.

| Engine | Where growth spend lives | Forecast identity | Diagnostic signals | Canonical examples |
|--------|--------------------------|-------------------|--------------------|--------------------|
| **opex_funded** | R&D + S&M expensed in EBIT | Cash-conversion margin: FCFF = revenue × cash_conversion_margin (anchored on actual/guided) | capex < 5% rev, R&D + S&M > 25% rev combined, low/episodic M&A, FCFF margin observable | TYL, NOW, CRM, V, MA, ADBE |
| **capex_funded** | Tangible capex on new units (stores/plants/customers/infra) | Sales-to-capital: net_reinvestment = ΔRevenue / sales_to_capital; FCFF = NOPAT − net_reinvestment | capex > 8% rev, unit-economics-driven, sales-to-capital ratio stable + observable | Dino Polska, Costco in expansion, datacenter operators, freight |
| **acquisition_funded** | M&A deployment from FCF (organic + acquired tracked separately) | Two-track: organic FCFF + M&A deployment; output both `FCFF_pre_M&A` (stop-engine view) and `FCFF_post_M&A` (engine-running view) | M&A deployment > 20% FCF over 3-yr trailing, ongoing roll-up pattern, organic growth modest | CSU, Roper, BRK, Danaher pre-spin |
| **mature_cash_cow** | Maintenance capex only | FCFF = NOPAT − maintenance_capex; FCFF margin anchored on stable observed value | low capex (maintenance only), low/no growth in unit count, growth via brand pricing power | KO, MO, HRMS, mature staples |
| **mixed_engine** | Multiple of above (different segments) | Per-segment: classify each segment with one of the 4 non-mixed types; aggregate FCFF by segment weight | Diversified company with materially different per-segment engines (e.g., AMZN: retail capex + AWS capex + ads opex + Prime loss-leader) | AMZN, META, BRK operating, ASML at segment level |

**Engine type is a forecasting METHOD choice, not a company-inherent property.** Two competent analysts could pick `opex_funded` vs `acquisition_funded` for the same company depending on which growth path they're modeling. The choice lives in DCF, not in TAM hand-off.

**Pricing-power-driven growth** (Hermès, V/MA, ASML) fits `opex_funded` if you squint, or `mature_cash_cow` with high pricing power. No dedicated engine — the cash-reality check (Step 5.5) catches it naturally since these companies have high observed FCFF margins that model output must match.

## Engine-Typed Forecasting Identities

### opex_funded — Cash-Conversion Margin

```
Y1-Y5:    FCFF_y = revenue_y × cash_conversion_margin_y
          cash_conversion_margin_y1 = anchor on max(actual_y0, guided_y1)
          cash_conversion_margin_y2..5 = ramp toward mature value (smooth)

Y6-Y15:   cash_conversion_margin fades from Y5 anchor toward terminal mature value (per scenario)

Terminal: FCFF_(N+1) = NOPAT_(N+1) × (1 − g_real / mature_ROIC)
          (At maturity, growth requires incremental invested capital. ROIC × reinvestment
           identity becomes the terminal anchor.)
```

Where:
- `cash_conversion_margin = (NOPAT + D&A − capex − ΔNWC − capitalized_software) / revenue`. Equivalent to after-SBC FCFF margin.
- Mature `cash_conversion_margin` per scenario set at Step 4 (one of the engine-specific anchors).
- Ramp shape: typically smooth from Y5 anchor to mature value over Y6-Y15. Stay-elevated if TAM scenario implies long durable margin expansion.

**Do not compute reinvestment as `ΔNOPAT / ROIC` during Y1-Y15.** Reinvestment is the residual implied by the margin path (`NOPAT − FCFF`); FCFF margin is the input, reinvestment is the output. ROIC is a downstream consistency check at maturity, not a Y1-Y15 forecast driver.

### capex_funded — Sales-to-Capital

```
For each year Y1..maturity:
  ΔRevenue_y = revenue_y − revenue_(y-1)
  net_reinvestment_y = ΔRevenue_y / sales_to_capital_y
  FCFF_y = NOPAT_y − net_reinvestment_y
  D&A_y modeled separately based on the growing capital base
```

Where:
- `sales_to_capital = revenue / (invested_capital ex_goodwill)`. Anchor on observed Y0 value, fade slowly toward mature value (5-10% degradation typical as scale increases working-capital intensity).
- `invested_capital ex_goodwill` excludes acquired goodwill so the ratio reflects the operating capital base, not historical M&A.
- Mature ROIC reconciles via `NOPAT_mature / invested_capital_mature` — used as terminal-stage consistency check.

For unit-driven companies (Dino Polska, Costco), an alternative parameterization is `revenue_per_unit × unit_count` with explicit `capex_per_new_unit`. Equivalent to sales-to-capital when expressed via the identity `sales_to_capital ≡ revenue / (capex_per_unit × cumulative_units_built)`.

### acquisition_funded — Acquisition Track

Two tracks, modeled independently, then combined.

**Organic track:**
```
For each year:
  revenue_organic_y = revenue_organic_(y-1) × (1 + organic_growth_y)
  FCFF_organic_y = revenue_organic_y × organic_fcff_margin_y
```

**M&A track:**
```
For each year:
  M_A_spend_y = FCFF_organic_y × m_a_deployment_pct_fcf_y
  acquired_revenue_y = M_A_spend_y × roic_acquired_y / steady_state_acquired_fcff_margin_y
    (Acquired revenue back-solves from the price paid divided by the prevailing acquired-business
     multiple — a function of ROIC_acquired and the steady-state FCFF margin of acquired businesses.)
  cumulative_acquired_revenue_y = cumulative_acquired_revenue_(y-1) + acquired_revenue_y
  revenue_total_y = revenue_organic_y + cumulative_acquired_revenue_y
```

**Combined:**
```
FCFF_pre_M&A_y  = FCFF_organic_y + cumulative_acquired_FCFF_y   (the "stop-the-engine" view)
FCFF_post_M&A_y = FCFF_pre_M&A_y − M_A_spend_y                  (deployed for growth)
```

**Output both.** `FCFF_pre_M&A` is what shareholders see if the engine stops (FCF returned as buybacks/dividends). `FCFF_post_M&A` is what shareholders see while the engine runs (cash deployed for inorganic growth). Both views surface in `dcf.md` Section 5; the reverse DCF runs on `FCFF_post_M&A` since that's the cash actually distributable during engine-running.

Mature stage: M&A pace fades. Typical assumption: M&A deployment % drops from current pace (e.g., 85% of FCF for CSU) to a terminal pace (e.g., 30% of FCF) by maturity. Beyond maturity, treat M&A as part of normal reinvestment via the standard ROIC × reinvestment identity.

### mature_cash_cow — Maintenance FCFF Margin

```
For each year:
  FCFF_y = revenue_y × maintenance_fcff_margin_y
  
maintenance_fcff_margin = (NOPAT − maintenance_capex) / revenue
```

Where:
- `maintenance_capex` anchored on 3-yr avg of (capex − any growth-attributable capex). For companies with disclosed maintenance vs growth capex split, use the disclosed split.
- `growth_via_pricing_power = true` if the company grows via brand-pricing CAGR above inflation rather than unit count (Hermès, KO international, V/MA take-rate creep). Revenue growth = pricing power CAGR; volume flat-to-modest. FCFF margin stays high because there's no incremental capital base to grow.

Special case of `opex_funded` with `cash_conversion_margin ≈ maintenance_fcff_margin` and zero growth-oriented spend. Treat separately when the company is far enough into maturity that no growth investment is plausible.

### mixed_engine — Per-Segment Aggregation

For diversified companies with materially different per-segment engines:

1. Classify each reporting segment with one of the 4 non-mixed engines (or sub-segment further if needed).
2. Forecast each segment using its engine's identity above.
3. Aggregate at the corporate level: `FCFF_corp_y = Σ FCFF_segment_y − corporate_overhead_y`.
4. Mature segment weights set at Step 4 per scenario (the TAM hand-off already provides revenue at maturity per layer; map layers to segments).

When segments aren't disclosed at this granularity, the user has options:
- (a) Group segments into 2-3 "super-segments" by dominant engine and proceed.
- (b) Pick the dominant engine and treat the whole company as that engine; surface the simplification in the cash-reality check (the check will halt if the simplification is too aggressive).
- (c) Halt: state the company can't be modeled in this skill until segment-level data is available.

## Terminal-Stage ROIC Consistency Check

At maturity year `N`, real growth slows to long-run (typically 0-1% real). At that point, growth requires incremental invested capital regardless of historical engine, so the identity:

```
growth_mature ≈ reinvestment_rate_mature × ROIC_mature
```

becomes the terminal-stage anchor. This identity **DOES NOT** apply during Y1-Y15 for opex_funded or acquisition_funded engines (it would produce phantom reinvestment when growth lives in opex or M&A). It applies only at maturity.

**Symmetric discipline rule.** Check both directions at terminal:

- If the forecast shows **high mature growth with low mature reinvestment**, justify explicitly: durable operating leverage, persistent negative working capital, network effects compounding, regulatory pricing power. Without justification, fix the forecast.
- If the forecast shows **modest mature growth with implausibly high mature reinvestment** (`rate × ROIC ≫ growth`), the model is suppressing FCFF. Check for: misuse of average ROIC where incremental ROIC is intended; double-counting of growth spend already in opex; reinvestment driver that ignores capital efficiency. This direction is historically under-checked.

Both failure modes show up as reverse-DCF IRR distortions. The Y1-Y10 cash-reality check (Step 8) catches the second pattern early. The terminal check catches it at convergence.

**Persistent ROIC above WACC requires a named moat.** Otherwise ROIC fades to WACC across the horizon. Default fade: ROIC matches WACC at maturity unless the user has named a structural moat in the TAM hand-off (asset-backed wedge).

## Mature Economics — When to Apply

The mature-economics anchor set is **engine-conditional** per the taxonomy above. Step 4 in `SKILL.md` walks the per-anchor confirmation using the right anchor names for the chosen engine:

| Engine | Mature anchors (per scenario, all 5) |
|--------|--------------------------------------|
| opex_funded | `cash_conversion_margin_mature`, `mature_EBIT_margin` (cross-check), `mature_ROIC` (terminal-only consistency) |
| capex_funded | `sales_to_capital_mature`, `mature_EBIT_margin`, `mature_ROIC` |
| acquisition_funded | `organic_fcff_margin_mature`, `roic_acquired_mature`, `m_a_deployment_pct_fcf_mature`, `organic_mature_growth` |
| mature_cash_cow | `maintenance_fcff_margin`, `maintenance_capex_pct_rev` |
| mixed_engine | per-segment, using each segment's engine anchors |

Mature `mature_EBIT_margin` remains a useful cross-check for opex_funded and capex_funded (it's the GAAP-equivalent of cash-conversion / sales-to-capital outputs). For acquisition_funded and mature_cash_cow, EBIT margin is informational only.

Mature margins apply at the layer's / company's maturity year, not at Y10 or Y15. For under-earning or heavily-investing growers:

- **Don't apply mature margins too early.** A company today at 5% EBIT margin doesn't reach 30% by Y3 just because peers are there.
- **Don't assume harvest-mode maximums.** "What if S&M drops to 0%" is not a defensible mature case.
- **Separate maintenance vs growth-oriented S&M and R&D.** Mature S&M = renewals + sector-pace replacement growth. Mature R&D = sustaining + competitive parity. Growth-oriented spend disappears at maturity.
- **Segment if necessary.** If a loss-making initiative (e.g., still-investing speculative TAM layer) is material, separate it from the core for forecast purposes. Two margin paths. Aggregate by revenue weight.

Compare mature margin assumption to:
- Best-in-class current peer margin (peers operating at saturation).
- Historical sector average (10-year median).
- Unit economics (gross margin × operating efficiency × revenue-mix shift).

**Comparisons use the same accounting basis on both sides.** See `SKILL.md` Step 2 — Reported-to-Economic Bridge. Peer benchmarks must be normalized for pass-through revenue, SBC vintage (run-rate only), and strategic-segment reclassification before they can anchor the target's mature-margin assumption. The dispatch payload to anchor-researcher carries the normalization spec from `economic_bridge.margin_side.peer_normalization_spec`.

If the mature assumption sits above best-in-class peer (normalized basis), **name the structural reason** (asset-backed moat, network effect, data flywheel, regulatory protection). Without a reason, push the assumption down to peer average.

## WACC Mechanics — Required-Return Framework

WACC is framed as **required return**, not derived from CAPM. The conventional `r_e = r_f + β × ERP` produces a falsely precise number from noisy backward-looking statistics. This skill replaces that with a transparent additive composition over preferences the user actually controls:

```
WACC ≈ required_real_return + reporting_currency_inflation + jurisdictional_risk_premium + sector_nudge
```

Then blend with cost of debt only if material:

```
WACC_final = (E / (E + D)) × required_return_composed + (D / (E + D)) × cost_of_debt_after_tax
```

For mostly-equity-financed growers (90%+ equity weight), `WACC_final ≈ required_return_composed`. Don't sweat the debt blending unless capital structure is material.

### Component 1 — Required Real Return

What you want to earn **after inflation**. Default 8%. Conservative buy-and-hold investors anchor 6-7%; aggressive growth investors anchor 9-10%. Floor 6% (below that it's a savings account, not equity risk-taking).

### Component 2 — Reporting Currency Inflation

| Currency | Long-run anchor | Source |
|----------|-----------------|--------|
| USD / EUR / GBP / CAD / AUD / SGD | 2% | Central-bank targets, well-anchored |
| CHF | 1% | SNB target |
| JPY | 1-2% | BoJ target |
| PLN / CZK / ILS | 3% | Stable EM |
| MXN | 4% | Banxico target 3%, realized ~4-5% |
| RON / HUF | 5% | Mid-tier EM, persistent above-target |
| BRL / ZAR / INR | 5-7% | Mid-tier EM |
| TRY (current) / ARS / EGP | 15%+ | Fragile EM, anchor on realized |

Use central-bank target where credible; 10-year realized average where it isn't.

### Component 3 — Jurisdictional Risk Premium

| Jurisdiction tier | Examples | Premium |
|-------------------|----------|---------|
| Developed markets | US, UK, EU-core, JP, CH, CA, AU, SG, KR | 0% |
| Stable EMs | MX, PL, CZ, IL, TW, CL | 1-2% |
| Mid-tier EMs | RO, BR, IN, ID, ZA, MY, TH | 2-4% |
| Fragile EMs / political risk | TR, EG, AR, NG, VN | 4-6% |
| Distressed / sanctioned | RU, IR, VE, MM | 6%+ or uninvestable |

Apply once at the listing-jurisdiction level. For multi-jurisdiction businesses (e.g., US-listed but 80% of revenue from Mexico + India), nudge up 1-2% to reflect operating exposure.

### Component 4 — Sector / Business-Quality Nudge (Optional)

- Regulated infrastructure / staples / utilities: -0.5% to -1%
- Quality compounders with proven track record: -0.5%
- High-growth unprofitable tech: +0.5% to +1%
- Cyclical commodity / shipping / semis: +1% to +2%
- Speculative biotech / pre-revenue: +2% to +3%
- Micro-cap (< $500M): +0.5% to +1%

Don't stack adjustments aggressively. ±3% from base of 10% is a sign of motivated reasoning — push back on the assumption set rather than the discount rate.

### Floor

**8.5% USD-equivalent floor** unless exceptionally justified. The floor exists because long-horizon DCFs are sensitive to WACC; very low discount rates produce intrinsic values that don't survive modest risk.

For non-USD reporting currencies: `floor_local = 8.5% + (currency_inflation − 2%)` to preserve the real-return basis. E.g., RON-listed floor = 8.5% + 3% = 11.5%; BRL-listed floor ≈ 12.5%.

Show BOTH the composed WACC and the used WACC in `dcf.md` if the floor is invoked.

### Reference Compositions

| Setup | Composition | WACC |
|-------|-------------|------|
| USD-listed quality compounder, US ops | 8% + 2% + 0% − 0.5% | 9.5% |
| USD-listed durable growth, US ops | 8% + 2% + 0% + 0% | 10% (default) |
| USD-listed speculative growth | 8% + 2% + 0% + 1% | 11% |
| USD-listed, 80% EM operations | 8% + 2% + 2% + 0% | 12% |
| EUR-listed European compounder | 8% + 2% + 0% − 0.5% | 9.5% |
| GBP-listed UK staples | 8% + 2% + 0% − 1% | 9% |
| MXN-listed Mexican retailer | 8% + 4% + 1% + 0% | 13% |
| RON-listed Romanian growth | 8% + 5% + 2% + 0% | 15% |
| BRL-listed Brazilian compounder | 8% + 6% + 3% − 0.5% | 16.5% |
| INR-listed Indian SaaS | 8% + 5% + 3% + 0% | 16% |
| TRY-listed (current) | 8% + 18% + 5% + 0% | 31% (heavily inflation-dominated) |

### Cost of Debt

Only material if D/(E+D) > 20%. For mostly-equity-financed growers, skip the blending — `WACC_final = required_return_composed`.

When material:
- Cost of debt = current YTM on the company's outstanding bonds, OR
- Investment-grade equivalent (BBB) yield + 50-150bps credit spread for the rating
- After-tax = pre-tax × (1 − tax rate)

### Tax Rate

Long-run normalized:
- US: ~25% (Federal 21% + state-adjusted)
- EU-core (FR, DE, IT): 25-30%
- UK: 25%
- Ireland: 12.5%
- Singapore: 17%
- EMs: country-specific (BR ~34%, IN ~25%, MX ~30%)

### Capital Structure Weights

Target weights at maturity, not current. Most growers tend toward 70-90% equity at maturity (operating cash flow self-funds). Use TAM-implied maturity-year capital structure if disclosed; otherwise default to current weights and explicit-forecast convergence.

### What This Framework Replaces

The skill explicitly does NOT compute or use:

- **Beta** (Cov / Var regression on historical returns).
- **Risk-free rate from current Treasury yields** (snapshot of the wrong-duration rate).
- **Equity risk premium** as a multiplicative input to beta.
- **CAPM-derived cost of equity** as the primary build.
- **Damodaran-style country-risk-premium tables derived from CDS spreads.** (The jurisdictional premium here is preference-based, transparent, and anchored on the user's tolerance — not a derivation from credit markets.)

This is a deliberate choice. CAPM produces a precise-looking number from inputs that are themselves noisy and contested. The required-return framework is honest about the fact that the discount rate is fundamentally a preference, then adjusts it for the real-world frictions (inflation, jurisdiction, sector risk) that the user can actually reason about.

## Lease Framework — Pick ONE

| Framework | Lease payments | Lease liabilities | ROU depreciation | Lease capex | WACC weights |
|-----------|----------------|-------------------|------------------|-------------|--------------|
| **Operating-cost** | In opex (rent line) | Excluded from EV bridge + capital | Not separated | Not separated | Equity + financial debt only |
| **Capitalized** | Separated: interest in interest expense, principal in financing CF | In EV bridge as debt-like; in capital base | In D&A | In total capex | Equity + financial debt + lease liabilities |

**Do not mix.** Picking both will silently double-count or under-count lease economics. The skill commits to one framework at Step 4 and applies it consistently.

Default: capitalized approach for companies with material lease portfolios (retailers, restaurants, transports, datacenter operators). Operating-cost approach for asset-light businesses where leases are small.

## SBC Treatment

**SBC is a real economic expense.** Companies that present "adjusted EBITDA ex-SBC" or "non-GAAP operating income" are obscuring the cost of stock dilution to existing shareholders. The DCF treats SBC as opex.

Concretely:

1. Use GAAP EBIT (which includes SBC) as the starting point for NOPAT. **For mature-margin assumption purposes, use run-rate SBC, not a sum that includes one-time vintage extrapolated as recurring** — see `SKILL.md` Step 2 for the vintage breakdown (`economic_bridge.margin_side.sbc_breakdown.run_rate_sbc_pct_rev` separates run-rate from one-time mega-grants tied to long-dated hurdles).
2. **Do NOT** add SBC back to FCFF as if it were a non-cash adjustment. It's cash-equivalent to the company's existing shareholders.
3. **Do NOT** also reduce per-share value via dilution from SBC-issued shares — that would double-count. The dilution lives in the diluted-share-count denominator. One-time hurdle-vested grants are handled separately as contingent expected-value dilution at vesting conditions (probability-weighted), not as run-rate.
4. If peer benchmarks use SBC-excluded margins, normalize them to SBC-included before using as anchors. If peers have their own one-time vintages, strip those too — peer comparisons run on run-rate-SBC basis for both sides.

The skill computes this way. If the user wants an SBC-adjusted view as a sanity check, that's a footnote, not the primary calculation.

## Diluted Share Count

For per-share value:

- Use current diluted shares outstanding from the latest filing.
- Add economically relevant dilutive instruments NOT already in diluted count: in-the-money options (treasury method), RSUs expected to vest over the next ~3 years, convertibles at conversion.
- For long-horizon DCFs (40+ years), also model the **trajectory** of share count: continued SBC issuance vs buybacks. The buyback assumption is itself a DCF input — capital return to shareholders, distinct from FCFF generation.

## Terminal Value

At maturity year `N`:

```
Terminal Value = FCFF_(N+1) / (WACC − g)
```

Where `g` = long-run nominal growth rate at maturity = real terminal growth + inflation. Real terminal growth is typically 0-1% for mature businesses; the long-run real GDP growth rate (~2% for advanced economies) is the absolute upper bound.

Cross-check: `g < WACC` (mathematical requirement). And:

```
g = mature reinvestment rate × mature ROIC
```

Both must reconcile to the chosen `g`. If they don't, fix the assumption that's wrong — usually the reinvestment rate.

Flag if PV of terminal value > 50% of EV. This indicates the valuation depends heavily on assumptions about a year ~40 years out. Not invalid, but high-uncertainty — surface to user.

## Reverse DCF

For each scenario (bear / low / base / high / bull):

```
Solve for r:  Current EV = Σ FCFF_t / (1 + r)^t + Terminal Value_N / (1 + r)^N
```

`r` is the **implied unlevered enterprise discount rate** that reconciles the current market EV with the scenario's projected FCFF stream + terminal value. This is NOT a levered equity IRR.

**Engine discipline**: the FCFF stream the reverse DCF solves against depends on the engine:
- `opex_funded`, `capex_funded`, `mature_cash_cow`, `mixed_engine`: standard total FCFF stream.
- `acquisition_funded`: runs on `FCFF_post_M&A` (cash distributable during engine-running phase, after M&A deployment). The `FCFF_pre_M&A` view ("stop-the-engine") is shown alongside in Section 5 but is NOT the reverse-DCF basis — it would over-state cash that's actually being deployed for growth.

**Basis discipline**: reverse DCF runs on **economic** revenue + **economic** margin basis. If the TAM hand-off carries `revenue_basis: economic_adjusted` and/or Step 2 produced margin-side adjustments, the FCFF stream the reverse DCF solves against is the economic stream — same Y0 anchor, same per-scenario CAGRs applied to economic revenue, same economic mature margin. The implied IRR shown is the rate that reconciles current EV with the **economic** FCFF stream. The screener's reported-basis multiples (Section 10 dual-basis block) will tell a different story when economic ≠ reported — that's the point of carrying both views.

Plus the 10%-required-return case: solve for the FCFF / margin / TAM assumptions that produce a value-per-share matching current price at 10% IRR. Identify what would have to be true.

## Sensitivity Matrices (Mechanics)

Three required matrices, each cell shows `value-per-share / implied unlevered CAGR%`. The IRR in each cell is solved via reverse-DCF for THAT cell's assumption set, not as a linear upside/downside from base.

1. **Primary**: TAM scenario × mature EBIT margin. 5 × N grid (TAM bear/low/base/high/bull × margin range from peer floor to peer ceiling).
2. **Secondary**: two-Fermi-driver matrix from the TAM hand-off's dominant drivers. E.g., L1 mature share × SP-A monetization for the IOT example. Skip if matrix #1 already captures the uncertainty.
3. **Tertiary**: discount rate × mature growth. Value per share only (discount rate is the return variable). State which discount rate is closest to the market-implied return.

Detail in `sensitivity-matrices.md`.

## Forecast Granularity

- **Y1-Y10**: annual rows.
- **Y11-Y20**: 5-year intervals (Y15, Y20).
- **Y21-maturity**: 5-year intervals to maturity (Y25, Y30, Y35, Y40+).

For each row, the dcf-math subagent computes: revenue (from TAM ramp), revenue growth, EBIT margin, NOPAT, D&A, capex, ΔNWC, FCFF, ROIC, reinvestment rate.

The per-scenario growth path declared in the TAM hand-off (period CAGRs + growth shape label per scenario) MUST be visible in the revenue-growth column. If the TAM hand-off declares a `stay-elevated` shape and the DCF growth column shows a smooth fade, dcf-math has applied the wrong revenue path — fail the math check. Conversely, if TAM declares `smooth-fade` and the DCF growth column shows mid-cycle elevation, also fail.

## Cash-Reality Reconciliation Discipline

After dcf-math generates the Y1-Y10 annual forecast at Step 7, the skill runs the **cash-reality reconciliation** at Step 8 before any output is emitted. The check compares modeled per-scenario FCFF margins against a "comparable" anchored on observed and guided actuals.

**The comparable** (the bar):

```
fy_actual_after_sbc_fcf_margin = (operating_cash_flow_y0 − capex_y0 − capitalized_software_y0 − sbc_y0) / revenue_y0
ny_guided_after_sbc_fcf_margin = mgmt_guided_fcf_margin_y1 − projected_sbc_margin_y1
tighter_bar = min_by_distance(fy_actual, ny_guided)   (the one closer to modeled Y1 across all scenarios — keeps the test honest)
```

When management doesn't explicitly guide FCFF margin (most don't — they guide capex % rev + OCF growth), the back-solve recipe is:

```
ny_guided_after_sbc_fcf_margin ≈ (guided_OCF_y1 − guided_capex_y1 − projected_capitalized_software_y1 − projected_sbc_y1) / guided_revenue_y1
```

All four components are typically disclosed in management's Y1 guidance package. The anchor-researcher dispatches at Step 8 fetch them. If a component is missing, log as "back-solve incomplete" and proceed with the actual (FY) anchor only.

**The check (per scenario, all 5):**

```
delta_y1_bp = (modeled_fcff_margin_y1 − tighter_bar) × 10000
delta_y2_y3_bp = (avg(modeled_fcff_margin_y2_y3) − tighter_bar) × 10000

HALT if |delta_y1_bp| > 500 without logged mechanism
HALT if |delta_y2_y3_bp| > 1000 without logged mechanism
```

**Resolution path (on HALT):**

The user has three options for each halting scenario:

1. **Revise assumptions.** Pull mature margins or ramp shape to close the gap. Re-dispatch dcf-math.
2. **Name the mechanism.** Logged in `cash_reality_check.override.{scenario}.mechanism` + `sources.md`. Example: "Bear scenario assumes large customer churn in FY2026 cutting FCF margin temporarily; trajectory rejoins peers by Y3." Free-text but must be specific.
3. **Halt the DCF.** User reconsiders the engine framing or revises in TAM.

**Engine-agnosticism.** The check compares modeled FCFF margin to observed/guided FCFF margin. Independent of which `forecast_method` generated the model. Works equally for:
- opex_funded: modeled `cash_conversion_margin` directly compared.
- capex_funded: modeled (NOPAT − reinvestment) / revenue compared.
- acquisition_funded: modeled `FCFF_post_M&A` / revenue compared (since post-deployment is what shareholders receive).
- mature_cash_cow: modeled `maintenance_fcff_margin` directly compared.
- mixed_engine: corporate-level aggregated FCFF margin compared.

The check catches assumption sets that look internally coherent but produce Y1-Y3 cash flows inconsistent with observed/guided reality. The terminal-stage check (modest growth + implausibly high reinvestment) catches the same class of failure at convergence. See the Known Failure Mode appendix for the canonical instance.

## What This Skill Does NOT Do

- **Does not rebuild the TAM.** Read it, summarize it, sanity-check it — never relitigate layer-by-layer.
- **Does not output a per-year discounted FCFF ledger.** The dcf-prompt forbids it; the output is structured PV-by-period in the EV bridge.
- **Does not output a "DCF margin of safety" final-value haircut.** Margin of safety lives in scenario design + sensitivity + reverse-DCF required return.
- **Does not adjust the TAM revenue path** to "be more conservative." If the TAM is wrong, the user fixes it via `/tam-analysis resume <TICKER>`.
- **DOES NOT SILENTLY RESCALE TAM CAGRs to fit per-scenario endpoints.** Per-scenario CAGRs and per-scenario endpoints are both first-class hand-off inputs; any reconciliation discrepancy halts at Step 0 and is resolved in TAM, not silently absorbed.
- **Does not generate a per-layer revenue ramp.** Neither this skill nor the TAM skill generates per-layer annual revenue. The growth path is declared per scenario in TAM (period CAGRs anchored on guidance + thesis), validated by `layer_schedule_consistency_test` against the layer activation schedule, and consumed here directly.
- **Does not apply `growth ≈ reinvestment_rate × ROIC` during Y1-Y15 for opex_funded or acquisition_funded engines.** This identity is a terminal-stage anchor only — applying it as a forecast generator during the ramp produces phantom reinvestment for businesses where growth lives in opex (R&D, S&M) or in M&A deployment. Engine-typed forecasting identities replace the universal identity during Y1-Y15. See Known Failure Mode appendix.
- **Does not classify engine in TAM.** Engine type is a forecasting METHOD choice, lives in DCF only. TAM hand-off stays clean of DCF-specific concepts — different engine choices produce different DCFs from the same TAM, no TAM re-run required.

## What This Skill REQUIRES from TAM

The hand-off block (section G of `handoff.md`) must contain:

- Revenue at maturity, today's $ + nominal $, **per scenario** (bear / low / base / high / bull)
- **Last reported revenue (Y0, today's $)** and **last reported YoY growth** (anchors the derived annual series interpolation)
- **`revenue_basis`** field (`reported` | `economic_adjusted`) and bridge summary from TAM Step 1. All revenue figures in the hand-off are on the stated basis. DCF margin assumptions must be anchored on the matching basis (Step 2 + Step 4 peer normalization handle this)
- **Per-scenario period CAGRs**: bear / low / base / high / bull rows, each with Y1-3, Y4-5, Y6-10, Y11-20, Y21-maturity (25 CAGRs total)
- **Y1-3 guidance anchor**: management guidance midpoint + range, consensus analyst midpoint
- **Per-scenario growth shape** (stay-elevated / smooth-fade / front-loaded / back-loaded)
- **Per-scenario peak-growth year** (used by sanity checks)
- **Per-scenario derived annual revenue series** (preferred consumption form; regenerable from the CAGRs via linear interp in growth-rate space)
- **Per-layer activation schedule**: activation_year, peak_contribution_year, maturity_year (drives the layer-schedule consistency check; not a revenue-path generator)
- **Layer-schedule consistency test results** per scenario (must be passed)
- **Scenario monotonicity test result** (bear < low < base < high < bull, must be passed)
- Dominant Fermi drivers (for sensitivity matrix #2)
- Bear mechanism + low/high partial materializations + bull adjacencies
- Per-layer maturity years
- Real pricing CAGR per layer
- Inflation assumption used

If any of these are missing, halt at Step 0 and ask user to re-run TAM.

## Hand-off Contract Test (Inherited from TAM)

When TAM math-checker emits the hand-off, it runs a contract test: per-scenario CAGRs must compound to per-scenario endpoint within 2%. DCF re-runs this test at Step 0 as a sanity check — if it fails on the DCF side, that means either:

- TAM math-checker has a bug.
- The hand-off was edited after TAM ran.
- The CAGRs and endpoints were never reconciled.

Whatever the cause: HALT. Force user to resolve in TAM before DCF proceeds.

## Known Failure Mode — TYL DCF Bug (Canonical Case)

The growth-engine taxonomy, the cash-reality check, and the implied-multiple sanity flag all exist because of one specific failure: an opex-funded vertical-SaaS DCF that applied a sales-to-capital reinvestment identity meant for capex-funded businesses. The misclassification produced an internally-consistent but externally-broken forecast.

Symptoms of that run:

- Modeled Y1 net reinvestment $429M vs Y1 NOPAT $324M — a reinvestment rate of 132% of NOPAT, only possible with external capital, none of which was named.
- Modeled Y1 FCFF margin around −4% versus latest-FY actual / management-guided FCFF margin around +20% — a 2400bp gap with no mechanism behind it.
- Section 10 printed `Current EV/FY27 FCFF: -111.8×` and `base intrinsic EV/FY27 FCFF: -54.9×` — negative implied multiples on a cash-generative company.

The root cause was a single bad identity choice: `net_reinvestment = ΔNOPAT / ROIC` applied during Y1-Y15. That identity is a *terminal-stage* anchor (`growth ≈ reinvestment_rate × ROIC`) when growth requires incremental invested capital. During the ramp years for an opex-funded business, growth lives in R&D + S&M expense already inside EBIT — applying the identity adds a phantom capital outflow on top.

The fix is structural, not numerical:

1. Engine classification at Step 3 picks `opex_funded`, `capex_funded`, `acquisition_funded`, `mature_cash_cow`, or `mixed_engine` per the diagnostic signals — engine-specific anchors and forecasting identity flow from that choice.
2. Y1-Y15 reinvestment for opex-funded engines is the *residual* (`NOPAT − FCFF` from the modeled FCFF margin path), not derived from `ΔNOPAT / ROIC`.
3. Step 8 cash-reality reconciliation halts when modeled Y1 FCFF margin diverges from actual/guided by >500bp without a logged mechanism, catching the failure at forecast-generation time.
4. Sanity check #5 (Y1-Y10 plausibility) FAILs when modeled reinvestment exceeds NOPAT in any year without an explicit external-capital raise.
5. Section 10 negative-multiple warning catches the symptom at output-emission time.

The numerical specifics — $429M, $469M, +20.1%, −4%, −111.8× — are useful as a calibration anchor for what "broken" looks like. They are not the failure pattern in general; the failure pattern is: confident-but-wrong default behavior when a textbook DCF identity is applied outside its valid range. Any future failure with the same shape (modeled cash flow disconnected from observed cash flow + impossible reinvestment rate + negative implied multiples) is the same class.
