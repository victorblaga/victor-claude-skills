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

## Execution Notes

- **Effort**: Use `xhigh` for orchestration + pushback. Use `medium` for the dcf-math subagent (the work is Python, not deep reasoning). Use `xhigh` for the domain-expert subagent when invoked.
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

   **3a. Required fields present.** Hand-off must carry: per-scenario period CAGRs (bear/low/base/high/bull, 5 scenarios × 5 periods = 25 CAGRs); per-scenario endpoints (today's $ + nominal $, 5 scenarios); last reported revenue + last reported YoY growth; Y1-3 guidance anchor; per-layer activation schedule; growth shape + peak-growth year per scenario. If anything is missing:

   > Hand-off is missing `<field>`. Cannot proceed without it — the contract requires the full per-scenario growth path plus Y0 anchoring plus the layer activation schedule.
   >
   > Run `/tam-analysis resume <TICKER>` and re-emit the hand-off, or provide the missing field inline.

   **3b. Hand-off contract test (per scenario).** For each scenario, verify the stated period CAGRs compound to the stated endpoint within 2%. If any scenario fails:

   > Bear case: hand-off CAGRs compound to $X.XB at Y`<N>`, but stated endpoint is $Y.YB (delta `<Z>`%). The CAGRs and endpoint disagree.
   >
   > Options:
   > (a) Revise TAM bear endpoint (`/tam-analysis resume <TICKER>`).
   > (b) Revise TAM bear CAGRs.
   > (c) Provide explicit annual revenue series for bear (overrides both).

   Do not pick silently. Force user choice. Do NOT silently rescale CAGRs to fit endpoint.

   **3c. Y1-3 anchor test.** Verify the **base** scenario's Y1-3 CAGR is within ±3pp of `aggregated.y1_3_guidance_anchor.midpoint`, OR carries a logged `override_reason`. Bear / low / high / bull must each carry their own `override_reason` describing the bear-mechanism / bull-adjacency intensity that drives the spread from base. Failure:

   > Base case Y1-3 CAGR is `<X>%`; management guidance midpoint is `<Y>%` (delta `<Z>pp`). No override_reason logged. The path starts off-anchor.
   >
   > Resolve in TAM: revise Y1-3 to within ±3pp of guidance, or log the mechanism justifying the deviation.

   **3d. Layer-schedule consistency.** Re-read `aggregated.layer_schedule_consistency_test`. Refuse to proceed if any of the 5 scenarios has unresolved violations. Surface the issue and require resolution in TAM.

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

## Step 2 — Mature Economics (Per Scenario)

The single most consequential DCF assumption set. Walk through per scenario (bear / low / base / high / bull):

1. **Mature EBIT margin**. Peer-anchored. Dispatch anchor-researcher for the relevant peer set (matched to the company's mix per the TAM hand-off). For multi-segment companies, sketch per-segment mature margin and aggregate by segment weight at maturity. All 5 scenario values. Monotonicity expected (bear ≤ low ≤ base ≤ high ≤ bull).
2. **Maintenance vs growth-oriented S&M and R&D**. For under-earning / heavily investing companies, separate the two explicitly. Mature S&M = maintenance only (renewals + replacement growth at sector-average pace). Mature R&D = sustaining + competitive parity, not greenfield expansion.
3. **Mature ROIC**. Per scenario (5 values). Persistent ROIC above WACC requires an explicit moat — name it. Without a named moat, ROIC fades to WACC over the horizon.
4. **Mature reinvestment rate**. Tied via `growth ≈ reinvestment rate × ROIC`. At maturity, real growth ≈ 0-1%, so reinvestment rate × ROIC should be small. Cross-check. All 5 scenarios.

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

WACC in this skill is framed as **required return**, not derived from CAPM. CAPM-derived betas are noisy, backward-looking, and produce a precise-looking number that obscures the fundamental question: *what real return do you require for taking equity risk, after adjusting for the currency you'll be paid back in and the jurisdiction you're exposed to?*

The framework is additive and transparent:

```
WACC ≈ required_real_return + reporting_currency_inflation + jurisdictional_risk_premium + sector_nudge
```

Step 4 walks through these four components, then applies the floor.

### 4a — Required Real Return (Anchor)

What you want to earn **after inflation**, in compensation for taking equity risk.

Default: **8%**. This matches the historical equity-risk-premium-implied real return for developed-market equities, but here it's a *preference*, not a derivation. You're saying "I require 8% real to deploy capital into a long-horizon equity claim."

Override only with a stated reason. Conservative buy-and-hold investors sometimes anchor at 6-7%; aggressive growth investors at 9-10%. Don't drop below 6% — that's not equity risk-taking, that's a savings account.

### 4b — Reporting Currency Inflation Anchor

The DCF outputs nominal dollars (or local-currency equivalent). The discount rate must contain the long-run inflation expectation for that currency:

| Currency | Long-run inflation anchor | Notes |
|----------|---------------------------|-------|
| USD / EUR / GBP / CAD / AUD / SGD | 2% | Central-bank targets, well-anchored |
| CHF | 1% | SNB target, historically undershoots |
| JPY | 1-2% | BoJ target, post-2022 trending higher |
| PLN / CZK / ILS | 3% | Stable EM, central-bank-targeted |
| MXN | 4% | Banxico target 3%, realized ~4-5% |
| RON / HUF | 5% | Mid-tier EM, persistent above-target |
| BRL / ZAR / INR / TRY (post-2025-recovery) | 5-7% | Mid-tier EM, BCB / SARB / RBI targeted but realized higher |
| TRY (current) / ARS / EGP | 15%+ | Fragile EM, anchoring on realized rather than targeted |

Anchor on the central bank's long-run target where credible; on the 10-year realized average where the target isn't credible.

### 4c — Jurisdictional Risk Premium

Equity in a Romania-listed company isn't the same risk as equity in a US-listed company even if the operations are identical. Currency convertibility, capital controls, judicial reliability, accounting integrity, political volatility — all real risks that don't go away just because the company has good unit economics.

| Jurisdiction tier | Examples | Premium |
|-------------------|----------|---------|
| Developed markets, deep capital markets | US, UK, EU-core, JP, CH, CA, AU, SG, KR | 0% |
| Stable EMs with reliable institutions | MX, PL, CZ, IL, TW, CL | 1-2% |
| Mid-tier EMs with idiosyncratic risk | RO, BR, IN, ID, ZA, MY, TH | 2-4% |
| Fragile EMs / political risk | TR, EG, AR, NG, VN, CN-post-2024 | 4-6% |
| Distressed / capital controls / sanctions | RU, IR, VE, MM | 6%+ or uninvestable |

Apply once per company at the listing-jurisdiction level. For multi-jurisdiction businesses (e.g., a US-listed company with 80% of revenue from Mexico + India), nudge upward by 1-2% to reflect the operating exposure.

### 4d — Sector / Business-Quality Nudge (Optional)

Last 0.5-1% adjustment for sector-specific risk. Optional — only use if the sector materially differs from average equity risk:

- **Regulated infrastructure / staples / utilities**: -0.5% to -1% (lower volatility, regulated returns).
- **Quality compounders with proven track record**: -0.5% (durable moat reduces risk).
- **High-growth unprofitable tech**: +0.5% to +1% (cash-burn risk).
- **Cyclical commodity / shipping / semis**: +1% to +2% (earnings volatility).
- **Speculative biotech / pre-revenue / single-product**: +2% to +3% (binary outcomes).
- **Micro-cap (< $500M)**: +0.5% to +1% (illiquidity).

Don't stack adjustments aggressively. If you find yourself adjusting +3% from a base of 10%, you're probably trying to make the DCF give a specific answer — push back on the assumption set instead.

### 4e — Compose + Floor

```
WACC = required_real_return + currency_inflation + jurisdiction_premium + sector_nudge
```

Apply the **8.5% floor (USD-equivalent)** unless exceptionally justified. The floor exists because long-duration equity claims need a minimum discount rate even for ultra-safe businesses — terminal-value math is too sensitive otherwise. For non-USD reporting currencies, the floor is `8.5% + (currency_inflation - 2%)` to keep the real-return basis consistent.

Show **both** the composed WACC and the used WACC if the floor is invoked.

### Reference Anchors (Sanity Check)

| Setup | Composed WACC | Real basis |
|-------|---------------|------------|
| USD-listed quality compounder (US ops) | 8% + 2% + 0% − 0.5% = **9.5%** | 8% real |
| USD-listed durable growth (US ops) | 8% + 2% + 0% + 0% = **10%** | 8% real |
| USD-listed speculative growth | 8% + 2% + 0% + 1% = **11%** | 8% real |
| USD-listed, 80% EM ops | 8% + 2% + 2% + 0% = **12%** | 8% real |
| RON-listed (Romania) durable growth | 8% + 5% + 2% + 0% = **15%** | 8% real |
| BRL-listed quality compounder | 8% + 6% + 3% − 0.5% = **16.5%** | 8% real |

If the user's company is USD-listed durable growth and they don't override, the default is **10%**. The skill announces the composition: "Defaulting to WACC = 10% (8% real + 2% USD inflation + 0% jurisdiction). Say so to override any component."

### Remaining DCF Mechanics

The rest of Step 4 follows after WACC is locked:

1. **Cost of debt** (only matters if material): current yield on the company's bonds, or BBB-rated equivalent + credit spread. After-tax = pre-tax × (1 − tax rate). For mostly-equity-financed growers, this barely moves the answer.
2. **Normalized tax rate**: long-run effective. US default ~25% (Federal 21% + state-adjusted).
3. **Capital structure weights**: target weights at maturity, not current. Growers tend toward 70-90% equity at maturity. WACC blends accordingly.
4. **Lease framework choice** — must pick ONE and apply consistently:
   - **Operating-cost approach**: lease payments stay in opex; lease liabilities excluded from EV bridge + capital. WACC uses equity + financial debt only.
   - **Capitalized approach**: ROU depreciation in D&A; lease capex in total capex; lease liabilities in EV bridge + WACC weights.
   - **Do not mix.** Frequent failure mode in real DCFs.
5. **SBC treatment**: real economic expense. Reverse any SBC-excluded "adjusted" margins from peer benchmarks. Avoid the double-count trap (expensing SBC in P&L AND counting dilution).
6. **Diluted share count**: current + economically relevant dilutive instruments (RSUs vesting, in-the-money options, convertibles at conversion).

### What the Skill Does NOT Do

- **Does not compute beta.** No `Cov(R_stock, R_market) / Var(R_market)` regression. Beta is a noisy backward-looking statistic that produces a falsely precise discount rate. The required-return framework is more honest.
- **Does not pull risk-free rate from current Treasury yields.** The DCF horizon is 25-40 years; a snapshot of the 10-year yield isn't the right input. The "risk-free baseline" is implicit in the required-real-return + currency-inflation composition.
- **Does not "build up" cost of equity from CAPM components.** Composed from preference + inflation + jurisdiction + sector. Transparent. Anchor-on-stuff-the-user-actually-controls.

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

The DCF skill inherits the no-magic-haircuts rule from `/tam-analysis`. Specifically:

- **No parallel "haircut base case"** alongside the bottom-up base. ONE bear / ONE low / ONE base / ONE high / ONE bull.
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
