# Output Format

Two deliverables. Both saved to `~/.investing/companies/<TICKER>/<DATE>/`.

- **`dcf.md`** — canonical report, matches the structure of the source DCF prompt. The primary reading artifact.
- **`dcf.html`** — interactive companion, valuable for sensitivity exploration. Self-contained.

This file specifies both.

## `dcf.md` — Canonical Markdown Report

### Required Section Order

The DCF prompt is specific about section order. Don't reorder.

```
1. Compact conclusion
2. Data snapshot
3. TAM hand-off summary
4. Key assumptions with evidence
5. Explicit forecast
6. WACC and EV → equity bridge
7. Reverse DCF
8. Sensitivity matrices
9. Brief accounting checks
10. Implied-multiple sanity check
11. Material risks and final confidence level
```

### Section 1 — Compact Conclusion

The most important section. The user reads this first; it must stand alone.

Required content (in this order):

- **Current price** and **base intrinsic value** per share.
- **Implied annualized return** at today's price (from reverse DCF, base case).
- **What's required to clear 10% IRR** at today's price — name the TAM scenario + margin combination.
- **Sensitivity range**: low intrinsic value (bear-of-bear) and high intrinsic value (bull-of-bull).
- **Adjacency / speculative dependency**: does the current price require any adjacent layer or speculative TAM contribution to be defensible? Be specific.
- **Bear-mechanism exposure**: is the current price exposed to the bear mechanism named in the TAM hand-off?
- **Verdict**: one of `BUY / WATCH / AVOID` + a short reason.
- **Overall confidence**: low / moderate / high.

Length: 6-12 bullet points or short paragraphs. **No filler.** No "the DCF model suggests" preamble. State results.

### Section 2 — Data Snapshot

A table or compact list of TODAY's numbers:

- Current price, market cap, EV, net debt, diluted shares.
- Last reported FY: revenue, EBIT, EBIT margin, GAAP and adjusted FCFF (note SBC).
- Current ROIC and reinvestment rate.
- Days since last reporting period.

All from the data anchored in Step 1.

### Section 3 — TAM Hand-Off Summary

ONE PARAGRAPH. Reference `handoff.md`, don't redo. Required content:

- Bear / base / bull revenue at maturity (today's $ + nominal $).
- Growth shape.
- 2-3 dominant Fermi drivers.
- Bear mechanism.
- Bull adjacencies (one line each).
- Speculative-layer weighting.
- Hand-off horizon year.

End with: "Full TAM analysis at `<absolute path to handoff.md>`."

### Section 4 — Key Assumptions With Evidence

The DCF-specific assumption set, with citations:

- Mature EBIT margin (bear / base / bull), with peer-anchor source.
- Mature ROIC (bear / base / bull), with moat justification.
- Mature reinvestment rate.
- Margin / reinvestment ramp shape (annual to Y10, periodic after).
- WACC components: cost of equity, cost of debt, tax rate, capital structure weights, calculated and used WACC.
- Lease framework chosen (operating-cost vs capitalized).
- SBC treatment (always: real economic expense).
- Diluted share count + projection of dilution/buybacks over the horizon.
- Terminal real growth + terminal nominal growth.

Each assumption cites a source or a TAM hand-off field.

### Section 5 — Explicit Forecast

Annual to Y10, then 5-year intervals to maturity (Y15, Y20, Y25, Y30 ... up to maturity).

Columns (per scenario, base case shown in detail; bear and bull in supplementary tables):

| Year | Revenue | Growth% | TAM_share | EBIT margin | NOPAT | D&A | Capex | ΔNWC | FCFF | ROIC | Reinv rate |
|------|---------|---------|-----------|-------------|-------|-----|-------|------|------|------|-----------|

**The stacked-S-curve inflection points from TAM MUST be visible in the Growth% column.** If the column shows smooth fade where TAM said stacked-S, the math is wrong — re-run dcf-math.

#### Revenue Path Method Disclosure (REQUIRED)

At the top of Section 5, before the per-scenario tables, include an explicit method disclosure block:

```markdown
**Revenue path method**: <one of>

- "Per-scenario annual revenue series sourced directly from TAM hand-off (highest fidelity, no derivation needed)."
- "Per-scenario annual revenue series derived from TAM per-scenario period CAGRs (Y1-3 / Y4-5 / Y6-10 / Y11-20 / Y21-maturity). Hand-off contract test PASS per scenario (CAGRs compound to endpoint within 2%)."
- "[HALT MODE — do not generate dcf.md if this applies] TAM hand-off provided only a single CAGR set; cannot proceed without per-scenario CAGRs."

**Per-scenario path shape**:
- Bear: <stacked-S / smooth fade / front-loaded / back-loaded>, peak year Y<N>
- Base: <...>
- Bull: <...>

**Shape sanity**: <PASS / FAIL>. If any mid-cycle reacceleration above an earlier peak, it must be traceable to a named TAM layer activating at that year. Otherwise FAIL and halt before dcf.md emission.
```

The disclosure must appear in every `dcf.md` output. No silent revenue-path generation. The user should be able to read the disclosure and know exactly how the revenue path was constructed.

### Section 6 — WACC and EV → Equity Bridge

```
PV by Period:
  Y1-10:        $X (Y% of EV)
  Y11-20:       $X (Y% of EV)
  Y21-maturity: $X (Y% of EV)
  Terminal:     $X (Y% of EV)
  Total EV:     $X
  
  − Net debt:                $X
  − Lease liabilities:       $X  (if capitalized framework)
  − Preferred:               $X
  − NCI:                     $X
  + Cash above operating:    $X
  = Equity value:            $X
  ÷ Diluted shares:          X
  = Value per share:         $X
```

Flag if Terminal > 50% of EV.

### Section 7 — Reverse DCF

Per scenario + 10%-clearing case. Format:

```
Bear:    Current EV = $X. Implied unlevered CAGR: Y%. Beats 10%? No / Yes.
Low:     Current EV = $X. Implied unlevered CAGR: Y%. Beats 10%? ...
Base:    Current EV = $X. Implied unlevered CAGR: Y%. Beats 10%? ...
High:    Current EV = $X. Implied unlevered CAGR: Y%. Beats 10%? ...
Bull:    Current EV = $X. Implied unlevered CAGR: Y%. Beats 10%? ...

10%-clearing case: requires <TAM scenario> + <mature margin> + <other anchor>.
  Inside the TAM spread? Yes / No / Beyond bull.
```

### Section 8 — Sensitivity Matrices

Three matrices per `sensitivity-matrices.md`. Markdown tables for Matrices 1 and 2; code-block for Matrix 3.

Each followed by a short prose block surfacing:
- Which cells clear 10% IRR.
- Which cells are below 6%.
- What the current price requires.
- Tolerance to TAM / margin disruption.

### Section 9 — Brief Accounting Checks

One line each:

- **SBC**: included as real opex; not added back. Diluted share count includes RSU/option dilution.
- **Leases**: `<framework>` applied. Lease liabilities `<included / excluded>` from EV bridge.
- **Dilution**: current diluted X shares, projected X shares at maturity reflecting SBC issuance minus buybacks.

If any of the three is material to the verdict, expand into a paragraph.

### Section 10 — Implied-Multiple Sanity Check

At the base intrinsic value, what do the implied entry multiples look like vs current and vs peer benchmarks?

```
                Implied at base value    Current        Peer median
EV / FY27 EBIT       X×                    Y×              Z×
EV / FY27 FCFF       X×                    Y×              Z×
P / FY27 E           X×                    Y×              Z×
```

Surface anomalies: e.g., "base value implies entry P/E of 60×, which is materially above peer median of 30×. Either the growth assumption is industry-leading and defensible, or the margin assumption is."

### Section 11 — Material Risks and Final Confidence

No boilerplate. Specific risks tied to the named bear mechanism + the speculative layer + the WACC assumption. 3-5 bullets.

Final confidence: low / moderate / high. One sentence explaining the rating.

---

## `dcf.html` — Interactive Companion

Self-contained single file. Opens in any modern browser. No external dependencies (no CDN, no internet required).

### Required Sections (Tabs or Vertical)

1. **Compact Conclusion** — same content as `dcf.md` section 1, formatted for screen.
2. **Sensitivity Heatmaps** — the three matrices, rendered as color-coded grids.
3. **Forecast** — sortable, collapsible table.
4. **Charts** — revenue / FCFF / EBIT margin / ROIC over horizon, per-scenario lines.
5. **Reverse-DCF** — current price marker, implied IRR per scenario, 10%-clearing requirements.

### Sensitivity Heatmap Specs

For each matrix:

- Grid of cells with `value-per-share` (large) + `implied CAGR%` (small) per cell.
- Color scale: red < 6% IRR; yellow 6-10%; green 10-15%; dark green > 15%.
- **Hover** on cell → tooltip showing the assumption deltas vs base.
- **Click** on cell → expandable card below the grid showing: full assumption set for that cell, FCFF path summary (Y1 / Y5 / Y10 / Y20 / maturity), reverse-DCF computation steps, implied multiples at that valuation.
- Cells where current price's IRR sits should be marked with a small icon (★).

### Chart Specs

Inline SVG charts (avoid heavy JS libraries). For each chart:

- X axis: year (Y1 → maturity).
- Y axis: the metric (revenue $, FCFF $, margin %, ROIC %).
- Three lines: bear / base / bull.
- Annotated breakpoints at S-curve inflection years.

### Forecast Table

- Annual rows Y1-Y10 visible by default; periodic rows (Y11-Y20, Y21-maturity) collapsed by default.
- Sortable by column (click header).
- "Switch scenario" dropdown — toggle bear / base / bull.

### Reverse-DCF Panel

- Current price displayed prominently.
- Per scenario: implied unlevered IRR, color-coded.
- "10%-clearing case" highlighted: what's required.
- Short explanation: "The reverse DCF solves for the unlevered enterprise discount rate that reconciles current EV with the scenario's FCFF stream. The IRR shown is unlevered, not levered equity IRR."

### Implementation Notes

- HTML5 + inline CSS + vanilla JS (no jQuery, no Chart.js, no React).
- File size target: under 200KB.
- Computation: pre-compute everything in dcf-math; HTML is rendering only — no on-the-fly DCF calculation in the browser.
- Mobile responsive (best-effort; desktop is the primary surface).

### Template Skeleton

The dcf-math subagent outputs structured JSON (see `state-schema.md` for `dcf-state.json` and the `output_artifacts.dcf_data` structure). The main thread takes that JSON and renders to HTML using the template skeleton in `agents/dcf-math.md` (the subagent writes the final HTML directly — main thread does not need to re-render).

## Sanity-Check Before Saving

Run dcf-math one last time with the "final pass" check:

1. Markdown report contains all 11 sections.
2. HTML file opens (smoke test: dispatch a subagent to view the file or just verify file size > 50KB).
3. Bear / base / bull are monotonic in every output (`bear < base < bull`).
4. Reverse-DCF IRR is consistent across the markdown report, the HTML, and the underlying `dcf-state.json`.
5. **No magic haircuts**: scan the markdown for "haircut," "conservative alternative base," "applied a X% reduction," "for margin of safety we cut" — these phrases trigger a hard fail and require regenerating.
6. PV-by-period sums to total EV.
7. Terminal value flag set correctly (> 50% of EV → flagged in section 6).
8. **Revenue path method disclosure** present in Section 5. If missing → FAIL.
9. **No `revenue_path_adjustment` entries** in `.dcf-check.log`. Their presence indicates silent rescaling occurred — should have HALTED at Step 0. FAIL the final pass.
10. **Per-scenario shape sanity** PASS. If any scenario's path shows unexplained mid-cycle reacceleration above an earlier peak → FAIL.

Failures: surface to user before declaring the output done.
