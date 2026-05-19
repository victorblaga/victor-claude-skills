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

2. **Layer revenue today's $ (per scenario)**: `pool_at_maturity × mature_share × monetization_at_maturity_today_$`. Recompute for bear / low / base / high / bull.

3. **Real → nominal conversion**: `revenue_nominal = revenue_today_$ × (1 + inflation) ** years_to_layer_maturity`. Inflation rate must match `state.json` reporting currency anchor.

4. **Overlap haircut applied once, not twice**: confirm the haircut is in `layer_revenue_at_maturity_today_$` and not double-counted in the aggregated total later.

### Final Aggregation

Validate:

1. **Cross-layer sum**: `aggregated.revenue_at_maturity_today_$ = Σ over layers of layer_revenue_at_maturity_today_$ × (1 - overlap_haircut_amount)`. Per scenario (bear / low / base / high / bull).

2. **Real → nominal at hand-off horizon**: `aggregated.revenue_at_maturity_nominal = aggregated.revenue_at_maturity_today_$ × (1 + inflation) ** hand_off_horizon_years`. Cross-check against per-layer nominal contributions at the hand-off horizon (must reconcile to ±1% allowing for rounding).

3. **Per-layer contribution at hand-off horizon**: for each layer, contribution = mature revenue if layer_maturity ≤ hand_off_horizon, else still-ramping projection at hand_off_horizon. Verify.

4. **Y1-3 guidance anchor test.** Verify the **base** scenario's Y1-3 CAGR is within ±3pp of `aggregated.y1_3_guidance_anchor.midpoint`, OR carries an `override_reason`. The other scenarios (bear / low / high / bull) are not tolerance-checked against guidance — they take reasoned spreads from base, each with its own `override_reason` describing the bear-mechanism / bull-adjacency intensity. The anchor itself must exist — if `y1_3_guidance_anchor` is missing, halt and prompt main thread to dispatch anchor-researcher for it.

   ```python
   def y1_3_anchor_test(period_cagrs_per_scenario, guidance_anchor, override_reasons):
       # guidance_anchor: {"midpoint": float, "range": [float, float], "consensus_midpoint": float}
       # override_reasons: {scenario: str | None} — per-scenario logged mechanism (None if not logged)
       results = {}
       midpoint = guidance_anchor["midpoint"]
       for scenario in ("bear", "low", "base", "high", "bull"):
           pick = period_cagrs_per_scenario[scenario]["y1_3"]
           delta_pp = (pick - midpoint) * 100
           if scenario == "base":
               status = "passed" if abs(delta_pp) <= 3.0 else (
                   "override" if override_reasons.get("base") else "failed"
               )
           else:
               # Non-base scenarios: not tolerance-checked vs guidance.
               # MUST carry an override_reason describing the bear-mechanism /
               # bull-adjacency intensity that drives the spread from base.
               status = "passed" if override_reasons.get(scenario) else "failed"
           results[scenario] = {
               "pick": pick,
               "guidance_midpoint": midpoint,
               "delta_pp": delta_pp,
               "override_reason": override_reasons.get(scenario),
               "status": status,
           }
       return results
   ```

   Base out-of-tolerance without override → FAIL. Non-base scenario without `override_reason` → FAIL.

5. **Hand-off contract test**: per-scenario declared CAGRs compound to per-scenario endpoint within 2%.

   ```python
   def handoff_contract_test(rev_y0, period_cagrs_per_scenario, scenario_endpoints, maturity_year):
       period_years = {"y1_3": 3, "y4_5": 2, "y6_10": 5, "y11_20": 10, "y21_maturity": max(0, maturity_year - 20)}
       results = {}
       for scenario in ("bear", "low", "base", "high", "bull"):
           compounded = rev_y0
           for period, years in period_years.items():
               compounded *= (1 + period_cagrs_per_scenario[scenario][period]) ** years
           stated = scenario_endpoints[scenario]
           delta_pct = abs(compounded - stated) / stated
           results[scenario] = {
               "compounded_endpoint": compounded,
               "stated_endpoint": stated,
               "delta_pct": delta_pct,
               "status": "passed" if delta_pct < 0.02 else "failed",
           }
       return results
   ```

   Run for all 5 scenarios independently. Save results to `aggregated.handoff_contract_test`. FAIL if any scenario exceeds 2%.

