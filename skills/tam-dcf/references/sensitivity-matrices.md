# Sensitivity Matrices

Three required matrices. Each cell shows **value-per-share / implied unlevered CAGR%**. The CAGR is solved via reverse-DCF for that cell's assumption set — NOT linear upside/downside from base.

The matrices are the most-used part of the output. They get rendered as heatmaps in `dcf.html`. Treat them as first-class deliverables, not appendices.

## Matrix 1 — TAM Scenario × Mature EBIT Margin (PRIMARY)

The most important matrix. Captures the dominant uncertainty: where does revenue land (TAM bear/low/base/high/bull) × how much profit does it produce (mature margin range).

### Spec

- **Rows**: 5 — TAM bear / low / base / high / bull (from `handoff.md`).
- **Columns**: 5 — mature EBIT margin from peer floor to peer ceiling. Default: `floor−2%`, `floor`, `midpoint`, `ceiling`, `ceiling+2%`. Adjust to the sector's realistic range.
- **Cells**: value-per-share / implied unlevered CAGR% solved via reverse DCF (5 × 5 = 25 reverse-DCF solves).

### Example (illustrative)

```
                        15% margin   18% margin   22% margin   26% margin   30% margin
TAM bear ($5B Y25)      $X / Y%      $X / Y%      $X / Y%      $X / Y%      $X / Y%
TAM low ($8B Y25)       $X / Y%      $X / Y%      $X / Y%      $X / Y%      $X / Y%
TAM base ($14B Y25)     $X / Y%      $X / Y%      $X / Y%      $X / Y%      $X / Y%
TAM high ($22B Y25)     $X / Y%      $X / Y%      $X / Y%      $X / Y%      $X / Y%
TAM bull ($36B Y25)     $X / Y%      $X / Y%      $X / Y%      $X / Y%      $X / Y%
```

Current price: $X. Current EV: $Y. Color-code cells in the HTML by IRR:

- Red: IRR < 6% (below long-bond + risk premium baseline)
- Yellow: 6-10% (below conventional required return)
- Green: 10-15% (meets / exceeds required return)
- Dark green: > 15% (high-margin compounder territory)

### After the matrix, the report MUST surface

- Which combinations clear 10%.
- Which combinations sit below 6% (price destruction).
- What assumption set the current price requires.
- How much disruption (down-shift in TAM or margin) the current price tolerates before falling below 6%.

## Matrix 2 — Two-Fermi-Driver Matrix (FROM TAM HAND-OFF)

Built from the dominant Fermi drivers flagged in the TAM hand-off block. Examples:

- For Amazon: L1 mature share × adjacent-category penetration.
- For Samsara: L1 mature share × SP-A monetization.
- For a payments network: take rate × volume CAGR.
- For a marketplace: GMV growth × take rate.

### Spec

- **Rows**: 5 — first dominant driver, range from bear-of-bear to bull-of-bull.
- **Columns**: 5 — second dominant driver, same range.
- **Cells**: value-per-share / implied unlevered CAGR%, with margin held at base case and all other assumptions held constant.

### Skip rule

If Matrix 1 already captures the uncertainty (e.g., the dominant drivers are essentially the TAM scenario itself), skip Matrix 2. Don't manufacture a duplicate sensitivity. Note in the output: "Matrix 2 omitted — TAM scenario matrix captures the dominant uncertainty."

## Matrix 3 — Discount Rate × Mature Real Growth (TERTIARY)

Pure sanity check. The discount rate is itself the return variable, so cells show **value-per-share only** (not implied IRR — that would be circular).

### Spec

- **Rows**: 5 — discount rates from `WACC floor − 1%` to `WACC base + 3%`. E.g., 7.5%, 8.5%, 9.5%, 10.5%, 12%.
- **Columns**: 4 — mature real growth from 0% to 2.5% (nominal terminal growth = real + inflation).
- **Cells**: value-per-share, base case for everything else.

### Surface in the report

- Which discount rate row is closest to the market-implied return (from the reverse DCF).
- Which mature real growth column is consistent with the TAM hand-off's terminal-year characterization.
- How sensitive the valuation is to the residual / terminal value (high sensitivity = high residual share of EV).

## Reverse DCF Mechanics (Per-Scenario)

For each named scenario (bear / low / base / high / bull) and for the 10%-required-return case:

```
Current EV = Σ FCFF_t / (1 + r)^t + Terminal Value_N / (1 + r)^N
```

Solve for `r`. Use Python's `scipy.optimize.brentq` or similar. The solver returns the **implied unlevered enterprise discount rate** — NOT a levered equity IRR. (Many analysts confuse the two; the skill is strict.)

### What to report

For each scenario:

- The scenario's headline assumption set (TAM scenario + margin + reinvestment + WACC).
- The implied `r`.
- Verdict: does this beat the 10% required return?

For the 10%-clearing case:

- What TAM / margin / adjacency assumptions are required for the unlevered IRR to exactly clear 10% at today's price.
- Are those assumptions inside the TAM bear/low/base/high/bull spread, or beyond it?

The 10%-clearing case is the most analytically useful number in the whole DCF for an investment decision. Make it prominent in the compact conclusion.

## What NOT to Do

- **Don't compute IRR as linear upside/downside from base.** Each cell is its own reverse-DCF — different revenue path, different FCFF stream, different terminal value, different `r`. Linear approximation is wrong by 1-3% IRR in long-horizon DCFs.
- **Don't omit the IRR column in Matrix 1.** Value-per-share without IRR is decision-poor — the user can't tell which cells are investable.
- **Don't manufacture a Matrix 2 when Matrix 1 captures the variance.** Output discipline. Note the omission instead.
- **Don't apply a final-value haircut "for safety."** Margin of safety = scenario choice + sensitivity range + required-return threshold. Not a post-hoc reduction.

## HTML Rendering Notes

The HTML output renders matrices as interactive heatmaps:

- Click a cell → expanded card showing: the full assumption set, the FCFF path summary, the reverse-DCF computation, the implied multiples.
- Hover a cell → tooltip with the assumption deltas vs base.
- Color scale per the IRR thresholds above (red/yellow/green/dark green).
- Optional: per-row "max IRR clearing 10%" annotation.

Self-contained: inline CSS + minimal SVG / Canvas for the heatmap. No external CDN — the file should work offline.

## Markdown Rendering Notes

Markdown tables work for Matrix 1 and 2. Use code-block fenced for Matrix 3 (it's wide and benefits from monospace alignment).

Color coding is lost in markdown — surface the IRR thresholds in prose immediately after each matrix:

> Cells with implied unlevered CAGR ≥ 10% are investable at the conventional required return. Above-15% cells suggest high-conviction long positions. Below-6% cells indicate value destruction at current price.
