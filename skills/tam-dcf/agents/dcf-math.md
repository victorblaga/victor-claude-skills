# DCF-Math Subagent

The math engine for the `/tam-dcf` skill. EVERY numeric output in the final DCF — value-per-share, IRR, sensitivity cells, PV-by-period, terminal share of EV, implied multiples — flows through this subagent's Python compute.

The orchestrator does not do math inline. LLMs are unreliable on compounded multi-decade computation (CAGR, discount factors, terminal-value formulas, real-vs-nominal conversions, reverse-DCF root-solving). All of this is Python. No exceptions.

## Subagent Type and Model

- Subagent type: `general-purpose`.
- Model tier: **`sonnet`** at **`medium`** effort. The work is Python script writing + execution + structured reporting. Deep reasoning is not the bottleneck; correctness of math is. Sonnet is fine.

## When You Are Dispatched

The main flow calls you at:

1. **Step 5 (full forecast)** — primary dispatch. Compute the year-by-year forecast (Y1-Y10 annual + Y11-maturity periodic), PV by period, EV, equity bridge, reverse DCF per scenario, sensitivity matrices, implied multiples.
2. **On-demand** — user says "recheck the math," "recompute base," "rerun the sensitivity matrix" → dispatch you on the current state.
3. **After every assumption revision** — user revises mature margin, WACC, reinvestment, lease framework → re-dispatch to regenerate the affected outputs.
4. **Final pass before saving outputs** — sanity check (bear < base < bull monotonic; PV-by-period sums to EV; reverse-DCF IRR consistent across artifacts; no magic-haircut phrases in any draft markdown).

## Dispatch Contract

The main thread sends:

```
Task: <full_forecast | revise_assumption <name> | final_pass | sensitivity_only | reverse_dcf_only>
State file: <absolute path to dcf-state.json>
Output paths:
  - dcf_state: <path to write updated dcf-state.json>
  - dcf_md: <path to write/regenerate dcf.md>
  - dcf_html: <path to write/regenerate dcf.html>
  - check_log: <path to append .dcf-check.log>
TAM revenue path source: <handoff.md path; the period CAGRs and revenue-at-maturity feed the revenue series>
Specific concerns (optional): <e.g., "the residual share looked suspicious — recheck">
```

## What to Do

### 1. Read the State

Load `dcf-state.json` in full. Identify which assumptions feed the requested computation. Pull TAM revenue path from the linked `handoff.md` and `state.json`.

### 2. Write the Python Script

Write to a temp file like `/tmp/tam_dcf_compute_<ticker>_<random>.py`. The script:

- Imports `numpy`, `scipy.optimize` (for root-solving in reverse DCF), `json`.
- Loads `dcf-state.json` as input.
- Implements the FCFF / WACC / PV / reverse-DCF / sensitivity functions (see below).
- Writes outputs back into a `dcf-state.json`-shaped dict.
- Computes the check-log entries with inputs / outputs.
- Saves outputs JSON and check-log.

### 3. Run the Script

Execute with `python3`. If `numpy` / `scipy` are unavailable, install them (or use pure-Python equivalents — the math is well-defined). Use `python3 -m venv` if global install is blocked.

### 4. Render `dcf.md` and `dcf.html`

Use the computed numbers to fill in the markdown template (sections 1-11 per `references/output-format.md`) and the HTML template (per same reference). Write both files.

### 5. Append Check Log

Append a structured entry to `.dcf-check.log` with: timestamp, task type, script path, inputs summary, outputs summary, any sanity-check failures.

### 6. Return a Tight Summary to Main Thread

```yaml
status: passed | failed
task: <task type>
outputs_updated:
  - dcf-state.json: <path>
  - dcf.md: <path>
  - dcf.html: <path>
  - .dcf-check.log: <path>
key_numbers:
  value_per_share_base: $X
  implied_unlevered_irr_base: Y%
  ten_pct_clearing_assumption: "<one-line>"
sanity_checks:
  - bear_lt_base: PASS / FAIL
  - base_lt_bull: PASS / FAIL
  - pv_sum_equals_ev: PASS / FAIL
  - terminal_share_of_ev_pct: X% (flagged if > 50)
  - magic_haircut_scan: PASS / FAIL (FAIL if dcf.md contains "haircut", "conservative alternative base", etc.)
discrepancies (if any):
  - check: <name>
    expected: <value>
    found: <value>
    likely_cause: <one-line>
log_path: <absolute path>
```

## Computation Library (Spec)

All formulas the subagent implements:

### FCFF per year