6. **Layer-schedule consistency test.** For each scenario, verify the declared period CAGRs are compatible with the per-layer activation schedule. Two checks:

   - **Late-activator check**: a layer activating in period P contributing ≥15% of scenario endpoint requires the CAGR in P (and in the period containing `peak_contribution_year`) to be ≥ Y1-3 CAGR − 1pp. Otherwise the layer is invisible in the path.
   - **Smooth-fade check**: if NO layer activates after Y3 contributing ≥15% of scenario endpoint, post-Y3 CAGRs (Y4-5, Y6-10, Y11-20, Y21-maturity) must be monotonically non-increasing.

   ```python
   PERIODS = {"y1_3": (1, 3), "y4_5": (4, 5), "y6_10": (6, 10), "y11_20": (11, 20), "y21_maturity": (21, None)}
   PERIOD_ORDER = ["y1_3", "y4_5", "y6_10", "y11_20", "y21_maturity"]

   def period_containing(year, maturity_year):
       for period, (start, end) in PERIODS.items():
           end_eff = end if end is not None else maturity_year
           if start <= year <= end_eff:
               return period
       return None

   def layer_schedule_consistency(scenario, period_cagrs, layers, scenario_endpoint, maturity_year):
       violations = []
       late_activator_present = False
       for layer in layers:
           if scenario == "bear" and layer.get("speculative"):
               continue  # speculative layers off in bear
           sched = layer["activation_schedule"]
           act = sched["activation_year"]
           peak = sched["peak_contribution_year"]
           contrib = layer["layer_revenue_at_maturity_today_$"][scenario] / scenario_endpoint
           if contrib < 0.15:
               continue
           if act >= 4:
               late_activator_present = True
           for y in (act, peak):
               p = period_containing(y, maturity_year)
               if p in (None, "y1_3"):
                   continue
               if period_cagrs[p] < period_cagrs["y1_3"] - 0.01:
                   violations.append({
                       "layer": layer["id"],
                       "scenario": scenario,
                       "issue": (
                           f"Layer activates/peaks in {p} contributing {contrib:.0%} of endpoint, "
                           f"but {p} CAGR ({period_cagrs[p]:.1%}) is below Y1-3 CAGR "
                           f"({period_cagrs['y1_3']:.1%}) − 1pp. Layer is invisible in the growth path."
                       ),
                   })
       if not late_activator_present:
           for i, p in enumerate(PERIOD_ORDER[1:-1], start=1):
               prev = PERIOD_ORDER[i - 1]
               if period_cagrs[p] > period_cagrs[prev] + 0.005:
                   violations.append({
                       "scenario": scenario,
                       "issue": (
                           f"No layer activates after Y3 with ≥15% contribution, but {p} CAGR "
                           f"({period_cagrs[p]:.1%}) > {prev} CAGR ({period_cagrs[prev]:.1%}). "
                           f"Path requires monotone fade — declared CAGRs declare elevation with no layer behind it."
                       ),
                   })
       return violations
   ```

   Save to `aggregated.layer_schedule_consistency_test`. Surface violations to main thread for user resolution (revise CAGRs, revise layer contributions, or name an offsetting mechanism).

   Speculative layers: `layer_revenue_at_maturity_today_$.bear == 0` is a hard rule (validated separately). For low/base/high/bull, the speculative layer's contribution is whatever the per-layer analysis produced — no top-down weighting.

7. **Scenario monotonicity test.** Verify `bear < low < base < high < bull` for `aggregated.revenue_at_maturity_today_$` AND for each layer's `layer_revenue_at_maturity_today_$`. Strict inequalities (equality allowed only with a logged justification — e.g., layer is genuinely scenario-insensitive on that boundary, rare).

   ```python
   def scenario_monotonicity_test(layers, aggregated):
       order = ["bear", "low", "base", "high", "bull"]
       violations = []
       # Aggregated check
       agg = aggregated["revenue_at_maturity_today_$"]
       for i in range(len(order) - 1):
           if agg[order[i]] >= agg[order[i + 1]]:
               violations.append({
                   "scope": "aggregated",
                   "issue": f"{order[i]} ({agg[order[i]]:.3g}) >= {order[i+1]} ({agg[order[i+1]]:.3g})",
               })
       # Per-layer check
       for layer in layers:
           rev = layer["layer_revenue_at_maturity_today_$"]
           # Speculative layer: bear == 0 is hard rule, skip strict-monotonicity check on bear→low if low > 0.
           start_idx = 1 if layer.get("speculative") and rev["bear"] == 0 else 0
           for i in range(start_idx, len(order) - 1):
               if rev[order[i]] >= rev[order[i + 1]]:
                   violations.append({
                       "scope": f"layer:{layer['id']}",
                       "issue": f"{order[i]} ({rev[order[i]]:.3g}) >= {order[i+1]} ({rev[order[i+1]]:.3g})",
                   })
       return {"status": "passed" if not violations else "failed", "violations": violations}
   ```

   Save to `aggregated.scenario_monotonicity_test`. FAIL if any violation. Speculative layers separately satisfy `bear == 0`.

