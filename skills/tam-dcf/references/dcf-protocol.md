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

## WACC Mechanics

```
WACC = (E / (E + D)) × Cost of Equity + (D / (E + D)) × Cost of Debt × (1 − Tax Rate)
```

Anchors:

- **Cost of equity**: 10% unless user specifies otherwise. (This is the "required return" convention — DCFs anchored to a target return rather than CAPM β.)
- **Cost of debt**: current YTM on the company's outstanding bonds, or BBB-rated equivalent + 50-100bps credit spread for the rating. After-tax = pre-tax × (1 − tax rate).
- **Tax rate**: long-run normalized. US default ~25%. Adjust for jurisdiction mix.
- **Capital structure weights**: target weights at maturity, not current. Growers tend toward 70-90% equity at maturity (operating cash flow self-funds). Use TAM-implied maturity-year capital structure if disclosed; otherwise default to current weights.
- **WACC floor**: 8.5%. If calculated WACC < 8.5%, use 8.5% unless user has a specific reason. Show BOTH the calculated and the used WACC in the output.

The floor exists because long-horizon DCFs are sensitive to WACC, and very low discount rates produce intrinsic values that don't survive even modest risk. 8.5% is a defensible floor for long-duration equity claims under any reasonable monetary regime.

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

## What This Skill REQUIRES from TAM

The hand-off block (section G of `handoff.md`) must contain:

- Revenue at maturity, today's $ + nominal $, bear/base/bull
- Period CAGRs (Y1-3, Y4-5, Y6-10, Y11-20, Y21-maturity)
- Growth shape (stacked-S vs smooth fade)
- Dominant Fermi drivers (for sensitivity matrix #2)
- Bear mechanism + bull adjacencies
- Per-layer maturity years
- Real pricing CAGR per layer
- Inflation assumption used

If any of these are missing or malformed, halt at Step 0 and ask user to re-run TAM.
