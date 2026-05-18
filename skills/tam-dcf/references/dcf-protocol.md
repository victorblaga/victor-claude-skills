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

## Growth-via-Reinvestment Discipline

At every forecast stage:

```
growth ≈ reinvestment rate × ROIC
```

Where:

- **reinvestment rate** = (capex + ΔNWC + R&D-if-capitalized + M&A) / NOPAT, or for unprofitable companies expressed as % of revenue.
- **ROIC** = NOPAT / invested capital (where invested capital = total assets − operating liabilities − cash above operating needs).

Check at every stage. If the forecast shows high growth with low reinvestment, **explicitly justify** — operating leverage, negative working capital, network effects, pricing power. Without justification, fix the forecast.

Persistent ROIC above WACC requires a named moat. Otherwise ROIC fades to WACC across the horizon. Default fade: ROIC matches WACC at maturity unless the user has named a structural moat in the TAM hand-off (asset-backed wedge).

## Mature Economics — When to Apply

Mature margins apply at the layer's / company's maturity year, not at Y10 or Y15. For under-earning or heavily-investing growers:

- **Don't apply mature margins too early.** A company today at 5% EBIT margin doesn't reach 30% by Y3 just because peers are there.
- **Don't assume harvest-mode maximums.** "What if S&M drops to 0%" is not a defensible mature case.
- **Separate maintenance vs growth-oriented S&M and R&D.** Mature S&M = renewals + sector-pace replacement growth. Mature R&D = sustaining + competitive parity. Growth-oriented spend disappears at maturity.
- **Segment if necessary.** If a loss-making initiative (e.g., still-investing speculative TAM layer) is material, separate it from the core for forecast purposes. Two margin paths. Aggregate by revenue weight.

Compare mature margin assumption to:
- Best-in-class current peer margin (peers operating at saturation).
- Historical sector average (10-year median).
- Unit economics (gross margin × operating efficiency × revenue-mix shift).

If the mature assumption sits above best-in-class peer, **name the structural reason** (asset-backed moat, network effect, data flywheel, regulatory protection). Without a reason, push the assumption down to peer average.

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

1. Use GAAP EBIT (which includes SBC) as the starting point for NOPAT.
2. **Do NOT** add SBC back to FCFF as if it were a non-cash adjustment. It's cash-equivalent to the company's existing shareholders.
3. **Do NOT** also reduce per-share value via dilution from SBC-issued shares — that would double-count. The dilution lives in the diluted-share-count denominator.
4. If peer benchmarks use SBC-excluded margins, normalize them to SBC-included before using as anchors.

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

Plus the 10%-required-return case: solve for the FCFF / margin / TAM assumptions that produce a value-per-share matching current price at 10% IRR. Identify what would have to be true.

## Sensitivity Matrices (Mechanics)

Three required matrices, each cell shows `value-per-share / implied unlevered CAGR%`. The IRR in each cell is solved via reverse-DCF for THAT cell's assumption set, not as a linear upside/downside from base.

1. **Primary**: TAM scenario × mature EBIT margin. 3 × 5 grid (TAM bear/base/bull × margin range from peer floor to peer ceiling).
2. **Secondary**: two-Fermi-driver matrix from the TAM hand-off's dominant drivers. E.g., L1 mature share × SP-A monetization for the IOT example. Skip if matrix #1 already captures the uncertainty.
3. **Tertiary**: discount rate × mature growth. Value per share only (discount rate is the return variable). State which discount rate is closest to the market-implied return.

Detail in `sensitivity-matrices.md`.

## Forecast Granularity

- **Y1-Y10**: annual rows.
- **Y11-Y20**: 5-year intervals (Y15, Y20).
- **Y21-maturity**: 5-year intervals to maturity (Y25, Y30, Y35, Y40+).

For each row, the dcf-math subagent computes: revenue (from TAM ramp), revenue growth, EBIT margin, NOPAT, D&A, capex, ΔNWC, FCFF, ROIC, reinvestment rate.

The stacked-S-curve inflections from the TAM hand-off MUST be visible in the revenue-growth column. If the growth column shows a smooth fade where TAM said stacked-S, the dcf-math is wrong — fail the math check.

## What This Skill Does NOT Do

- **Does not rebuild the TAM.** Read it, summarize it, sanity-check it — never relitigate layer-by-layer.
- **Does not output a per-year discounted FCFF ledger.** The dcf-prompt forbids it; the output is structured PV-by-period in the EV bridge.
- **Does not output a "DCF margin of safety" final-value haircut.** Margin of safety lives in scenario design + sensitivity + reverse-DCF required return.
- **Does not adjust the TAM revenue path** to "be more conservative." If the TAM is wrong, the user fixes it via `/tam-analysis resume <TICKER>`.
- **DOES NOT SILENTLY RESCALE TAM CAGRs to fit per-scenario endpoints.** If TAM provides a single CAGR set and three different endpoints, the math forces a rescale that produces shape artifacts (U/W-shapes, mid-cycle reacceleration above early peak). The skill halts at Step 0 and forces the user to fix TAM rather than carry the artifact downstream.

## What This Skill REQUIRES from TAM

The hand-off block (section G of `handoff.md`) must contain:

- Revenue at maturity, today's $ + nominal $, **per scenario** (bear / base / bull)
- **Per-scenario period CAGRs**: bear / base / bull rows, each with Y1-3, Y4-5, Y6-10, Y11-20, Y21-maturity (15 CAGRs total)
- **Per-scenario growth shape** (stacked-S vs smooth fade vs front-loaded vs back-loaded)
- **Per-scenario peak-growth year** (used by shape sanity check)
- **Optional but recommended: per-scenario annual revenue series** for highest-fidelity DCF consumption (no derivation needed)
- **Per-layer ramp schedules**: activation_year, peak_growth_year, maturity_year, curve_shape, per-scenario overrides
- Dominant Fermi drivers (for sensitivity matrix #2)
- Bear mechanism + bull adjacencies
- Per-layer maturity years
- Real pricing CAGR per layer
- Inflation assumption used

If any of these are missing, halt at Step 0 and ask user to re-run TAM with the updated skill. Legacy hand-offs (with a single CAGR set) are not supported; the rescale they'd require is the bug this contract exists to prevent.

## Hand-off Contract Test (Inherited from TAM)

When TAM math-checker emits the hand-off, it runs a contract test: per-scenario CAGRs must compound to per-scenario endpoint within 2%. DCF re-runs this test at Step 0 as a sanity check — if it fails on the DCF side, that means either:

- TAM math-checker has a bug.
- The hand-off was edited after TAM ran.
- The CAGRs and endpoints were never reconciled.

Whatever the cause: HALT. Force user to resolve in TAM before DCF proceeds.
