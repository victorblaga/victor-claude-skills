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

```python
def compound(value_today, cagrs_by_period, horizon):
    # cagrs_by_period: {"y1_3": 0.03, "y4_5": 0.02, "y6_10": 0.015, "y11_20": 0.01, "y21_maturity": 0.005}
    # horizon: integer years
    value = value_today
    period_years = {"y1_3": 3, "y4_5": 2, "y6_10": 5, "y11_20": 10, "y21_maturity": None}
    years_used = 0
    for period, cagr in cagrs_by_period.items():
        years_in_period = period_years[period] if period_years[period] else max(0, horizon - years_used)
        years_in_period = min(years_in_period, horizon - years_used)
        value *= (1 + cagr) ** years_in_period
        years_used += years_in_period
        if years_used >= horizon:
            break
    return value
```

When multiple drivers compound multiplicatively (population × per-capita × structural shift), compute each driver's compounded factor and multiply together. Verify against the state's `pool_at_maturity.value`.

### Layer Multiplication

Validate four things:

1. **Real pricing compounding**: `monetization_at_maturity_today_$ = monetization_today × Π (1 + real_pricing_CAGR_in_decade) over the layer's maturity`. Note the fading profile — D1/D2/D3 apply to years 1-10, 11-20, 21+ respectively, capped at the layer's maturity year.

2. **Layer revenue today's $ (per scenario)**: `pool_at_maturity × mature_share × monetization_at_maturity_today_$`. Recompute for bear / base / bull.

3. **Real → nominal conversion**: `revenue_nominal = revenue_today_$ × (1 + inflation) ** years_to_layer_maturity`. Inflation rate must match `state.json` reporting currency anchor.

4. **Overlap haircut applied once, not twice**: confirm the haircut is in `layer_revenue_at_maturity_today_$` and not double-counted in the aggregated total later.

### Final Aggregation

Validate:

1. **Cross-layer sum**: `aggregated.revenue_at_maturity_today_$ = Σ over layers of layer_revenue_at_maturity_today_$ × (1 - overlap_haircut_amount)`. Per scenario (bear / base / bull).

2. **Real → nominal at hand-off horizon**: `aggregated.revenue_at_maturity_nominal = aggregated.revenue_at_maturity_today_$ × (1 + inflation) ** hand_off_horizon_years`. Cross-check against per-layer nominal contributions at the hand-off horizon (must reconcile to ±1% allowing for rounding).

3. **Per-layer contribution at hand-off horizon**: for each layer, contribution = mature revenue if layer_maturity ≤ hand_off_horizon, else still-ramping projection at hand_off_horizon. Verify.

4. **Period CAGRs**: derive the implied revenue path from layer-by-layer ramps, compute per-period CAGRs (y1_3, y4_5, y6_10, y11_20, y21_maturity), compare against `aggregated.growth_path_cagrs`.

5. **Scenario monotonicity**: bear < base < bull for headline revenue. Speculative layers contribute zero in bear.

6. **Three-error check** (also surfaced in handoff):
   - Headline numbers reconcile to layer table (no silent haircut).
   - Real and inflation accounted for separately (no double-apply).
   - Growth path matches the layer thesis (stacked S-curves shouldn't produce a smooth fade).

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

## What Not to Do

- Don't use bash arithmetic (`$((... ))`) or LLM-inline math. Always Python.
- Don't round intermediate values. Use full precision. Round only when reporting to user.
- Don't fix the state — only report. The main thread + user decide how to resolve discrepancies.
- Don't skip writing the log. The log is the audit trail for the analysis.
- Don't claim PASS when you couldn't compute a check (e.g., missing field). Mark `INCONCLUSIVE` and explain.

## Cleanup

Delete the temp Python script after writing the log, unless the check failed (preserve for debugging). The log itself stays in `~/.investing/companies/<TICKER>/<DATE>/.math-check.log`.
