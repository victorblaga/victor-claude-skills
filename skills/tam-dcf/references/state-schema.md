# DCF State Schema

The DCF skill writes its session state to `dcf-state.json` alongside the existing TAM artifacts. This file is the resume contract + the input to dcf-math + the source from which `dcf.md` and `dcf.html` are regenerated.

Files in `~/.investing/companies/<TICKER>/<DATE>/`:

| File | Owner | Read/Write |
|------|-------|------------|
| `handoff.md` | TAM | read-only here |
| `state.json` | TAM | read-only here |
| `sources.md` | shared | append (DCF anchors land here too) |
| `dialogue.md` | shared | append (DCF dialogue continues here) |
| `dcf-state.json` | DCF | this skill writes |
| `dcf.md` | DCF | this skill writes |
| `dcf.html` | DCF | this skill writes |
| `.dcf-check.log` | DCF (math-checker) | this skill writes |

## `dcf-state.json`

```json
{
  "schema_version": "1.0",
  "tam_session": {
    "handoff_path": "/home/victor/.investing/companies/IOT/2026-05-18/handoff.md",
    "state_path": "/home/victor/.investing/companies/IOT/2026-05-18/state.json",
    "horizon_year": "Y25",
    "maturity_calendar_year": 2051,
    "revenue_at_maturity_today_$": {
      "bear": 4800000000,
      "low":  8100000000,
      "base": 13700000000,
      "high": 21500000000,
      "bull": 35900000000
    },
    "revenue_at_maturity_nominal_$": {
      "bear": 7880000000,
      "low":  13290000000,
      "base": 22470000000,
      "high": 35260000000,
      "bull": 58880000000
    },
    "inflation_assumption_pct": 0.02,
    "last_reported_revenue_today_$": 2330000000,
    "last_reported_yoy_growth": 0.092,
    "y1_3_guidance_anchor": {"midpoint": 0.095, "range": [0.085, 0.105], "consensus_midpoint": 0.093},
    "growth_shape_per_scenario": {
      "bear": "smooth_fade",
      "low":  "smooth_fade",
      "base": "stay_elevated",
      "high": "stay_elevated",
      "bull": "stay_elevated"
    },
    "peak_growth_year_per_scenario": {"bear": 1, "low": 3, "base": 4, "high": 6, "bull": 8},
    "period_cagrs_per_scenario": {
      "bear": {"y1_3": 0.04, "y4_5": 0.05, "y6_10": 0.05, "y11_20": 0.04, "y21_maturity": 0.02},
      "low":  {"y1_3": 0.07, "y4_5": 0.08, "y6_10": 0.08, "y11_20": 0.07, "y21_maturity": 0.04},
      "base": {"y1_3": 0.095, "y4_5": 0.105, "y6_10": 0.10, "y11_20": 0.09, "y21_maturity": 0.05},
      "high": {"y1_3": 0.11, "y4_5": 0.13, "y6_10": 0.14, "y11_20": 0.11, "y21_maturity": 0.055},
      "bull": {"y1_3": 0.13, "y4_5": 0.17, "y6_10": 0.19, "y11_20": 0.15, "y21_maturity": 0.06}
    },
    "dominant_drivers": [
      {"name": "L1 mature share", "range": [0.18, 0.28, 0.40]},
      {"name": "SP-A monetization", "range": [1.3e9, 8.1e9, 18.7e9]},
      {"name": "L1 mature ASP", "range": [631, 1236, 1950]}
    ],
    "consistency_check": "passed | failed",
    "consistency_notes": [
      "No two-bases pathology",
      "Per-scenario CAGRs compound to per-scenario endpoint (handoff contract test PASS, 5 scenarios)",
      "Y1-3 anchor test PASS (base within ±3pp of guidance; bear/low/high/bull with override_reason)",
      "Layer-schedule consistency PASS (5 scenarios)",
      "Scenario monotonicity PASS (bear < low < base < high < bull)"
    ]
  },
  "data_snapshot": {
    "as_of_date": "2026-05-18",
    "current_price": 38.50,
    "currency": "USD",
    "diluted_shares_M": 567.2,
    "market_cap_$": 21837000000,
    "net_debt_$": -800000000,
    "ev_$": 21037000000,
    "ttm_revenue_$": 1618600000,
    "ttm_ebit_$": -52600000,
    "ttm_ebit_margin": -0.0325,
    "ttm_fcff_$": 80000000,
    "ttm_roic": -0.04,
    "ttm_reinvestment_rate": null,
    "sources": ["src_iot_10k_fy26", "src_iot_q4fy26_release"]
  },
  "assumptions": {
    "mature_ebit_margin": {"bear": 0.18, "low": 0.22, "base": 0.25, "high": 0.275, "bull": 0.30, "peer_anchor": "Salesforce 26% mature, ServiceNow 27% mature, industrials-SaaS median 22%"},
    "mature_roic": {"bear": 0.15, "low": 0.18, "base": 0.22, "high": 0.26, "bull": 0.30, "moat_named": "data flywheel + frontline UI ownership"},
    "mature_reinvestment_rate": {"bear": 0.06, "low": 0.055, "base": 0.05, "high": 0.045, "bull": 0.04},
    "margin_ramp_path": {
      "y1": -0.01, "y2": 0.03, "y3": 0.06, "y4": 0.09, "y5": 0.12, "y6": 0.15, "y7": 0.17, "y8": 0.19, "y9": 0.21, "y10": 0.22,
      "y15": 0.24, "y20": 0.25, "y25": 0.25
    },
    "wacc": {
      "framework": "required_return",
      "components": {
        "required_real_return": 0.08,
        "reporting_currency_inflation": 0.02,
        "jurisdictional_risk_premium": 0.00,
        "sector_nudge": 0.00,
        "sector_nudge_reason": null
      },
      "composed_required_return": 0.10,
      "cost_of_debt_pretax": 0.055,
      "cost_of_debt_after_tax": 0.041,
      "tax_rate": 0.25,
      "capital_structure": {"equity_weight": 0.90, "debt_weight": 0.10},
      "wacc_calculated": 0.094,
      "wacc_floor_local": 0.085,
      "wacc_used": 0.094,
      "floor_invoked": false,
      "framework_notes": "USD-listed durable growth, US ops; composition 8% + 2% + 0% + 0% = 10% required-return anchor."
    },
    "lease_framework": "operating_cost",
    "sbc_treatment": "real_economic_expense",
    "diluted_share_count_projection": {
      "y5": 595e6,
      "y10": 620e6,
      "y20": 660e6,
      "maturity": 680e6,
      "logic": "Continued SBC issuance ~1.5%/yr fading to 0.5%/yr at maturity; net of any buybacks (not modeled)"
    },
    "terminal_growth_real_pct": 0.005,
    "terminal_growth_nominal_pct": 0.025
  },
  "forecast": {
    "annual": [
      {"year": 1, "revenue": 1965e6, "growth": 0.214, "ebit_margin": -0.01, "nopat": -14.7e6, "da": 30e6, "capex": 25e6, "delta_nwc": 30e6, "fcff": -39.7e6, "roic": -0.02, "reinvestment_rate": null},
      {"year": 2, "revenue": 2380e6, "growth": 0.211, "ebit_margin": 0.03, "nopat": 53.5e6, "da": 40e6, "capex": 35e6, "delta_nwc": 35e6, "fcff": 23.5e6, "roic": 0.05, "reinvestment_rate": null}
    ],
    "periodic": [
      {"year": 15, "revenue": 12e9, "growth": 0.11, "ebit_margin": 0.24, "nopat": 2.16e9, "da": 250e6, "capex": 600e6, "delta_nwc": 200e6, "fcff": 1.61e9, "roic": 0.20, "reinvestment_rate": 0.40}
    ]
  },
  "ev_bridge": {
    "pv_y1_10": 4.5e9,
    "pv_y11_20": 12.3e9,
    "pv_y21_maturity": 18.6e9,
    "pv_terminal": 16.4e9,
    "total_ev": 51.8e9,
    "net_debt": -800e6,
    "lease_liabilities": 0,
    "preferred": 0,
    "nci": 0,
    "cash_above_operating": 0,
    "equity_value": 52.6e9,
    "diluted_shares_used": 620e6,
    "value_per_share_base": 84.84,
    "terminal_share_of_ev_pct": 31.7
  },
  "reverse_dcf": {
    "bear":  {"current_ev": 21037e6, "implied_unlevered_cagr": 0.02, "beats_10pct": false},
    "low":   {"current_ev": 21037e6, "implied_unlevered_cagr": 0.05, "beats_10pct": false},
    "base":  {"current_ev": 21037e6, "implied_unlevered_cagr": 0.13, "beats_10pct": true},
    "high":  {"current_ev": 21037e6, "implied_unlevered_cagr": 0.16, "beats_10pct": true},
    "bull":  {"current_ev": 21037e6, "implied_unlevered_cagr": 0.22, "beats_10pct": true},
    "ten_pct_clearing": {
      "tam_scenario": "base",
      "mature_margin": 0.22,
      "other_anchors": "WACC 9.4%, reinvestment rate 5%",
      "inside_tam_spread": true
    }
  },
  "sensitivity": {
    "matrix_1": {
      "rows": ["TAM bear", "TAM low", "TAM base", "TAM high", "TAM bull"],
      "cols": ["margin 18%", "margin 22%", "margin 25%", "margin 28%", "margin 30%"],
      "cells": [
        [{"vps": 12, "irr": -0.02}, {"vps": 18, "irr": 0.02}, {"vps": 22, "irr": 0.05}, {"vps": 26, "irr": 0.07}, {"vps": 28, "irr": 0.08}],
        [{"vps": 22, "irr": 0.03}, {"vps": 32, "irr": 0.06}, {"vps": 42, "irr": 0.09}, {"vps": 52, "irr": 0.11}, {"vps": 60, "irr": 0.13}],
        [{"vps": 35, "irr": 0.05}, {"vps": 55, "irr": 0.09}, {"vps": 75, "irr": 0.13}, {"vps": 95, "irr": 0.16}, {"vps": 110, "irr": 0.18}],
        [{"vps": 55, "irr": 0.09}, {"vps": 85, "irr": 0.13}, {"vps": 120, "irr": 0.17}, {"vps": 150, "irr": 0.20}, {"vps": 180, "irr": 0.22}],
        [{"vps": 80, "irr": 0.12}, {"vps": 130, "irr": 0.17}, {"vps": 180, "irr": 0.21}, {"vps": 230, "irr": 0.24}, {"vps": 270, "irr": 0.26}]
      ]
    },
    "matrix_2": null,
    "matrix_3": {
      "rows": ["WACC 7.5%", "WACC 8.5%", "WACC 9.5%", "WACC 10.5%", "WACC 12%"],
      "cols": ["real g 0%", "real g 0.5%", "real g 1.5%", "real g 2.5%"],
      "cells": [
        [120, 130, 145, 165],
        [95, 100, 110, 125],
        [80, 85, 90, 100],
        [68, 70, 75, 80],
        [50, 52, 55, 58]
      ]
    }
  },
  "implied_multiples_at_base": {
    "ev_ebit_fy27": 25,
    "ev_fcff_fy27": 40,
    "pe_fy27": 50,
    "current_ev_ebit_fy27": 10,
    "peer_median_ev_ebit_fy27": 22
  },
  "verdict": {
    "decision": "WATCH | BUY | AVOID",
    "rationale": "Base case clears 10% with ~3% margin of safety; current price requires base-TAM + 22% mature margin; bear is plausible (TAM bear mechanism + margin compression). Hold pending margin trajectory confirmation."
  },
  "current_step": "step_5_dcf_math_complete",
  "pacing_mode": "per_anchor",
  "history": [
    {"step": "step_0_tam_loaded_and_verified", "completed_at": "2026-05-19T10:00:00Z"},
    {"step": "step_1_data_snapshot_done", "completed_at": "2026-05-19T10:25:00Z"},
    {"step": "step_2_mature_economics_done", "completed_at": "2026-05-19T11:10:00Z"},
    {"step": "step_3_margin_ramp_done", "completed_at": "2026-05-19T11:35:00Z"},
    {"step": "step_4_wacc_done", "completed_at": "2026-05-19T11:55:00Z"},
    {"step": "step_5_dcf_math_complete", "completed_at": "2026-05-19T12:30:00Z"}
  ]
}
```

