---
name: tam-dcf
description: >
  Long-horizon FCFF DCF for a single growth stock, anchored to a completed TAM analysis
  produced by /tam-analysis. Loads handoff.md + state.json from the most recent
  ~/.investing/companies/<TICKER>/<DATE>/ session and refuses to proceed if none exists.
  Per-anchor dialogue on the DCF-specific assumptions (mature margins, reinvestment
  intensity, ROIC, WACC components, lease + SBC treatment), with Python-validated math,
  reverse-DCF per scenario, sensitivity matrices, and a final report saved as both
  Markdown (canonical) and interactive HTML (sensitivity heatmaps + charts). Trigger
  ONLY on explicit invocation: "/tam-dcf", "/tam-dcf <TICKER>", "/tam-dcf <TICKER>
  <DATE>", "/tam-dcf resume <TICKER>". Do not trigger on generic phrases like "value X",
  "build a DCF for X", "what's X worth" — this is a deliberate workflow that requires
  a completed TAM analysis as input.
---

# TAM-DCF

Long-horizon FCFF DCF for a single growth stock, **anchored** to a TAM analysis produced by the sister `/tam-analysis` skill. This skill does the DCF half of the workflow: revenue ramp comes from the TAM hand-off; this skill focuses on margins, reinvestment intensity, ROIC, WACC, scenario discounting, reverse DCF, sensitivity.

**Hard prerequisite**: a completed TAM analysis at `~/.investing/companies/<TICKER>/<DATE>/handoff.md`. If one does not exist for the requested ticker, the skill refuses to proceed and tells the user to run `/tam-analysis <TICKER>` first.

The TAM/revenue path is mostly settled by the time this skill runs — don't relitigate it. The DCF skill is for the *math*, *margin assumptions*, and *sensitivity*, where most of the iteration value lives.

## Agentic Execution Notes (Claude Opus 4.7)

- **Effort**: Use `xhigh` for orchestration + pushback. Use `sonnet medium` for the dcf-math subagent (the work is Python, not deep reasoning). Use `opus xhigh` for the domain-expert subagent when invoked.
- **Don't rebuild the TAM**: read it, summarize the user's interpretation, but do not relitigate layer-by-layer. If the TAM revenue path looks broken or inconsistent on inspection, FLAG it to the user — don't silently compensate.
- **Subagents are the budget**: dispatch dcf-math via subagent so its Python compute doesn't pollute the orchestrator's context. Same for peer-margin / WACC anchor research via anchor-researcher.
- **Slow by default**: per-anchor confirm for margin assumptions, WACC components, reinvestment intensity. The dcf-math runs in code, but the *assumptions feeding it* are per-anchor.

### All Math Runs in Python — No Exceptions

**Hard rule.** LLMs are unreliable on compounded computation: CAGR over decades, discount-factor compounding, terminal-value formulas, real-vs-nominal conversions, reverse-DCF root-solving, sensitivity-cell IRR derivation. These calculations MUST be performed in Python via the dcf-math subagent. The orchestrator does NOT do math inline — even simple things like "revenue grows 10% → next year is X" go through dcf-math.

Concretely:

- **Never** compute a value-per-share, an IRR, a CAGR, a PV, or a sensitivity-cell number in the main thread. Dispatch dcf-math.
- **Never** "round and present" a number you computed in your head. If a number appears in `dcf.md`, `dcf.html`, or anywhere the user sees it, it came out of a Python computation that was logged to `.dcf-check.log`.
- **Never** approximate the reverse-DCF IRR as "linear upside/downside from base." Every reverse-DCF cell is its own root-solve.
- **Dispatch dcf-math** at minimum: at Step 5 (the full forecast + EV bridge + reverse DCF + sensitivity matrices) and on-demand whenever the user asks "recheck" or revises an assumption.

The `.dcf-check.log` file records every Python computation with inputs, code path, outputs. The user can audit it.

If the main thread is tempted to inline-compute something to "save a subagent dispatch," it must instead write a TODO comment to itself in `dialogue.md` and dispatch dcf-math. The dispatch cost is small; the credibility cost of a wrong DCF number is large.

## Invocation

Explicit only. Triggers:

- `/tam-dcf` — ask which company
- `/tam-dcf <TICKER>` — load latest session for TICKER and start DCF
- `/tam-dcf <TICKER> <YYYY-MM-DD>` — load that specific session date
- `/tam-dcf resume <TICKER>` — resume an in-progress DCF session for TICKER

If no TAM session exists for the ticker, the skill outputs:

> No TAM analysis found at `~/.investing/companies/<TICKER>/`. Run `/tam-analysis <TICKER>` first — the DCF needs a hand-off block as input. Stopping here.

And exits. **Do not** offer to "build a quick DCF without TAM" — the discipline only works end-to-end.

## Output Location

Saved alongside the TAM session:

```
~/.investing/companies/<TICKER>/<YYYY-MM-DD>/
├── handoff.md           # from TAM (consumed, not modified)
├── state.json           # TAM state (read-only)
├── sources.md           # TAM sources (read + appended for DCF anchors)
├── dialogue.md          # TAM dialogue (appended with DCF dialogue)
├── dcf-state.json       # DCF session state (this skill writes)
├── dcf.md               # Canonical DCF report (this skill writes)
├── dcf.html             # Interactive view: sensitivity heatmaps + charts
└── .dcf-check.log       # dcf-math validation log
```

`handoff.md` and TAM `state.json` are read-only inputs. `sources.md` and `dialogue.md` are appended to (DCF-specific anchors live alongside TAM anchors). The four DCF outputs are this skill's deliverables.

## Output Format Decision: Markdown Primary + Interactive HTML Companion

- **`dcf.md`** is the canonical output. Matches the structure of the source DCF prompt verbatim. Markdown because (a) it's the natural reading format for a long quantitative report, (b) it diffs cleanly across iterations, (c) it composes with the existing `handoff.md` pattern.
- **`dcf.html`** is the interactive companion. Specifically valuable for:
  - **Sensitivity matrices** — heatmap cells with hover-detail showing the underlying assumption set, color-coded by implied unlevered IRR.
  - **Charts** — revenue / FCFF / margin / ROIC paths over the long horizon, with per-scenario lines.
  - **Sortable forecast table** — Y1-10 annual plus 5-year intervals to maturity.
- **No xlsx.** Spreadsheets don't fit the read-once-decide-now workflow this skill optimizes for.

Generate both. The HTML is self-contained (no external dependencies — Chart.js inlined or omitted in favor of small SVG charts).

## Working Pattern: Per-Anchor Confirm (for DCF-Specific Assumptions)

The revenue path is already settled by TAM — don't reopen it. Per-anchor confirm applies to **DCF-specific assumptions** the TAM hand-off doesn't pin down:

| Anchor | Why per-anchor | Default range |
|--------|----------------|---------------|
| Mature EBIT margin (per scenario) | Peer-anchored, but persona-dependent (industrials-SaaS vs pure-play SaaS vs marketplace) | varies |
| Margin ramp path | When does mature margin land? Annual to Y10, then by period | shape conversation |
| Reinvestment intensity (capex + ΔNWC as % of revenue) | Drives the growth-via-reinvestment identity | 3-15% mature |
| Mature ROIC | Required by `growth ≈ reinvestment rate × ROIC` | 15-30% for durable moats |
| Cost of equity | 10% default unless user specifies | 10% |
| Cost of debt | Current yield + spread for the company's rating | varies |
| Normalized tax rate | Long-run effective rate | 21-25% US, varies |
| WACC floor | 8.5% unless exceptionally justified | 8.5% |
| Lease framework | Operating-cost vs capitalized — pick one, apply consistently | one |
| SBC treatment | Treated as real economic expense; show explicitly | always real |
| Diluted share count | Current + economically relevant dilutive instruments | from latest filings |
| Terminal growth (real) | At maturity, the "perpetual" real growth. Typically 0-1% real for mature businesses | 0-1% real |

Pacing commands inherited from `/tam-analysis`: `faster`, `autopilot`, `pause`, `back`. Same semantics.

## Step 0 — Load TAM, Verify, Sanity-Check

First message of every fresh DCF session:

1. **Load** `~/.investing/companies/<TICKER>/<DATE>/handoff.md` and `state.json`. Parse the hand-off block (section G) into structured form.
2. **Summarize** the user's TAM interpretation: company, currency, hand-off horizon (Y`<N>`), revenue at maturity bear/base/bull, period CAGRs, growth shape, dominant Fermi drivers, bear mechanism, bull adjacencies, speculative weighting.
3. **Sanity-check** the hand-off internally. Detect:
   - **Two-bases pathology**: if the TAM output mentions an "alternative haircut base" or "analyst-conservative base" alongside the bottom-up base, surface this to the user as a TAM-side error. The DCF cannot proceed with two bases. Stop and ask: "Which base is the actual base? The TAM should have resolved this — either revise the TAM (run `/tam-analysis resume <TICKER>`) or pick one for this DCF run and we'll proceed."
   - **Internal arithmetic inconsistency**: revenue at maturity nominal vs today's-$ × inflation^N — must reconcile.
   - **Smooth-fade where stacked-S claimed**: period CAGRs don't match the stated shape.
   - **Bear/base/bull non-monotonic** (bear ≥ base or base ≥ bull).
4. If any check fails, **flag explicitly** to user before proceeding. Don't silently work around a broken TAM.
5. Ask: "Hand-off looks consistent. Ready to start the DCF assumptions? Same per-anchor pacing as `/tam-analysis`."

