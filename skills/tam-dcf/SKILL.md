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
- **Dispatch dcf-math** at minimum: at Step 7 (the full forecast + EV bridge + reverse DCF + sensitivity matrices) and on-demand whenever the user asks "recheck" or revises an assumption.

The `.dcf-check.log` file records every Python computation with inputs, code path, outputs. The user can audit it.

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
| Mature EBIT margin (per scenario, all 5) | Peer-anchored, but persona-dependent (industrials-SaaS vs pure-play SaaS vs marketplace) | varies |
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

## Step 0 — Load TAM, Verify, Sanity-Check (HARD-FAIL ON INCONSISTENCY)

First message of every fresh DCF session:

1. **Load** `~/.investing/companies/<TICKER>/<DATE>/handoff.md` and `state.json`. Parse the hand-off block (section G) into structured form.
2. **Summarize** the user's TAM interpretation: company, currency, hand-off horizon (Y`<N>`), last reported revenue + YoY growth, revenue at maturity across 5 scenarios (bear/low/base/high/bull), **per-scenario period CAGRs** (5 rows), Y1-3 guidance anchor, growth shape per scenario, dominant Fermi drivers, bear mechanism, low/high partial materializations, bull adjacencies, speculative layer values per scenario, layer activation schedule.
3. **Run hand-off verification checks**. Any failure HALTS the DCF — do not silently work around:

   **3a. Required fields present.** Hand-off must carry: per-scenario period CAGRs (bear/low/base/high/bull, 5 scenarios × 5 periods = 25 CAGRs); per-scenario endpoints (today's $ + nominal $, 5 scenarios); last reported revenue + last reported YoY growth; **`revenue_basis` field (`reported` | `economic_adjusted`) + economic bridge summary** (from TAM Step 1); Y1-3 guidance anchor; per-layer activation schedule; growth shape + peak-growth year per scenario. If anything is missing, halt and prompt user to re-run TAM with the missing field.

   **3b. Hand-off contract test (per scenario).** For each scenario, verify the stated period CAGRs compound to the stated endpoint within 2%. If any scenario fails, halt and force user choice between revising the TAM endpoint, revising the TAM CAGRs, or providing an explicit annual series. Do NOT silently rescale CAGRs to fit endpoint.

   **3c. Y1-3 anchor test.** Verify the **base** scenario's Y1-3 CAGR is within ±3pp of `aggregated.y1_3_guidance_anchor.midpoint`, OR carries a logged `override_reason`. Bear / low / high / bull must each carry their own `override_reason` describing the bear-mechanism / bull-adjacency intensity that drives the spread from base. Halt on failure — resolve in TAM.

   **3d. Layer-schedule consistency.** Re-read `aggregated.layer_schedule_consistency_test`. Refuse to proceed if any of the 5 scenarios has unresolved violations.

   **3e. Y0 anchoring.** Verify the consumed annual series Y0 (per scenario) equals `last_reported_revenue_today_$` within 50bps. Mismatch → halt.

   **3f. Scenario monotonicity.** Re-read `aggregated.scenario_monotonicity_test`. `bear < low < base < high < bull` must hold for revenue at maturity (aggregated and per-layer). Halt on violation.

   **3g. Speculative-bear-zero.** Any layer flagged `speculative: true` must have `layer_revenue_at_maturity_today_$.bear == 0`. Halt on violation.

   **3h. Two-bases pathology.** If the TAM output mentions an "alternative haircut base" or "analyst-conservative base" alongside the bottom-up base, surface as TAM-side error. DCF cannot proceed with two bases.

   **3i. Internal arithmetic.** Revenue at maturity nominal vs today's-$ × inflation^N — must reconcile per scenario.

4. If any check fails, **HALT and prompt user with the specific options** for that failure. Never silently work around. Never silently rescale.
5. Once all checks pass, ask: "Hand-off verified consistent across all scenarios. Ready to start the DCF assumptions? Same per-anchor pacing as `/tam-analysis`."

**This step is the firewall between TAM and DCF.** A broken TAM should never produce a DCF artifact silently. Either the TAM is fixed or the DCF refuses to run.

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

Step 1 captures the reported snapshot. The **reported-to-economic bridge** runs at Step 2 before mature-margin assumptions are anchored at Step 4.

## Step 2 — Reported-to-Economic Bridge (Margin Side)

Step 1 captured the reported picture. Before anchoring mature economics (Step 4) on peer-benchmarked GAAP margins, audit the income statement for accounting-economic divergence on the **margin side**. Three patterns to surface, each with potential to swing the DCF by 2-10×.

This step is the firewall between reported financials and modeling assumptions. A polluted peer-margin benchmark corrupts Step 4 (the single highest-leverage assumption in the whole DCF) → corrupts Step 7 forecast → corrupts the reverse DCF → corrupts the verdict. Run the audit even when nothing obvious surfaces — confirming a clean reading is itself useful.

### 2a — Pass-through Revenue (Carried from TAM)

If `handoff.md` carries `revenue_basis: economic_adjusted`, the TAM has already stripped pass-through revenue at the Y0 anchor. Confirm propagation:

- Step 4 peer-margin benchmarks must be computed on the **same basis** as the target. If peer median EBIT margin uses reported revenue in the denominator and target uses economic revenue, the comparison is corrupted.
- Normalize both sides — when dispatching anchor-researcher for peer margins, the dispatch payload must explicitly say: "strip the same pass-through pattern from peers (where present) before computing peer EBIT margin."
- Surface both raw peer margin and normalized peer margin in the Step 4 anchor confirmation.

If `revenue_basis: reported`, no propagation needed — both target and peers use reported revenue. Note this in the bridge and move on.

### 2b — SBC Vintage Audit

The SBC line on the income statement is a **sum** — run-rate annual grants + any active one-time vintage (CEO performance award, founder mega-grant, retention package). The DCF's mature-margin assumption must use **run-rate SBC**, not a sum that includes a one-time vintage extrapolated as recurring.

Action:

1. Dispatch anchor-researcher: pull DEF14A / proxy statement for the company's material outstanding grant vintages. Identify one-time mega-grants tied to long-dated stock-price hurdles, founder-transition vesting, retention packages. Note vesting structure (cliff, hurdle prices, expiry).
2. Decompose reported SBC into:
   - `run_rate_sbc_pct_revenue`: the recurring annual grant pace (RSU refresh, new-hire grants, broad-based equity).
   - `one_time_sbc_components`: list of distinct vintages, each with total grant value, vesting structure, probability-weighted expected value.
3. Treatment split:
   - **Mature-margin assumption (Step 4)**: use `run_rate_sbc_pct_revenue` only. Do not extrapolate one-time vintage.
   - **EV → equity bridge (Step 7)**: treat one-time vintage as contingent equity dilution at the hurdle prices. Probability-weighted expected dilution adds to diluted share count *at the conditions when it vests*.
   - **Do not strip one-time vintage entirely**. The grant has expected economic cost — it's just not run-rate. Probability-weighted value matters.

### 2c — Strategic Segment Reclassification

Companies sometimes carry a segment whose role is **strategic**, not stand-alone economic — embedded R&D function, captive distribution, brand vehicle, ecosystem loss-leader. Reported margin treats the segment as a sub-business and aggregates by revenue weight; that under-states the economic margin of the **real** business.

Examples:
- **WING company-owned stores** = R&D function (kitchen innovation, pricing tests, tech rollout) → reclassify costs as opex-R&D; exclude segment from operating-segment mature-margin benchmark.
- **AMZN Prime sub revenue** = ecosystem loss-leader (cost in fulfillment, value in cross-category attach) → segment is a customer-acquisition mechanism, not a stand-alone subscription business.
- **AAPL Services initially** = lock-in vehicle, not stand-alone profit center → margin profile reads as embedded software-attach, not stand-alone media.

Action:

1. For each segment with reported margin materially below corporate target margin: ask, "is this a true profit-center sub-business, or is it serving a strategic role (R&D, distribution, brand, customer acquisition)?"
2. If strategic: propose **reclassification** — segment costs move to opex-R&D / opex-distribution / opex-acquisition; the segment is removed from "operating segments" view for mature-margin benchmarking purposes. The reclassified-economic-margin reflects the true economic engine.
3. User confirms per segment. Reclassification requires a named structural reason — not just "lower margin than peer benchmark."

### 2d — Peer Benchmark Normalization Rule (Binding for Step 4)

When dispatching anchor-researcher for peer mature EBIT margins, the dispatch must include normalization spec: "compute peer EBIT margin on the same basis as the target — strip pass-through revenue, normalize SBC vintage (run-rate only), reclassify strategic segments. Surface both raw peer margin and normalized peer margin."

Without this, peer benchmarks lie. The rule is binding.

### Output

Write `economic_bridge.margin_side` to `dcf-state.json` (schema in `references/state-schema.md`) with:
- `reported_ebit_margin_y0` + `economic_ebit_margin_y0` + bridge math.
- `sbc_breakdown.run_rate_sbc_pct_rev` + `sbc_breakdown.one_time_components`.
- `segment_reclassifications`.
- `peer_normalization_spec` (the dispatch spec used at Step 4).
- `audit_status`: `completed`.

### The Economic Basis Flows Downstream

- **Step 4**: mature EBIT margins anchored on `economic_ebit_margin_y0` and normalized peer benchmarks.
- **Step 6f**: SBC treatment uses run-rate; one-time vintage handled separately.
- **Step 7 dcf-math**: takes economic revenue + economic margins as inputs (not reported).
- **Step 10 dcf.md**: surfaces a "Reported → Economic Bridge" section (2.5) with the explicit reconciliation.
- **Reverse DCF + implied multiples**: runs on economic basis. Implied multiples show BOTH bases (economic = the real read; reported = the screener view).

### Clean Case

If the company is clean (typical SaaS, typical industrial, no pass-through, no recent CEO mega-grant, no strategic-loss-leader segment), the audit completes in one short turn with `economic = reported` and Step 4 proceeds on reported basis. Prompt:

> Quick check: no recent CEO performance award, no founder/retention mega-grants, no segments running materially below corporate margin, TAM brought no pass-through? If yes to all four, Step 2 completes as "no quirks — economic = reported" and we proceed to Step 3. Otherwise we walk 2a / 2b / 2c in detail.

Only short-circuit if user affirmatively answers all four. Default to the detailed walk.

### Pushback

- Push back if user accepts reported as economic without scrutiny on a company with obvious quirks: high SBC y/y volatility (suggests vintage), pass-through revenue inherited from TAM (always propagates), multi-segment with one materially below corporate margin (always investigate).
- Push back if user wants to reclassify a real sub-business as "strategic R&D" to manufacture a higher margin. Reclassification requires a named structural reason — the segment's purpose must visibly be strategic, not just "lower margin than peer benchmark."

## Step 3 — Growth Engine Classification

Before anchoring mature economics in Step 4, classify the company's growth engine — what fuels its growth and where growth spend lives in the financials. This drives the forecasting identity that dcf-math uses at Step 7. Misclassification produces the canonical class of DCF failure (sales-to-capital identity applied to opex-funded business → phantom reinvestment, negative implied FCFF margins, negative implied multiples) — see `references/dcf-protocol.md` Known Failure Mode appendix for the canonical instance.

Engine type is a forecasting METHOD choice, not a company-inherent property. Lives in DCF only; does not pollute TAM hand-off. Different engine choices produce different DCFs from the same TAM — no TAM re-run.

The 5 engine types (full detail + identity math in `references/dcf-protocol.md` Growth Engine Taxonomy):

| Engine | Where growth spend lives | Diagnostic signals | Forecast identity |
|--------|--------------------------|--------------------|--------------------|
| `opex_funded` | R&D + S&M in EBIT | capex < 5% rev; R&D+S&M > 25% rev; FCFF margin observable | Cash-conversion margin (FCFF margin direct) |
| `capex_funded` | Tangible capex on new units | capex > 8% rev; unit-economics-driven; sales-to-capital stable | Sales-to-capital (Δrev / s2c) |
| `acquisition_funded` | M&A deployment from FCF | M&A > 20% FCF trailing 3yr; ongoing roll-up; organic modest | Two-track (organic FCFF + M&A deployment) |
| `mature_cash_cow` | Maintenance capex only | Stable revenue base; growth via pricing power | Maintenance FCFF margin |
| `mixed_engine` | Multiple segments with different engines | Diversified large-cap (AMZN, META, BRK) | Per-segment aggregation |

**Action:**

1. **Dispatch anchor-researcher** to fetch 3-yr trailing diagnostic signals: capex intensity, R&D/S&M as % rev, M&A deployment as % of FCF, organic growth rate, sales-to-capital ratio (where applicable), actual FCFF margin (back-solved from disclosed components), guided FY1 FCFF margin.
2. **Skill proposes engine type + rationale** based on the signals. Surface the diagnostic numbers.
3. **User confirms or overrides.** Reclassification requires a named mechanism (e.g., "treating as acquisition_funded because the 3yr M&A pace is the dominant growth source"). Override logged in `growth_engine.rationale`.
4. **Capture engine-specific anchors** (per scenario, all 5):
   - `opex_funded`: cash_conversion_margin_y0, cash_conversion_margin_guided_y1, mature cash_conversion_margin per scenario
   - `capex_funded`: sales_to_capital_y0, mature sales_to_capital per scenario, capex_intensity_y0
   - `acquisition_funded`: organic_growth + organic_fcff_margin per scenario, m_a_deployment_pct_fcf, roic_acquired per scenario, M&A pace assumption
   - `mature_cash_cow`: maintenance_capex_pct_rev_3yr_avg, maintenance_fcff_margin per scenario, growth_via_pricing_power flag
   - `mixed_engine`: per-segment breakdown (each with its own engine + anchors + revenue weight at maturity)
5. **Always ask: maintenance-only FCFF margin (per scenario, all 5).** The "stop-the-engine" view — what FCFF margin if growth-oriented spend drops to maintenance-only (renewals, parity, sustaining). For acquisition_funded, this equals `organic_fcff_margin` (since stopping the engine = stopping M&A deployment). Confirms structural ceiling on cash-cow mode.
6. **Save** to `dcf-state.growth_engine` (schema in `references/state-schema.md`).

**Mixed-engine handling.** If segments can't be modeled separately (segment data not disclosed at this granularity), user picks one of:
- (a) Group segments into 2-3 super-segments by dominant engine.
- (b) Pick the dominant engine and treat the whole company as that engine; the cash-reality check (Step 8) flags if the simplification is too aggressive.
- (c) Halt the DCF: company can't be modeled until segment-level data is available.

**Pushback:**

- Push back when diagnostic signals point one way but user picks a different engine. Force the named mechanism. Example: "Signals show capex 0.7% rev + R&D/S&M 20% rev + M&A deployment 45% of FCF. You picked acquisition_funded — what's the mechanism? If M&A is the dominant growth path, agree. If M&A is opportunistic and organic operating growth is the real engine, that's opex_funded."
- Push back on mature_cash_cow for a growing business. The classification commits to maintenance-only spend, which is wrong if the business is still building units.
- Push back on mixed_engine as a dodge. If the user picks mixed but only one engine actually matters (e.g., 90% of revenue + 95% of FCFF from one segment), simplify.

## Step 4 — Mature Economics (Per Scenario)

The single most consequential DCF assumption set. **Anchor set is engine-conditional** — engine type was confirmed at Step 3. Walk through per scenario (bear / low / base / high / bull).

### Common to all engines

1. **Mature EBIT margin (cross-check)**. Peer-anchored on **economic basis** — both target and peers normalized for pass-through revenue, SBC vintage (run-rate only), and strategic-segment reclassification per Step 2. Dispatch anchor-researcher with the normalization spec from `economic_bridge.margin_side.peer_normalization_spec`. EBIT margin is the GAAP-equivalent cross-check for opex_funded + capex_funded engines; informational for acquisition_funded + mature_cash_cow (their primary anchor is FCFF margin or organic FCFF margin, not EBIT). All 5 scenarios. Monotonicity expected.
2. **Mature ROIC**. Per scenario (5 values). At maturity, drives the terminal-stage `growth ≈ reinvestment_rate × ROIC` identity. Persistent ROIC above WACC requires an explicit moat. Without a named moat, ROIC fades to WACC.
3. **Terminal real growth + reinvestment rate**. Tied at maturity via `g ≈ rate × ROIC`. Real terminal growth typically 0-1%. Cross-check.

### Engine-specific mature anchors (the PRIMARY forecast drivers)

| Engine | Primary mature anchor | Secondary anchors |
|--------|----------------------|-------------------|
| **opex_funded** | `cash_conversion_margin_mature_per_scenario` (FCFF margin at maturity, 5 values) | EBIT margin cross-check |
| **capex_funded** | `sales_to_capital_mature_per_scenario` (revenue / invested capital ex-goodwill at maturity, 5 values) | Mature EBIT margin used directly in `FCFF = NOPAT − ΔRev/s2c` |
| **acquisition_funded** | `organic_fcff_margin_mature_per_scenario` + `roic_acquired_mature_per_scenario` + `m_a_deployment_pct_fcf_mature` + `organic_mature_growth_per_scenario` (5 each) | M&A pace fade assumption to maturity |
| **mature_cash_cow** | `maintenance_fcff_margin_per_scenario` (5 values) | `maintenance_capex_pct_rev` + growth_via_pricing_power flag |
| **mixed_engine** | Per-segment anchors using each segment's engine | Corporate overhead % rev |

Mature `maintenance_only_fcff_margin` from Step 3 is the **structural ceiling** for every engine. If mature scenario FCFF margin exceeds maintenance-only FCFF margin, the math is wrong — flag and resolve.

### Per-anchor confirmation discipline

Push back when:

- The mature EBIT margin sits above sector best-in-class without a named structural reason.
- Persistent ROIC above WACC has no moat behind it.
- Mature reinvestment rate × ROIC doesn't reconcile to terminal real growth — symmetric check per `references/dcf-protocol.md` Terminal-Stage ROIC Consistency Check. Catches both directions: low rate + high growth (operating leverage justified?) AND high rate + modest growth (FCFF suppression).
- Engine-specific anchors imply mature FCFF margin > maintenance-only FCFF margin from Step 3 (impossible — maintenance-only is the structural ceiling).
- For acquisition_funded: `roic_acquired` sits above peer-acquired ROIC without named integration capability (CSU's vertical-software moat is the canonical defensible high value).
- For mature_cash_cow: any mature scenario implies real growth > 2% (mature cash-cow with that growth is mis-classified — should be opex_funded or capex_funded).

## Step 5 — Margin + Reinvestment Ramp (Path from Today to Mature)

Annual to Y10, then per period. The shape matters: a company today at -5% EBIT margin doesn't reach +30% mature margin in Y3. Sketch the ramp:

- Annual EBIT margin Y1-Y10 (per scenario).
- Per-period EBIT margin Y11-15, Y16-20, Y21-maturity.
- Reinvestment rate ramp matching (high reinvestment during ramp, fading to mature rate).

Don't apply mature margins too early. Don't assume harvest-mode maximums. If a loss-making initiative (e.g., still-investing speculative layer) is material, **segment** the core business from the initiative for forecast purposes — feed two separate margin paths and aggregate.

## Step 6 — WACC + Discount Mechanics

WACC framed as **required return** (not CAPM). Additive composition:

```
WACC = required_real_return + reporting_currency_inflation + jurisdictional_risk_premium + sector_nudge
```

Defaults: USD-listed durable growth → 8% real + 2% USD inflation + 0% jurisdiction + 0% sector = **10%**. Floor: **8.5% USD-equivalent** (scales with currency inflation for non-USD).

The skill announces the composition: "Defaulting to WACC = 10% (8% real + 2% USD inflation + 0% jurisdiction). Say so to override any component."

**Full mechanics + per-currency inflation table + per-jurisdiction risk table + per-sector nudge ranges + reference composition examples** live in `references/dcf-protocol.md` — the WACC Mechanics — Required-Return Framework section. Read it once when WACC is being set; the SKILL.md flow only needs the composition + the override hook above.

**Other DCF mechanics confirmed at Step 6:**

1. **Cost of debt** (matters only if material — D/(E+D) > 20%): current yield or BBB-rated equivalent + credit spread. After-tax = pre-tax × (1 − tax rate).
2. **Normalized tax rate**: long-run effective. US default ~25%.
3. **Capital structure weights**: target weights at maturity, not current.
4. **Lease framework**: pick ONE — operating-cost OR capitalized. Apply consistently. Detail in `references/dcf-protocol.md`.
5. **SBC treatment**: real economic expense at **run-rate** (`economic_bridge.margin_side.sbc_breakdown.run_rate_sbc_pct_rev` from Step 2). One-time hurdle-vested grants treated as **contingent expected-value** separately. Reverse SBC-excluded "adjusted" margins from peer benchmarks.
6. **Diluted share count**: current + economically relevant dilutive instruments (RSUs, options, convertibles).

Per-anchor confirmation. WACC and lease/SBC choices are sticky — flag them as binding for the whole DCF. Do NOT compute beta or pull a current 10Y Treasury yield as inputs (see `references/dcf-protocol.md` What This Framework Replaces).

## Step 7 — Build the Forecast (Dispatch dcf-math)

Once all assumptions are pinned, dispatch the **dcf-math** subagent (`agents/dcf-math.md`) with explicit **basis + engine declarations**:
- Revenue path on the basis from TAM hand-off (`revenue_basis: reported | economic_adjusted`).
- Margins on `economic_ebit_margin_y0` per Step 2.
- **Growth engine** from `dcf-state.growth_engine.type` and **forecast method** from `dcf-state.growth_engine.forecast_method` (set at Step 3). dcf-math branches its forecast generator per engine — opex_funded uses cash-conversion margin, capex_funded uses sales-to-capital, acquisition_funded uses two-track, etc.
- SBC at run-rate only; one-time vintage handled separately in the equity bridge as contingent dilution.

Computes:

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

## Step 8 — Cash-Reality Reconciliation Check

After dcf-math generates the forecast at Step 7 and BEFORE output emission at Step 10. dcf-math runs the **cash-reality reconciliation** (sanity check #12). Compares modeled Y1 + Y2-Y3 FCFF margins against a back-solved "comparable" (the tighter of latest-FY actual after-SBC FCF margin and management-guided NY after-SBC FCF margin).

**Halt thresholds:**
- Y1 modeled FCFF margin: `|delta vs comparable| > 500bp` → halt absent logged mechanism.
- Y2-Y3 average modeled FCFF margin: `|delta vs comparable| > 1000bp` → halt absent logged mechanism.

**Check logic** (engine-agnostic; for acquisition_funded uses `fcff_post_ma` as the modeled cash basis; for mixed_engine uses corporate-level aggregated FCFF margin).

**Why this exists**: catches an assumption set that looks internally coherent but produces Y1-Y3 cash flows inconsistent with observed/guided reality. See `references/dcf-protocol.md` Known Failure Mode appendix for the canonical instance. Full spec in `references/dcf-protocol.md` Cash-Reality Reconciliation Discipline.

**On HALT (per failing scenario):**

> Cash-reality check FAIL for `<scenario>`: modeled Y1 FCFF margin `<X%>` vs comparable `<Y%>` (delta `<Z>bp`, threshold 500bp). Options:
> (a) **Revise assumptions** — pull mature margins, ramp shape, or engine-specific anchors to close the gap. Re-dispatch dcf-math.
> (b) **Name the mechanism** — e.g., "Bear assumes FY2026 customer churn cutting FCF margin temporarily; rejoins peers by Y3." Logged in `cash_reality_check.override.<scenario>.mechanism` + `sources.md`. Free-text but specific.
> (c) **Halt the DCF** — user reconsiders the engine framing (Step 3) or revises in TAM via `/tam-analysis resume`.

Force user choice. Do not proceed silently. If user picks (b), the override mechanism must be specific enough that a future reviewer reading `sources.md` understands the assumption.

**Pass-through**: if all scenarios are within threshold (or have logged overrides), continue to Step 9.

## Step 9 — Forecast-Output Expert Review (Proactive)

The dcf-math output is now generated. Before final emission, the skill offers a **forecast-output expert dispatch** when any of these triggers fire:

1. **Cash-reality check delta in 250-500bp zone** (below halt, above clean) for any scenario.
2. **Terminal share of EV > 50%**.
3. **Mature margin at peer ceiling without named moat** (per `economic_bridge.margin_side.peer_normalization_spec`).
4. **Implied entry multiples > 2× peer median** on economic basis.

If any trigger fires, skill consolidates to one offer:

> Triggers fired: `<list>`. Want a forecast-output expert review? The expert reads the generated Y1-Y3 forecast lines (not just assumptions) + cash conversion vs actual/guidance + terminal share of EV + implied multiples on economic basis. Different persona from the assumption-review expert (see `agents/domain-expert.md` for the forecast-output persona spec).

User can decline.

**Dispatch payload differs from assumption review.** Feeds:
- Y0 actual financials (revenue, NOPAT, FCFF, FCFF margin from `data_snapshot`).
- Latest guidance / consensus (back-solved if FCFF margin not explicit).
- Modeled Y1, Y2, Y3 revenue / NOPAT / FCFF / FCFF margin / cash conversion (from `forecast.annual[0..2]`).
- Modeled Y10 + maturity revenue / NOPAT / FCFF / margin (from `forecast.periodic`).
- Terminal value share of EV.
- Implied entry multiples on economic basis at base.
- Question: "Are the modeled outputs internally coherent and externally credible against observed economics?"

Result appended to `expert-opinions.md`. Recommends number revisions or bear-strengthening only — no haircut option (same discipline as assumption-review expert per `agents/domain-expert.md`).

## Step 10 — Output: Generate dcf.md + dcf.html

Two deliverables. Both saved to the session folder.

### `dcf.md` Structure (Canonical)

Sections in order. Spec in `references/output-format.md`.

1. **Compact conclusion** — current price; base intrinsic value; implied annualized return at today's price; what's required to clear 10%; sensitivity range; whether the price requires adjacent expansion or the speculative layer; whether it's exposed to the named bear mechanism; verdict; overall confidence.
2. **Data snapshot** — from Step 1.
2.5. **Reported → Economic Bridge** — from Step 2. Reconciliation table (revenue, EBIT, EBIT margin, diluted shares) with rationale per adjustment. If clean (no quirks), one-line "no adjustments — reported = economic." Spec in `references/output-format.md` section 2.5.
3. **TAM hand-off summary** — one paragraph; reference `handoff.md`, don't redo.
4. **Key assumptions with evidence** — margins, ROIC, WACC components, reinvestment, tax. Cite.
5. **Explicit forecast** — annual to Y10; periodic to maturity. Per-scenario growth-shape inflections (declared by TAM) visible in the Growth% column.
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

The DCF skill inherits the discipline from `/tam-analysis`: ONE bear / ONE low / ONE base / ONE high / ONE bull. No parallel "haircut base case". No silent value-haircut on the final intrinsic value for "margin of safety" — that lives in scenario design, sensitivity range, and reverse-DCF required return. Expert disagreement on margins / ROIC / WACC resolves the same three ways: revise the assumption (and the old number disappears), reject and log the rejection, or move the concern into the bear scenario. Never carry both.

If the TAM hand-off contains a two-bases pathology, halt at Step 0 and force resolution before the DCF runs.

## Auto-Archive on Supersession

When a DCF run is superseded — due to math-checker FAIL with override, cash-reality FAIL with override, material TAM revision (`tam_handoff_hash` mismatch on resume), or user-initiated rerun with different assumptions — the prior artifacts are archived rather than overwritten. Failure history is part of the audit trail.

**Trigger conditions:**

1. **Automatic** (skill moves files without prompting):
   - Math-checker FAIL not resolved via assumption revision → archive `archive-math-fail/` and re-dispatch.
   - Cash-reality FAIL with override mechanism logged → archive `archive-cash-reality-fail/` (the flagged run) and proceed with override.
2. **User-confirmed** (skill prompts):
   - `/tam-dcf <TICKER>` invoked when existing `dcf-state.json` exists AND assumptions about to change materially (different engine type, different mature anchors, different WACC composition, hand-off hash mismatch). Prompt: "Existing DCF found from `<date>`. Archive as `archive-<reason>/` and start fresh, or resume?"
3. **User-initiated**:
   - User says `/tam-dcf archive <reason>` → manual archive of current artifacts.

**Folder naming convention** (controlled vocab + escape hatch):

```
archive-<reason>/
```

Reason values:
- `math-fail` — math-checker arithmetic violation, unresolved
- `cash-reality-fail` — cash-reality check halt, mechanism logged or user pushed through
- `user-supersede` — user-initiated rerun with materially different assumptions
- `tam-revised` — TAM hand-off changed since last DCF (`tam_handoff_hash` mismatch)
- `other-<short-descriptor>` — escape hatch for unanticipated reasons

**What gets moved:**

```
archive-<reason>/
├── dcf-state.json    # the flagged run's state
├── dcf.md            # the flagged report
├── dcf.html          # the flagged interactive view
├── .dcf-check.log    # validation log
└── README.md         # one-page failure note (auto-written)
```

**README.md template** (auto-written by skill):

```markdown
# Archived DCF Run — <reason>

Archived: <YYYY-MM-DD HH:MM>
Reason: <reason>

## What happened

<one-paragraph: what the run produced, why it was superseded>

## Key diff

- Engine type: <previous> → <new>
- Mature `<anchor>` (base): <previous> → <new>
- WACC: <previous> → <new>
- (etc. — only fields that materially changed)

## Files

- `dcf-state.json` — the state at archival
- `dcf.md` — the flagged report
- `dcf.html` — the flagged interactive view
- `.dcf-check.log` — Python validation history

The active run (post-archive) is in the parent session folder.
```

Archive is **never** silently overwritten — if `archive-<reason>/` already exists, append a numeric suffix (`archive-math-fail-2/`, etc.). Multiple flagged runs preserve their lineage.

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
| `references/dcf-protocol.md` | Per-step DCF logic, FCFF identity, growth-via-reinvestment, mature-economics framework, Known Failure Mode appendix |
| `references/sensitivity-matrices.md` | Spec for the three required sensitivity matrices + reverse-DCF mechanics |
| `references/output-format.md` | `dcf.md` section spec + `dcf.html` schema (self-contained, inline assets) |
| `references/state-schema.md` | `dcf-state.json` structure, resume contract |
| `agents/dcf-math.md` | Python-driven FCFF + WACC + reverse-DCF + sensitivity subagent |
| `agents/domain-expert.md` | On-demand opus-xhigh subagent for margin / ROIC / WACC / peer-benchmark opinions |