### Field Notes

- **`tam_session.consistency_check`**: set at Step 0. Must be `passed` before any further step runs. If `failed`, the skill halts.
- **`current_step`**: must reflect the latest completed step. Resume reads this.
- **`history[]`**: append-only log of completed steps.
- **`sensitivity.matrix_2: null`** is valid — Matrix 2 is omitted when Matrix 1 captures the variance.
- **`assumptions.wacc.floor_invoked`**: explicit flag when the 8.5% floor was used in place of a lower calculated WACC.

## `dcf.md` and `dcf.html`

Generated from `dcf-state.json` by dcf-math (HTML) and by the main thread (markdown — straightforward formatting of the same state). Both should always reflect the current state — regenerate after every assumption revision, don't hand-edit.

## Resume Contract

`/tam-dcf resume <TICKER>`:

1. Glob `~/.investing/companies/<TICKER>/*/dcf-state.json` — pick the most recent.
2. Read it. Check `current_step`.
3. Read the tail of `dialogue.md` (last ~5 turns) to recover conversation.
4. Re-present a one-paragraph summary:
   > Resuming DCF for `<TICKER>` from session `<date>`. TAM loaded from `<TAM date>`. Last completed step: `<current_step>`. We were in the middle of `<step>`. Pick up from there, or revise an earlier step?
5. Continue per-anchor from the appropriate point.

## Auto-Detect on Fresh Invocation

`/tam-dcf <TICKER>` when `dcf-state.json` exists:

> Found existing DCF session for `<TICKER>` from `<date>` (TAM from `<TAM date>`). Last completed step: `<current_step>`. Resume that, or start a new DCF in the same TAM session folder?

If no TAM exists at all:

> No TAM analysis found at `~/.investing/companies/<TICKER>/`. Run `/tam-analysis <TICKER>` first — the DCF needs a hand-off block as input. Stopping here.

(Hard fail. Don't offer alternatives.)