## Step 1 — Data Snapshot (Current Financials)

Before margins, anchor on what the company looks like *today*. Dispatch anchor-researcher for:

- **Current revenue** (TTM or last reported FY) — already in TAM state, just confirm.
- **Current EBIT, EBIT margin** — GAAP and adjusted (note SBC).
- **Current ROIC** — NOPAT / invested capital. May be negative for unprofitable growers.
- **Current reinvestment rate** — (capex + R&D + ΔNWC + acquisitions) / NOPAT, or for unprofitable companies, expressed as % of revenue.
- **Current diluted share count + dilutive instruments** — RSUs, options, convertibles.
- **Net debt, cash, leases on balance sheet** — for the EV bridge.
- **Current market cap and EV** (for the reverse-DCF baseline).

Save these to `dcf-state.json` under `data_snapshot`. Confirm each anchor with user.

## Step 2 — Mature Economics (Per Scenario)

The single most consequential DCF assumption set. Walk through per scenario (bear / base / bull):

1. **Mature EBIT margin**. Peer-anchored. Dispatch anchor-researcher for the relevant peer set (matched to the company's mix per the TAM hand-off). For multi-segment companies, sketch per-segment mature margin and aggregate by segment weight at maturity.
2. **Maintenance vs growth-oriented S&M and R&D**. For under-earning / heavily investing companies, separate the two explicitly. Mature S&M = maintenance only (renewals + replacement growth at sector-average pace). Mature R&D = sustaining + competitive parity, not greenfield expansion.
3. **Mature ROIC**. Per scenario. Persistent ROIC above WACC requires an explicit moat — name it. Without a named moat, ROIC fades to WACC over the horizon.
4. **Mature reinvestment rate**. Tied via `growth ≈ reinvestment rate × ROIC`. At maturity, real growth ≈ 0-1%, so reinvestment rate × ROIC should be small. Cross-check.

Per-anchor confirmation. Push back when:

- The mature EBIT margin sits above sector best-in-class without a named structural reason.
- Persistent ROIC above WACC has no moat behind it.
- Mature reinvestment rate × ROIC doesn't reconcile to the terminal real growth.

## Step 3 — Margin + Reinvestment Ramp (Path from Today to Mature)

Annual to Y10, then per period. The shape matters: a company today at -5% EBIT margin doesn't reach +30% mature margin in Y3. Sketch the ramp:

- Annual EBIT margin Y1-Y10 (per scenario).
- Per-period EBIT margin Y11-15, Y16-20, Y21-maturity.
- Reinvestment rate ramp matching (high reinvestment during ramp, fading to mature rate).

Don't apply mature margins too early. Don't assume harvest-mode maximums. If a loss-making initiative (e.g., still-investing speculative layer) is material, **segment** the core business from the initiative for forecast purposes — feed two separate margin paths and aggregate.

## Step 4 — WACC + Discount Mechanics

1. **Cost of equity**: 10% unless user specifies. (Required-return convention.)
2. **Cost of debt**: current yield on the company's bonds, or BBB-rated equivalent + credit spread. Times `(1 - tax rate)` for after-tax cost.
3. **Normalized tax rate**: long-run effective. US default ~25% (Federal 21% + state-adjusted).
4. **Capital structure**: target weights, not current. Most growers tend toward 70-90% equity at maturity.
5. **WACC floor**: 8.5% unless exceptionally justified. Show **both** the calculated and the used WACC if floor is invoked.
6. **Lease framework choice** — must pick ONE and apply consistently:
   - **Operating-cost approach**: lease payments stay in opex; lease liabilities excluded from EV bridge + capital. WACC uses equity + financial debt only.
   - **Capitalized approach**: ROU depreciation in D&A; lease capex in total capex; lease liabilities in EV bridge + WACC weights.
   - **Do not mix.** Frequent failure mode in real DCFs.
7. **SBC treatment**: real economic expense. Reverse any SBC-excluded "adjusted" margins from peer benchmarks. Avoid the double-count trap (expensing SBC in P&L AND counting dilution).
8. **Diluted share count**: current + economically relevant dilutive instruments (RSUs vesting, in-the-money options, convertibles at conversion).

Per-anchor confirmation. WACC and lease/SBC choices are sticky — flag them as binding for the whole DCF.

## Step 5 — Build the Forecast (Dispatch dcf-math)

Once all assumptions are pinned, dispatch the **dcf-math** subagent (`agents/dcf-math.md`) to compute:

1. **Annual forecast Y1-Y10**: revenue (from TAM ramp), EBIT margin, NOPAT, D&A, capex, ΔNWC, FCFF, ROIC, reinvestment rate.
2. **Periodic forecast Y11-maturity**: 5-year intervals. Same columns.
3. **PV of FCFF** by period: Y1-10, Y11-20, Y21-maturity, residual. Flag if residual > 50% of EV.
4. **EV → equity bridge**: subtract net debt, lease liabilities (if capitalized framework), preferred / minorities; divide by diluted share count → value per share.
5. **Reverse DCF per scenario**: solve for the unlevered enterprise discount rate that reconciles current EV with the scenario's FCFF + residual. Plus the 10%-required-return case — what TAM / margin / adjacency assumptions clear 10%?
6. **Sensitivity matrices** (see `references/sensitivity-matrices.md`):
   - TAM scenario × mature EBIT margin (primary).
   - Two-Fermi-driver (from TAM dominant drivers).
   - Discount rate × mature growth (sanity).
7. **Implied multiples** at the base value: entry EV/EBIT, EV/FCFF, P/E. Compare to current and peer benchmarks.

dcf-math returns structured numbers + a Python compute log to `.dcf-check.log`. Main thread surfaces results to user.

## Step 6 — Output: Generate dcf.md + dcf.html

Two deliverables. Both saved to the session folder.

### `dcf.md` Structure (Canonical)

Sections in order. Spec in `references/output-format.md`.

1. **Compact conclusion** — current price; base intrinsic value; implied annualized return at today's price; what's required to clear 10%; sensitivity range; whether the price requires adjacent expansion or the speculative layer; whether it's exposed to the named bear mechanism; verdict; overall confidence.
2. **Data snapshot** — from Step 1.
3. **TAM hand-off summary** — one paragraph; reference `handoff.md`, don't redo.
4. **Key assumptions with evidence** — margins, ROIC, WACC components, reinvestment, tax. Cite.
5. **Explicit forecast** — annual to Y10; periodic to maturity. Stacked-S-curve inflections visible.
6. **WACC and EV → equity bridge** — PV bucketed by period. Flag residual > 50% EV.
7. **Reverse DCF** — per scenario + 10%-clearing case.
8. **Sensitivity matrices** — three matrices, cells as `value-per-share / implied unlevered CAGR%`.
9. **Brief accounting checks** — SBC, leases, dilution — one line each.
10. **Implied-multiple sanity check** — entry EV/EBIT, EV/FCFF, P/E vs current + peers.
11. **Material risks + final confidence** — no boilerplate.

Do NOT dump a per-year discounted FCFF ledger (the prompt explicitly forbids this).

### `dcf.html` Structure (Interactive Companion)

Self-contained single file. Tabs or sections:

- **Sensitivity heatmaps** — three matrices rendered as color-coded grids; hover shows underlying assumptions; click rotates to a per-cell scenario card.
- **Forecast table** — sortable / collapsible (annual Y1-10 expanded, periodic Y11-maturity collapsed).
- **Charts** — revenue / FCFF / EBIT margin / ROIC over the horizon; per-scenario lines.
- **Reverse-DCF panel** — current price, implied unlevered IRR per scenario, the 10%-clearing requirements.

HTML schema in `references/output-format.md`.

## No Magic Haircuts (Inherited Discipline)

The DCF skill inherits the no-magic-haircuts rule from `/tam-analysis`. Specifically:

- **No parallel "haircut base case"** alongside the bottom-up base. ONE bear / ONE base / ONE bull.
- **No silent value-haircut on the final intrinsic value** for "margin of safety." Margin of safety lives in scenario design, sensitivity range, and reverse-DCF required return — never in a post-hoc reduction.
- **Expert disagreement on margins / ROIC / WACC** resolves the same three ways: revise the actual assumption (and the old number disappears), reject and log the rejection, or move the concern into the bear scenario. Never carry both.

If the TAM hand-off contains a two-bases pathology, halt at Step 0 and force resolution before the DCF runs.

## Resume

`/tam-dcf resume <TICKER>`:

1. Find `~/.investing/companies/<TICKER>/<DATE>/dcf-state.json` — pick the most recent.
2. Read it. Identify last completed step.
3. Re-summarize where we left off.
4. Continue per-anchor from the appropriate point.

Within a session, survives context compaction the same way: re-read `dcf-state.json` and dialogue tail.

## Files in This Skill

| File | Purpose |
|------|---------|
| `SKILL.md` | This file. Main flow. |
| `references/dcf-protocol.md` | Per-step DCF logic, FCFF identity, growth-via-reinvestment, mature-economics framework |
| `references/sensitivity-matrices.md` | Spec for the three required sensitivity matrices + reverse-DCF mechanics |
| `references/output-format.md` | `dcf.md` section spec + `dcf.html` schema (self-contained, inline assets) |
| `references/state-schema.md` | `dcf-state.json` structure, resume contract |
| `agents/dcf-math.md` | Python-driven FCFF + WACC + reverse-DCF + sensitivity subagent |
| `agents/domain-expert.md` | On-demand opus-xhigh subagent for margin / ROIC / WACC / peer-benchmark opinions |
