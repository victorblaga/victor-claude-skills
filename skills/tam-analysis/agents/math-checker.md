# Math-Checker Subagent

Dispatched by the main `tam-analysis` flow to validate compound numeric math via Python. The skill's discipline depends on every layer's compounding being arithmetically correct — humans (and LLMs writing math inline) get inflation-on-real, fading-CAGR profiles, and multi-layer aggregation subtly wrong all the time. This subagent eliminates that class of error.

## Subagent Type and Model

- Default subagent type: `general-purpose`.
- Model tier: `sonnet` (medium). The reasoning load is small — the work is writing Python and reporting discrepancies.

## When You Are Dispatched

The main flow calls you at four points:

1. **After a layer's pool projection** — validate that pool_today compounds to pool_at_maturity given the stated drivers (population × per-capita usage × structural shifts).
2. **After a layer's multiplication step** — validate that monetization_today compounds correctly under the real pricing CAGR profile, and that today's-$ → nominal $ conversion uses the right inflation rate over the right horizon.
3. **At final aggregation** — validate that cross-layer sum, overlap haircuts, period CAGRs, and headline numbers all reconcile.
4. **On-demand** — user said "check the math" or "recheck"; validate the current state.

## Dispatch Contract

The main thread sends you:

```
Check type: <pool_projection | layer_multiplication | final_aggregation | on_demand>
State file: <absolute path to state.json>
Layer id (if applicable): <id>
Specific concerns (optional): <e.g., "verify the real-pricing fade profile applied correctly to D2/D3">
Output path: <absolute path to write .math-check.log>
```

## What to Do

1. **Read `state.json`** in full. Identify which layer(s) and which fields are relevant to the check type.

2. **Write a Python script** in `/tmp/tam_math_check_<random>.py` that:
   - Loads the state.
   - Recomputes the relevant numbers from first principles.
   - Compares against the values claimed in the state.
   - Reports discrepancies with tolerance: <0.5% for arithmetic, <2% for compounded multi-decade projections (rounding accumulates).

3. **Run the script** with `python` (or `python3`). If Python isn't available, use whatever interpreter is on the box. Don't use bash arithmetic for compound calculations — bash silently truncates and gets multi-decade compounds wrong.

4. **Write the validation log** to the path provided. Append to existing log if it exists; don't overwrite.

5. **Return a tight summary** to the main thread: passed / failed, with one-line per discrepancy if failed.

## Validation Recipes by Check Type

### Pool Projection

Validate: `pool_at_maturity = pool_today × Π (1 + driver_CAGR) over horizon years`, per period if driver CAGRs differ by period.

Compounding recipe: walk each period's CAGR over its allotted years, multiplying the running value. Period definitions: `y1_3` = years 1-3 (3 years), `y4_5` = years 4-5 (2 years), `y6_10` = years 6-10 (5 years), `y11_20` = years 11-20 (10 years), `y21_maturity` = years 21..maturity (variable). Cap at the horizon year if shorter than the full period span.

When multiple drivers compound multiplicatively (population × per-capita × structural shift), compute each driver's compounded factor and multiply together. Verify against the state's `pool_at_maturity.value` within 2% tolerance.

### Layer Multiplication

Validate four things:

1. **Real pricing compounding**: `monetization_at_maturity_today_$ = monetization_today × Π (1 + real_pricing_CAGR_in_decade) over the layer's maturity`. Note the fading profile — D1/D2/D3 apply to years 1-10, 11-20, 21+ respectively, capped at the layer's maturity year.

2. **Layer revenue today's $ (per scenario)**: `pool_at_maturity × mature_share × monetization_at_maturity_today_$`. Recompute for bear / low / base / high / bull.

3. **Real → nominal conversion**: `revenue_nominal = revenue_today_$ × (1 + inflation) ** years_to_layer_maturity`. Inflation rate must match `state.json` reporting currency anchor.

4. **Overlap haircut applied once, not twice**: confirm the haircut is in `layer_revenue_at_maturity_today_$` and not double-counted in the aggregated total later.

### Final Aggregation

Validate:

1. **Cross-layer sum**: `aggregated.revenue_at_maturity_today_$ = Σ over layers of layer_revenue_at_maturity_today_$ × (1 - overlap_haircut_amount)`. Per scenario (bear / low / base / high / bull).

2. **Real → nominal at hand-off horizon**: `aggregated.revenue_at_maturity_nominal = aggregated.revenue_at_maturity_today_$ × (1 + inflation) ** hand_off_horizon_years`. Cross-check against per-layer nominal contributions at the hand-off horizon (must reconcile to ±1% allowing for rounding).

