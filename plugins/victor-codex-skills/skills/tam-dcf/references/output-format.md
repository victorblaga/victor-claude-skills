# Output Format

Two deliverables. Both saved to `~/.investing/companies/<TICKER>/<DATE>/`.

- **`dcf.md`** — canonical report, matches the structure of the source DCF prompt. The primary reading artifact.
- **`dcf.html`** — interactive companion, valuable for sensitivity exploration. Self-contained.

This file specifies both.

**Unit convention for output.** Revenue, FCFF, NOPAT, EBIT and all $-denominated quantities are in **nominal $**. Growth% column in the forecast table is **nominal growth %** (matches the TAM nominal CAGRs by construction). Terminal real growth surfaces as a derived quantity in sensitivity Matrix 3 and the assumption table only — for reader intuition, not a separate ledger. No today's-$ column appears in the forecast — that lives in the TAM dialogue, not in the DCF output.

## `dcf.md` — Canonical Markdown Report

### Required Section Order

The DCF prompt is specific about section order. Don't reorder.

```
1. Compact conclusion
2. Data snapshot
2.5. Reported → Economic Bridge
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

### Section 2.5 — Reported → Economic Bridge

From Step 2. Surfaces the accounting-to-economic reconciliation so the rest of the report reads on a consistent basis and the user (or any skeptic) can trace the bridge.

**Clean case** — if the audit found no quirks on either revenue or margin side:

> No reported-to-economic adjustments. Revenue and margins on reported basis throughout. Audit confirmed clean: no pass-through revenue, no one-time SBC vintage, no strategic-segment reclassification needed.

**Quirky case** — table format:

| Item | Reported | Adjustment | Economic | Rationale |
|------|----------|------------|----------|-----------|
| Revenue (Y0, nominal $) | $X | -$Y (pass-through ad fund, inherited from TAM) | $Z | <link to TAM `economic_bridge.revenue_side` source> |
| EBIT (Y0) | $X | +$Y (strategic store segment reclassified) - $Z (run-rate SBC normalization removes one-time vintage) | $W | <link to source> |
| EBIT margin (Y0) | X% | computed | Y% | bridge math from rows above |
| Diluted shares | X | + Y (one-time CEO grant, probability-weighted dilution at hurdle prices) | X+Y (contingent) | <link to DEF14A source> |
| Run-rate SBC % rev | Z% reported (3yr avg) | -W% (one-time vintage) | (Z-W)% | <link to vintage breakdown> |

Followed by 1-2 short paragraphs covering:
- Which quirks were stripped, which reclassified, which treated as contingent.
- Which peer-benchmark normalizations were applied at Step 4.
- One-line per significant adjustment: the rationale and the source.

Footer:

> Full bridge in `dcf-state.json` `economic_bridge` block. The Reported → Economic Bridge ensures the rest of this report (mature-margin assumptions, reverse DCF, implied multiples) reads on a consistent economic basis. The reported view appears in Section 10 (Implied-Multiple Sanity Check) for screener-comparability only — it is not the basis for the verdict.

### Section 3 — TAM Hand-Off Summary

ONE PARAGRAPH. Reference `handoff.md`, don't redo. Required content:

- Bear / low / base / high / bull revenue at hand-off horizon (**nominal $**, single unit).
- Growth shape per scenario.
- 2-3 dominant Fermi drivers.
- Bear mechanism (one line) + low partial materialization (one line).
- Bull adjacencies (one line each) + high partial realization (one line).
- Speculative-layer values per scenario (bear=0 hard rule).
- Hand-off horizon year + inflation assumption used (for terminal real-growth derivation).

End with: "Full TAM analysis at `<absolute path to handoff.md>`."

### Section 4 — Key Assumptions With Evidence

The DCF-specific assumption set, with citations:

- Mature EBIT margin (bear / low / base / high / bull), with peer-anchor source.
- Mature ROIC (bear / low / base / high / bull), with moat justification.
- Mature reinvestment rate.
- Margin / reinvestment ramp shape (annual to Y10, periodic after).
- WACC components: cost of equity, cost of debt, tax rate, capital structure weights, calculated and used WACC.
- Lease framework chosen (operating-cost vs capitalized).
- SBC treatment (always: real economic expense).
- Diluted share count + projection of dilution/buybacks over the horizon.
- Terminal real growth + terminal nominal growth.

Each assumption cites a source or a TAM hand-off field.

### Section 5 — Explicit Forecast

Annual to Y10, then 5-year intervals to hand-off horizon (Y15, Y20, Y25, Y30 ... up to horizon).

Columns (per scenario, base case shown in detail; bear and bull in supplementary tables):

| Year | Revenue (nominal $) | Nominal growth % | TAM_share | EBIT margin | NOPAT | D&A | Capex | ΔNWC | FCFF | ROIC | Reinv rate |
|------|---------------------|------------------|-----------|-------------|-------|-----|-------|------|------|------|-----------|

**Column units are explicit.** Revenue is nominal $. Growth% is nominal growth (matches the TAM nominal CAGRs). EBIT margin, ROIC, Reinv rate are dimensionless ratios on the same nominal flows. No real columns in this table — real terminal growth is a derived cross-check, surfaced in the assumption table + Matrix 3.

**The per-scenario growth path declared in TAM (nominal period CAGRs + growth shape label) MUST be visible in the Nominal-growth% column.** If TAM declared `stay-elevated` and the column shows smooth fade, the math is wrong — re-run dcf-math. Same the other way: if TAM declared `smooth-fade` and the column shows mid-cycle elevation, also wrong.

**Nominal-throughout disclosure (required at top of Section 5):**

> Revenue stream consumed from TAM hand-off as nominal $ directly. No inflation overlay applied in DCF. Growth% column is nominal growth, matches TAM-declared nominal period CAGRs by construction. WACC is nominal (composition embeds `<X>%` currency inflation). Terminal real growth derived as `g_nominal_Y21-maturity − inflation_assumption_pct = <X>%`.

#### Revenue Path Method Disclosure (REQUIRED)

At the top of Section 5, before the per-scenario tables, include an explicit method disclosure block:

```markdown
**Revenue path method**: Per-scenario nominal annual revenue series sourced directly from TAM hand-off
(`aggregated.annual_revenue_nominal_per_scenario`). No inflation pass — series is nominal at every year.
Re-derived locally and audited cell-by-cell against TAM-stored series within 50bp tolerance (Step 7.0
series consumption audit, sanity check #15). Mgmt-guide reconciliation at Step 7.1 (sanity check #14)
confirms modeled Y1 nominal growth matches mgmt FY+1 guide midpoint within 100bp on base.

**Per-scenario path shape**:
- Bear: <stay-elevated / smooth-fade / front-loaded / back-loaded>, peak year Y<N>
- Base: <...>
- Bull: <...>

**Growth engine + forecast method**:
- Engine type: <opex_funded | capex_funded | acquisition_funded | mature_cash_cow | mixed_engine>
- Forecast method: <cash_conversion_margin | sales_to_capital | acquisition_track | maintenance_fcff | per_segment>
- Rationale: <one-line: e.g., "Vertical SaaS; capex 0.7% rev; R&D+S&M 20%; M&A episodic; FCFF margin 20% observable → opex_funded with cash-conversion margin">
- Engine-specific anchor summary: <one line per scenario showing the primary anchor — e.g., "Base mature cash_conversion_margin: 25%; Bull: 30%; Bear: 18%">
- Maintenance-only FCFF margin (stop-the-engine view): <one line per scenario — e.g., "Base 30% / Bull 35% / Bear 24% — structural ceiling">

For `acquisition_funded` engines, also disclose:
- M&A deployment % FCF assumption per period (current → mature, e.g., "85% → 30%")
- ROIC-acquired per scenario
- FCFF_pre_M&A vs FCFF_post_M&A — both shown in the forecast table; reverse DCF runs on `FCFF_post_M&A`

For `mixed_engine`, list per segment:
- Segment name, engine type, revenue weight at maturity (per scenario), forecast method, primary anchor.

**Layer-schedule consistency**: <PASS / FAIL>. Read from `aggregated.layer_schedule_consistency_test` in TAM state. If FAIL, halt before dcf.md emission.
**Series consumption audit (Step 7.0)**: <PASS / FAIL>. If FAIL, halt — TAM CAGRs vs stored series have drifted.
**Mgmt-guide reconciliation (Step 7.1)**: <PASS / OVERRIDE / FAIL>. If FAIL, halt — modeled Y1 nominal growth doesn't reconcile to mgmt guide.
```

The disclosure must appear in every `dcf.md` output. No silent revenue-path generation. No silent engine choice. No silent inflation overlay. The user should be able to read the disclosure and know exactly how the revenue path was constructed AND which forecasting identity drives FCFF generation AND that the nominal-throughout firewall held.

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

**Dual-basis presentation when economic ≠ reported**. If Step 2 produced any margin-side adjustment, OR if TAM hand-off carries `revenue_basis: economic_adjusted`, present multiples on both bases — economic for the real read, reported for screener comparability:

```
                            Implied at base value    Current        Peer median (normalized)    Peer median (raw)
Economic basis:
  EV / FY27 EBIT                X×                    Y×              Z×                          —
  EV / FY27 FCFF                X×                    Y×              Z×                          —
  P / FY27 E                    X×                    Y×              Z×                          —

Reported basis (screener view):
  EV / FY27 EBIT (reported)     X×                    Y×              —                           Z×
  EV / FY27 FCFF (reported)     X×                    Y×              —                           Z×
```

**Clean case** — single block, reported = economic.

Surface anomalies on the **economic** basis (the real read): e.g., "base value implies entry P/E of 60× on economic basis, which is materially above peer-normalized median of 30×. Either the growth assumption is industry-leading and defensible, or the margin assumption is."

Footnote any large reported-vs-economic gap: e.g., "Reported P/E of 25× makes this look cheap to a screener; the economic P/E of 60× reflects the true earnings power after stripping pass-through revenue and normalizing SBC vintage."

**Negative-multiple flag (mandatory).** If any implied multiple comes out negative (e.g., negative `EV/FCFF` because modeled FY-next FCFF is negative for a cash-generative company), the section must include a prominent warning block:

```markdown
> ⚠ **NEGATIVE IMPLIED MULTIPLE DETECTED**: Modeled FY-next FCFF = `$<X>M` (negative), producing implied EV/FCFF of `<Y>×`. For a cash-generative company, this is a smoking gun — the forecast is producing negative cash flow where actual cash flow is positive. Cross-check against Step 8 cash-reality result: if Y1 modeled FCFF margin is materially below actual/guided AND no override mechanism is logged, the model is suspect. See `references/dcf-protocol.md` Known Failure Mode appendix.
>
> Resolution: revisit Step 3 engine classification + Step 4 anchor set + Step 8 cash-reality check.
```

For acquisition_funded engines, the multiple should use `fcff_post_ma` (cash distributable during engine-running phase) — not `fcff_pre_ma` which would over-state the multiple by ignoring M&A deployment. Disclose which basis is used.

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
- Five lines: bear / low / base / high / bull.
- Annotated breakpoints at per-scenario peak-growth years.

### Forecast Table

- Annual rows Y1-Y10 visible by default; periodic rows (Y11-Y20, Y21-maturity) collapsed by default.
- Sortable by column (click header).
- "Switch scenario" dropdown — toggle bear / low / base / high / bull.

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
3. All 5 scenarios are monotonic in every output (`bear < low < base < high < bull`).
4. Reverse-DCF IRR is consistent across the markdown report, the HTML, and the underlying `dcf-state.json`.
5. **No magic haircuts**: scan the markdown for "haircut," "conservative alternative base," "applied a X% reduction," "for margin of safety we cut" — these phrases trigger a hard fail and require regenerating.
6. PV-by-period sums to total EV.
7. Terminal value flag set correctly (> 50% of EV → flagged in section 6).
8. **Revenue path method disclosure** present in Section 5, including nominal-throughout disclosure block. If missing → FAIL.
9. **Layer-schedule consistency (carried from TAM)** PASS per scenario. If any scenario has unresolved violations → FAIL the final pass.
10. **Y0 anchoring** verified: consumed nominal series Y0 == `data_snapshot.ttm_revenue_$` (nominal by construction) within 50bps. If `revenue_basis: economic_adjusted`, Y0 anchor uses `economic_revenue_y0_nominal_$` from `tam_session.economic_bridge`, not the reported figure — verify the right field flowed through.
11. **Section 2.5 (Reported → Economic Bridge)** present in dcf.md. Clean case = one-line "no adjustments." Quirky case = bridge table populated with rationale per row. If missing → FAIL.
12. **Section 10 dual-basis presentation** when economic ≠ reported. If `economic_bridge.margin_side` shows any adjustment OR `revenue_basis: economic_adjusted`, multiples must show both bases. If single-block presentation under those conditions → FAIL.
13. **Section 5 growth engine + forecast method disclosure** present. Engine type, forecast method, rationale, engine-specific anchor summary, maintenance-only FCFF margin all populated. If missing → FAIL.
14. **Section 10 negative-multiple warning** present if any implied multiple is negative. Without the warning block → FAIL.
15. **Cash-reality check result reflected in dcf.md.** Section 9 or a new sub-block must surface the comparable + per-scenario delta + any override mechanisms logged. If `cash_reality_check.audit_status != "completed"` in dcf-state.json → FAIL.
16. **Series consumption audit (Step 7.0)** PASS. Re-derived nominal series matches TAM-stored series cell-by-cell within 50bp per scenario per year. If FAIL → halt.
17. **Mgmt-guide reconciliation (Step 7.1)** PASS or OVERRIDE. Modeled Y1 nominal growth within 100bp of mgmt FY+1 guide midpoint on base (300bp on non-base) absent logged override. If FAIL without override → halt.
18. **Nominal-throughout basis-flag check** PASS. All TAM basis flags (`annual_revenue_nominal_per_scenario._basis`, `growth_path_cagrs_per_scenario._basis`, `y1_3_guidance_anchor.basis`) carry nominal labels. If any flag stale → halt; TAM must be re-run under nominal-throughout schema.

Failures: surface to user before declaring the output done.