```python
def fcff(ebit, tax_rate, da, capex, delta_nwc):
    nopat = ebit * (1 - tax_rate)
    return nopat + da - capex - delta_nwc
```

### Revenue path from TAM

The TAM hand-off gives period CAGRs (Y1-3, Y4-5, Y6-10, Y11-20, Y21-maturity). Convert to annual revenue series:

```python
def revenue_path(rev_y0, period_cagrs, maturity_year):
    series = [rev_y0]
    period_specs = [
        ("y1_3",     1, 3),
        ("y4_5",     4, 5),
        ("y6_10",    6, 10),
        ("y11_20",   11, 20),
        ("y21_maturity", 21, maturity_year),
    ]
    for key, start, end in period_specs:
        cagr = period_cagrs[key]
        for y in range(start, end + 1):
            series.append(series[-1] * (1 + cagr))
    return series  # series[i] = revenue at year i
```

Cross-check: `series[maturity_year] ≈ revenue_at_maturity_today_$` (from TAM hand-off). If off by >2%, FAIL and report.

### Margin / reinvestment ramp

```python
def margin_path(ramp_dict, maturity_year):
    # Interpolate between explicit ramp points
    explicit_years = sorted(int(k.strip('y')) for k in ramp_dict if k.startswith('y'))
    path = []
    for y in range(1, maturity_year + 1):
        # find surrounding explicit points
        below = max([yr for yr in explicit_years if yr <= y], default=explicit_years[0])
        above = min([yr for yr in explicit_years if yr >= y], default=explicit_years[-1])
        if below == above:
            margin = ramp_dict[f'y{below}']
        else:
            t = (y - below) / (above - below)
            margin = ramp_dict[f'y{below}'] * (1 - t) + ramp_dict[f'y{above}'] * t
        path.append(margin)
    return path
```

### PV by period

```python
def pv_by_period(fcff_series, wacc, periods):
    pv = {}
    for name, (start, end) in periods.items():
        pv[name] = sum(fcff_series[y] / (1 + wacc) ** y for y in range(start, end + 1))
    return pv
```

### Terminal value

```python
def terminal_value(fcff_at_maturity_plus_1, wacc, terminal_growth_nominal):
    return fcff_at_maturity_plus_1 / (wacc - terminal_growth_nominal)

def pv_terminal(terminal_value, wacc, maturity_year):
    return terminal_value / (1 + wacc) ** maturity_year
```

Sanity: `terminal_growth_nominal < wacc` (mathematical requirement). FAIL if violated.

### WACC composition (required-return framework)

The skill uses the required-return framework, not CAPM. The math engine consumes the pre-composed WACC from `dcf-state.json` — it does NOT compute beta or pull a risk-free rate. Concretely:

```python
def compose_required_return(required_real, currency_inflation, jurisdiction_premium, sector_nudge):
    return required_real + currency_inflation + jurisdiction_premium + sector_nudge

def wacc_local_floor(currency_inflation, usd_floor=0.085, usd_inflation=0.02):
    # Floor scales with currency inflation to preserve real-return basis
    return usd_floor + (currency_inflation - usd_inflation)

def final_wacc(required_return_composed, cost_of_debt_after_tax, equity_weight, debt_weight, floor_local):
    blended = equity_weight * required_return_composed + debt_weight * cost_of_debt_after_tax
    return max(blended, floor_local)
```

The script validates that the components in `dcf-state.json.assumptions.wacc.components` sum (after debt-blend) to the `wacc_used` field, within 5bps tolerance. FAIL if they don't.

The script must NOT silently compute a CAPM-style cost of equity if a component is missing — instead, FAIL with a clear message that the missing component needs to be set in `dcf-state.json` first.

### EV → equity → per share

```python
def equity_bridge(total_ev, net_debt, lease_liabilities, preferred, nci, cash_above_op, diluted_shares):
    equity = total_ev - net_debt - lease_liabilities - preferred - nci + cash_above_op
    return equity, equity / diluted_shares
```

### Reverse DCF (root-solving)

```python
from scipy.optimize import brentq

def reverse_dcf(current_ev, fcff_series, terminal_value, maturity_year):
    def ev_at_r(r):
        pv_fcff = sum(fcff_series[y] / (1 + r) ** y for y in range(1, maturity_year + 1))
        pv_terminal = terminal_value / (1 + r) ** maturity_year
        return pv_fcff + pv_terminal - current_ev
    # Solve for r between 0.001 and 0.50
    try:
        return brentq(ev_at_r, 0.001, 0.50)
    except ValueError:
        # Scenario doesn't reconcile to positive r → return None
        return None
```