8. **Annual revenue series derivation.** For each scenario, derive the annual series via linear interpolation in growth-rate space, anchored on `aggregated.last_reported_yoy_growth` at Y0, with per-period renormalization to honor each stated CAGR exactly.

   ```python
   def interpolate_linear(anchors, x):
       # anchors: dict {x_position: rate}; linear interp between adjacent anchors
       xs = sorted(anchors.keys())
       if x <= xs[0]:
           return anchors[xs[0]]
       if x >= xs[-1]:
           return anchors[xs[-1]]
       for i in range(len(xs) - 1):
           if xs[i] <= x <= xs[i + 1]:
               t = (x - xs[i]) / (xs[i + 1] - xs[i])
               return anchors[xs[i]] * (1 - t) + anchors[xs[i + 1]] * t

   def renormalize_periods(series, period_cagrs, maturity_year):
       # For each period, scale the within-period rates by a constant factor
       # so that (series[end] / series[start]) ** (1 / years) - 1 == stated_cagr.
       period_bounds = [("y1_3", 0, 3), ("y4_5", 3, 5), ("y6_10", 5, 10),
                        ("y11_20", 10, 20), ("y21_maturity", 20, maturity_year)]
       adjusted = list(series)
       for period, start, end in period_bounds:
           if end > maturity_year:
               end = maturity_year
           if start >= end:
               continue
           target_ratio = (1 + period_cagrs[period]) ** (end - start)
           current_ratio = adjusted[end] / adjusted[start]
           scale_factor = target_ratio / current_ratio
           per_year_scale = scale_factor ** (1 / (end - start))
           # apply compounding adjustment, preserving series[start]
           running = adjusted[start]
           for y in range(start + 1, end + 1):
               raw_growth = adjusted[y] / adjusted[y - 1] - 1
               adjusted_growth = (1 + raw_growth) * per_year_scale - 1
               running *= (1 + adjusted_growth)
               adjusted[y] = running
       return adjusted

   def annual_series_from_period_cagrs(rev_y0, last_year_growth, period_cagrs, maturity_year):
       anchors = {
           0: last_year_growth,
           2: period_cagrs["y1_3"],
           4.5: period_cagrs["y4_5"],
           8: period_cagrs["y6_10"],
           15.5: period_cagrs["y11_20"],
           (21 + maturity_year) / 2: period_cagrs["y21_maturity"],
       }
       series = [rev_y0]
       for y in range(1, maturity_year + 1):
           g = interpolate_linear(anchors, y)
           series.append(series[-1] * (1 + g))
       series = renormalize_periods(series, period_cagrs, maturity_year)
       return series
   ```

   Run per scenario. Save results to `aggregated.annual_revenue_today_$_per_scenario` with a `_provenance` key noting the series is derived and regenerable from the CAGRs.

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

11. **Three-error check** (also surfaced in handoff):
    - Headline numbers reconcile to layer table (no silent haircut).
    - Real and inflation accounted for separately (no double-apply).
    - Declared per-scenario CAGRs are consistent with the layer activation schedule (verified by `layer_schedule_consistency_test`).

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

## What Not to Do

- Don't use bash arithmetic (`$((... ))`) or LLM-inline math. Always Python.
- Don't round intermediate values. Use full precision. Round only when reporting to user.
- Don't fix the state — only report. The main thread + user decide how to resolve discrepancies.
- Don't skip writing the log. The log is the audit trail for the analysis.
- Don't claim PASS when you couldn't compute a check (e.g., missing field). Mark `INCONCLUSIVE` and explain.

## Cleanup

Delete the temp Python script after writing the log, unless the check failed (preserve for debugging). The log itself stays in `~/.investing/companies/<TICKER>/<DATE>/.math-check.log`.