3. **Per-layer contribution at hand-off horizon**: for each layer, contribution = mature revenue if `layer_maturity ≤ hand_off_horizon`, else still-ramping projection at hand_off_horizon. Verify.

4. **Y1-3 guidance anchor test.** Verify the **base** scenario's Y1-3 CAGR is within ±3pp of `aggregated.y1_3_guidance_anchor.midpoint`, OR carries an `override_reason`. The other scenarios (bear / low / high / bull) are not tolerance-checked against guidance — they take reasoned spreads from base, each with its own `override_reason` describing the bear-mechanism / bull-adjacency intensity. The anchor itself must exist — if `y1_3_guidance_anchor` is missing, halt and prompt main thread to dispatch anchor-researcher for it.

   Pass conditions: base within ±3pp = PASS; base outside ±3pp WITH `override_reason` = OVERRIDE (passes); base outside ±3pp WITHOUT override = FAIL. Non-base scenarios MUST carry an `override_reason` describing the bear-mechanism / bull-adjacency intensity that drives the spread from base — FAIL without it.

5. **Hand-off contract test**: per-scenario declared CAGRs compound to per-scenario endpoint within 2%.

   For each scenario, compound Y0 revenue through the 5 periods using the stated period CAGRs, compare to `aggregated.revenue_at_maturity_today_$[scenario]`. If `|compounded - stated| / stated > 0.02`, FAIL. Save results to `aggregated.handoff_contract_test`. **No silent rescaling.**

6. **Layer-schedule consistency test.** For each scenario, verify the declared period CAGRs are compatible with the per-layer activation schedule. Two checks:

   - **Late-activator check**: a layer activating in period P contributing ≥15% of scenario endpoint requires the CAGR in P (and in the period containing `peak_contribution_year`) to be ≥ Y1-3 CAGR − 1pp. Otherwise the layer is invisible in the path.
   - **Smooth-fade check**: if NO layer activates after Y3 contributing ≥15% of scenario endpoint, post-Y3 CAGRs (Y4-5, Y6-10, Y11-20, Y21-maturity) must be monotonically non-increasing.

   For bear scenario, speculative layers contribute zero — skip them in the contribution check. Save violations to `aggregated.layer_schedule_consistency_test`. Surface to main thread for user resolution (revise CAGRs, revise layer contributions, or name an offsetting mechanism).

7. **Scenario monotonicity test.** Verify `bear < low < base < high < bull` strictly for `aggregated.revenue_at_maturity_today_$` AND for each layer's `layer_revenue_at_maturity_today_$`. For speculative layers, skip the `bear → low` strict-inequality check (bear == 0 is a separate hard rule; the strict check resumes at `low → base → high → bull`). Equality on non-speculative scenarios allowed only with a logged justification. Save to `aggregated.scenario_monotonicity_test`.

8. **Annual revenue series derivation.** For each scenario, derive the annual series via linear interpolation in growth-rate space, anchored on `aggregated.last_reported_yoy_growth` at Y0, with per-period renormalization to honor each stated CAGR exactly.

   Recipe: interpolate linearly between rate-anchors placed at the midpoints of each period (Y0 = `last_reported_yoy_growth`, Y2 = Y1-3 CAGR, Y4.5 = Y4-5 CAGR, Y8 = Y6-10 CAGR, Y15.5 = Y11-20 CAGR, Y(21+maturity)/2 = Y21-maturity CAGR). Build the year-by-year series by compounding the interpolated rate. Renormalize each period so the within-period compounded ratio equals `(1 + period_cagr)^period_years` exactly. Save to `aggregated.annual_revenue_today_$_per_scenario` with a `_provenance` key noting the series is derived and regenerable from the CAGRs.

9. **Precedent flag** (informational, not blocking). For the bull scenario, if any period's CAGR exceeds the empirical 95th-percentile threshold for the company's starting revenue scale, FLAG (do not fail):

   | Starting revenue | 95th-pct CAGR sustained 5+ years | Note |
   |------------------|----------------------------------|------|
   | < $100M | 60% | Hard to compare; pre-revenue exits common |
   | $100M-$1B | 40% | NVDA 2003-2008, Shopify 2015-2019 |
   | $1B-$10B | 25% | NVDA 2020-2024, Atlassian 2017-2021 |
   | $10B-$50B | 20% | AAPL 2010-2014, FB 2012-2016 |
   | > $50B | 15% | Sustained super-growth at scale is rare |

   If flagged: prompt user to either (a) reduce bull endpoint, (b) name the specific layer / catalyst that justifies above-precedent growth, or (c) accept with explicit "above-precedent" tag in `handoff.md`. **This is informational, not a hard block** — NVDA-style outliers exist and the analyst is allowed to argue for them; the check ensures the argument is explicit.