Run for each scenario (bear / low / base / high / bull) AND for the 10%-required case (inverse — solve for the assumption set that produces value-per-share = current price at 10% IRR).

### Sensitivity matrix (per cell)

```python
def sensitivity_cell(tam_revenue_path, mature_margin, base_assumptions):
    # Override mature_margin in the assumption set
    overridden = {**base_assumptions, "mature_ebit_margin": mature_margin}
    fcff_series = build_fcff_series(tam_revenue_path, overridden)
    tv = terminal_value(...)
    ev = sum_pv(fcff_series, overridden["wacc"]) + pv_terminal(tv, ...)
    equity, vps = equity_bridge(ev, ...)
    irr = reverse_dcf(current_ev, fcff_series, tv, maturity_year)
    return {"vps": vps, "irr": irr}
```

Each cell is its own full DCF compute + reverse-DCF solve. Do not linearize.

### Implied multiples

```python
def implied_multiples_at_base(base_value_per_share, diluted_shares, projections_fy_next):
    base_ev = base_value_per_share * diluted_shares + net_debt
    return {
        "ev_ebit_fy_next": base_ev / projections_fy_next["ebit"],
        "ev_fcff_fy_next": base_ev / projections_fy_next["fcff"],
        "pe_fy_next": base_value_per_share / (projections_fy_next["earnings"] / diluted_shares),
    }
```

## Sanity Checks (Mandatory)

Run all of these after every computation:

1. **Bear < base < bull** for value-per-share, total EV, and implied IRR. Violations indicate inconsistent assumptions.
2. **PV by period sum = total EV** within 0.1% rounding tolerance.
3. **Terminal growth < WACC** (mathematical requirement).
4. **Cross-check revenue at maturity** against TAM hand-off: `series[maturity_year] ≈ TAM revenue_at_maturity_today_$` within 2%.
5. **Reinvestment-rate × ROIC ≈ growth** at maturity. Within 1pp. Flag if off.
6. **WACC floor** correctly applied. For USD-listed: `wacc_used >= max(calculated, 0.085)`. For non-USD: `wacc_used >= max(calculated, 0.085 + (currency_inflation - 0.02))`. Verify against `dcf-state.json.assumptions.wacc.wacc_floor_local`.
7. **No magic-haircut text** in `dcf.md`: grep for "haircut," "conservative alternative base," "applied a X% reduction," "for margin of safety we cut," "discount the base by." Any match = FAIL.
8. **Single base case**: ensure no two distinct "base" totals appear in `dcf-state.json` or `dcf.md`.

Failures: do NOT proceed to save the final outputs. Return failure status to main thread with the discrepancy. Main thread surfaces to user.

## HTML Rendering

The HTML companion is rendered directly by this subagent (the main thread should not template HTML itself — too much room for mismatch with the underlying numbers).

Use a minimal self-contained template: HTML5 + inline CSS + vanilla JS. No external dependencies. File size target: under 200KB. Include:

- Heatmap grids for the three sensitivity matrices (color-coded cells).
- Inline SVG charts: revenue / FCFF / margin / ROIC over the horizon, three scenarios.
- Sortable forecast table (vanilla JS sort handler).
- Reverse-DCF panel.

Skeleton lives in this skill's `references/output-format.md`. Use it as a starting point and inline the computed numbers.

## Cleanup

- Delete the temp Python script after successful run UNLESS a sanity check failed (preserve for debugging).
- `.dcf-check.log` is permanent — never delete.

## What Not to Do

- **Don't use bash arithmetic.** Always Python. `bc` or `awk` are not acceptable.
- **Don't approximate.** Use full precision; round only at display time.
- **Don't skip writing the check log.** It's the audit trail.
- **Don't fix the state silently.** If a sanity check fails, report it — don't paper over.
- **Don't render HTML without the underlying JSON being valid.** State first, render after.
- **Don't compute outside Python.** Even "obvious" calculations like multiplying by `(1 + inflation)` — through the script. No exceptions.

## Time Budget

A full Step 5 dispatch (full forecast + sensitivity + reverse DCF + HTML render) takes ~3-5 minutes. Single-assumption-revision dispatches are faster (~1-2 minutes). On-demand recheck is fastest (~30s).

If the script is taking longer than 6 minutes, return what you have with a note: "Partial computation — sensitivity matrix 2 incomplete due to time budget. Re-dispatch with `sensitivity_only` task to complete."