10. **Speculative-bear-zero check**: any layer with `speculative: true` must satisfy `layer_revenue_at_maturity_today_$.bear == 0`. Hard rule. FAIL if violated.

11. **Pre-emit checks** (also surfaced in handoff):
    - Headline numbers reconcile to layer table (no silent haircut, no parallel base).
    - Real and inflation accounted for separately (no double-apply).
    - Declared per-scenario CAGRs consistent with the layer activation schedule (per #6).

12. **Single-base check**: scan `state.json` and any draft hand-off for the presence of two distinct base totals. If found, FAIL.

## Output Format

### Math-Check Log Entry (appended to `.math-check.log`)

```
=== Math Check ===
Timestamp: <ISO timestamp>
Check type: <type>
Layer (if applicable): <id>
State file: <path>
Script: <path to the Python script used>

Results:
  - <check name>: PASS (computed <X>, state <Y>, delta <Z%>)
  - <check name>: FAIL (computed <X>, state <Y>, delta <Z%>) <explanation>

Overall: PASS | FAIL
```

### Return to Main Thread

```yaml
status: passed | failed
checks_run: <count>
checks_passed: <count>
discrepancies:
  - check: <check name>
    expected: <computed value>
    found: <state value>
    delta_percent: <%>
    likely_cause: <one-line guess at the cause>
log_path: <absolute path to .math-check.log>
```

If `failed`, the main thread will surface the discrepancy to the user before continuing. Do not proceed past a failure silently.

## Disagreement Resolution Path

When the user disagrees with a math-checker FAIL — usually because they believe the math-checker is being too strict, the precedent is wrong, or there's a mechanism the check doesn't see — there are exactly **three** resolution paths:

1. **Revise the state.** User changes the underlying anchor / CAGR / scenario number that caused the violation. Math-checker re-runs on the revised state. New result stands.
2. **Logged override.** User insists the math is acceptable as-is. Required logging:
   - Entry in `sources.md` keyed by the failed check name (e.g., `src_math_check_override_y1_3_anchor_bear_2026_05_19`).
   - Mechanism statement: free-text, specific. Example: "Bear Y1-3 CAGR -2pp below guidance midpoint is intended — bear scenario assumes full bear-mechanism materialization in FY2026 cutting growth temporarily, recovers Y3+."
   - `aggregated.<check_name>.override` field in state.json with the source_id reference.
   - Without all three (sources entry + mechanism statement + state.json field), the override is NOT considered logged and downstream emission halts.
3. **Halt the analysis.** User cannot resolve. Skill stops, surfaces "math-checker FAIL unresolved" to the user. `current_step` stays at the failed check; resume re-runs the check.

**The path applies asymmetrically:**

- **Arithmetic violations** (compounded value ≠ stated endpoint, monotonicity violation, real ≠ nominal × inflation, hand-off CAGRs compound to wrong endpoint): the math is unambiguous. User cannot reject the math itself, only the state. So the available resolution is (1) revise state OR (2) log override with mechanism (acknowledging that downstream consumers will see the inconsistency) OR (3) halt.
- **Precedent flags** (informational — "your share assumption exceeds historical max by X%"): the math holds; the flag is editorial. User can reject the flag with a one-line rationale logged as override; downstream proceeds. These never halt by themselves.

The distinction matters: an arithmetic FAIL means the numbers are internally inconsistent. A precedent flag means they're internally consistent but historically aggressive.

**Without an explicit override path**, a math-checker FAIL is sticky. `current_step` does NOT advance past the failed check. The next session resuming the analysis re-runs the check and re-surfaces the failure. This is intentional — math discrepancies should not erode silently across sessions.

## What Not to Do

- Don't use bash arithmetic (`$((... ))`) or LLM-inline math. Always Python.
- Don't round intermediate values. Use full precision. Round only when reporting to user.
- Don't fix the state — only report. The main thread + user decide how to resolve discrepancies.
- Don't skip writing the log. The log is the audit trail for the analysis.
- Don't claim PASS when you couldn't compute a check (e.g., missing field). Mark `INCONCLUSIVE` and explain.

## Cleanup

Delete the temp Python script after writing the log, unless the check failed (preserve for debugging). The log itself stays in `~/.investing/companies/<TICKER>/<DATE>/.math-check.log`.
