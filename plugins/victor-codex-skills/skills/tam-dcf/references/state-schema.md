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
    "tam_handoff_hash": "sha256:7f3a9b2c8e5d4f1a6b9c3e2d5f8a1b4c7e0d3a6b9c2e5f8a1b4c7e0d3a6b9c2e",
    "tam_handoff_hash_verified_at": "2026-05-19T10:00:00Z",
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
    "revenue_basis": "reported",
    "economic_bridge_summary_from_tam": "no adjustments — reported = economic",
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
  "growth_engine": {
    "type": "opex_funded",
    "forecast_method": "cash_conversion_margin",
    "rationale": "Vertical SaaS. R&D + S&M ~30% of revenue (in EBIT). PPE capex 0.7% of revenue. Capitalized software 0.7%. M&A material but episodic, not the engine. Organic growth ~9% YoY. Clean opex_funded.",
    "diagnostic_signals": {
      "capex_intensity_3yr_avg_pct_rev": 0.007,
      "capitalized_software_3yr_avg_pct_rev": 0.007,
      "r_and_d_3yr_avg_pct_rev": 0.060,
      "s_and_m_3yr_avg_pct_rev": 0.140,
      "m_a_deployment_3yr_avg_pct_fcf": 0.45,
      "m_a_pattern": "episodic_large_deals",
      "organic_growth_3yr_avg": 0.085,
      "sales_to_capital_y0": null,
      "fcff_margin_actual_y0": 0.201,
      "fcff_margin_guided_y1": 0.205
    },
    "engine_specific_anchors": {
      "_engine_note": "Schema for engine_specific_anchors varies by engine.type. See per-engine sections below.",
      "cash_conversion_margin_y0": 0.201,
      "cash_conversion_margin_guided_y1": 0.205,
      "cash_conversion_margin_mature_per_scenario": {
        "bear": 0.18, "low": 0.22, "base": 0.25, "high": 0.28, "bull": 0.30
      },
      "ramp_anchored_to": "FY2025 actual after-SBC FCF margin (20.1%) + FY2026 management FCF guide (26-28% before SBC; ~20.5% after-SBC)"
    },
    "maintenance_only_fcff_margin": {
      "value_per_scenario": {
        "bear": 0.24, "low": 0.27, "base": 0.30, "high": 0.32, "bull": 0.35
      },
      "rationale": "Stop-the-engine view: if growth-oriented S&M drops to renewals + sector-pace replacement only, and growth R&D drops to sustaining + parity, FCFF margin would expand by ~10pp on base. This is the structural ceiling on cash-cow mode.",
      "user_confirmed": true
    },
    "user_confirmed": true,
    "audit_status": "completed"
  },
  "economic_bridge": {
    "revenue_side_inherited_from_tam": {
      "basis": "reported",
      "adjustments_summary": "no adjustments — reported = economic"
    },
    "margin_side": {
      "audit_status": "completed",
      "reported_ebit_margin_y0": -0.0325,
      "economic_ebit_margin_y0": -0.0325,
      "sbc_breakdown": {
        "reported_sbc_pct_rev_3yr_avg": 0.18,
        "run_rate_sbc_pct_rev": 0.16,
        "one_time_components": []
      },
      "segment_reclassifications": [],
      "peer_normalization_spec": "Peers: Salesforce, ServiceNow, industrials-SaaS median. Strip pass-through (none present in peer set); use run-rate SBC (3yr avg ex-vesting-vintage); no segment reclassification needed.",
      "bridge_notes": "Clean reading. Reported = economic on both revenue and margin side. Audit completed at Step 2."
    }
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
  "cash_reality_check": {
    "comparable": {
      "fy_actual_after_sbc_fcf_margin": 0.201,
      "fy_actual_basis": "FY2025: OCF $653.5M − PPE capex $16.0M − capitalized software $16.8M − SBC $151.3M = $469.4M ÷ revenue $2,330M = 20.1%",
      "ny_guided_after_sbc_fcf_margin": 0.205,
      "ny_guided_basis": "FY2026 mgmt FCF guide 26-28% (midpoint 27%); less Q1 2026 SBC margin 6.5% projection = ~20.5%",
      "tighter_bar_used": "ny_guided",
      "tighter_bar_value": 0.205,
      "source_ids": ["src_tyl_10k_fy25", "src_tyl_q4_fy25_release"]
    },
    "y1": {
      "modeled_fcff_margin_per_scenario": {
        "bear": 0.150, "low": 0.180, "base": 0.205, "high": 0.215, "bull": 0.225
      },
      "delta_bp_per_scenario": {
        "bear": -550, "low": -250, "base": 0, "high": 100, "bull": 200
      },
      "halt_triggered_scenarios": ["bear"],
      "override": {
        "bear": {
          "mechanism": "Bear scenario assumes FY2026 large customer churn (state ERP losses) cuts FCF margin temporarily; trajectory rejoins peers by Y3.",
          "logged_in_dialogue": true,
          "logged_in_sources_id": "src_tyl_bear_mechanism_override"
        }
      }
    },
    "y2_y3": {
      "avg_modeled_fcff_margin_per_scenario": {
        "bear": 0.175, "low": 0.195, "base": 0.215, "high": 0.225, "bull": 0.235
      },
      "delta_bp_per_scenario_vs_tighter_bar": {
        "bear": -300, "low": -100, "base": 100, "high": 200, "bull": 300
      },
      "halt_triggered_scenarios": [],
      "override": null
    },
    "audit_status": "completed",
    "halt_thresholds": {"y1_bp": 500, "y2_y3_bp": 1000},
    "audit_notes": "Y1 base scenario passes (delta 0bp). Y1 bear scenario halts at -550bp; override mechanism logged. Y2-Y3 all scenarios pass (max delta -300bp, within 1000bp threshold)."
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
  "current_step": "step_7_dcf_math_complete",
  "pacing_mode": "per_anchor",
  "history": [
    {"step": "step_0_tam_loaded_and_verified", "completed_at": "2026-05-19T10:00:00Z"},
    {"step": "step_1_data_snapshot_done", "completed_at": "2026-05-19T10:25:00Z"},
    {"step": "step_2_economic_bridge_done", "completed_at": "2026-05-19T10:45:00Z"},
    {"step": "step_3_growth_engine_done", "completed_at": "2026-05-19T11:00:00Z"},
    {"step": "step_4_mature_economics_done", "completed_at": "2026-05-19T11:25:00Z"},
    {"step": "step_5_margin_ramp_done", "completed_at": "2026-05-19T11:50:00Z"},
    {"step": "step_6_wacc_done", "completed_at": "2026-05-19T12:10:00Z"},
    {"step": "step_7_dcf_math_complete", "completed_at": "2026-05-19T12:40:00Z"},
    {"step": "step_8_cash_reality_done", "completed_at": "2026-05-19T12:50:00Z"},
    {"step": "step_9_forecast_expert_done", "completed_at": "2026-05-19T13:05:00Z"}
  ]
}
```

### Field Notes

- **`tam_session.consistency_check`**: set at Step 0. Must be `passed` before any further step runs. If `failed`, the skill halts.
- **`current_step`**: must reflect the latest completed step. Resume reads this.
- **`history[]`**: append-only log of completed steps.
- **`sensitivity.matrix_2: null`** is valid — Matrix 2 is omitted when Matrix 1 captures the variance.
- **`assumptions.wacc.floor_invoked`**: explicit flag when the 8.5% floor was used in place of a lower calculated WACC.
- **`tam_session.tam_handoff_hash`**: SHA-256 of `handoff.md` content (Section G text only — the strict block parsed by DCF) computed at Step 0. Used to detect TAM-side staleness on resume: if the current hash of `handoff.md` differs from `tam_handoff_hash_verified_at`, the TAM has been modified since the DCF last verified it. DCF halts and re-runs Step 0 verification. Prevents silent drift between TAM and DCF when user re-runs `/tam-analysis resume <TICKER>` between DCF sessions.
- **`growth_engine`**: results of Step 3 growth-engine classification. The engine type drives the forecasting math at Step 7 and the mature-economics anchor set at Step 4. Engine type is a forecasting METHOD choice, not a company-inherent property — two competent analysts could legitimately pick different engines for the same name based on which growth path they're modeling. Lives in DCF only (not TAM hand-off).
  - `type`: one of `opex_funded | capex_funded | acquisition_funded | mixed_engine | mature_cash_cow`.
  - `forecast_method`: paired with `type`. `cash_conversion_margin | sales_to_capital | acquisition_track | per_segment | maintenance_fcff`. Used by dcf-math dispatch to select the right forecasting identity.
  - `diagnostic_signals`: 3-yr trailing financial signals that informed the classification (capex intensity, R&D/S&M % rev, M&A deployment, organic growth, sales-to-capital, FCFF margin actual + guided). Computed from Step 1 data snapshot + anchor-researcher dispatches for M&A history.
  - `engine_specific_anchors`: schema varies by engine type. See per-engine schemas below.
  - `maintenance_only_fcff_margin`: the "stop-the-engine" view per scenario — what FCFF margin if growth spend (growth-oriented S&M, R&D greenfield, M&A deployment, growth capex on new units) drops to maintenance-only (renewals, parity, sustaining). Surfaces in `dcf.md` Section 5 as a discipline anchor. Always asked, even when current FCFF margin is already high.
  - `audit_status`: `completed` after Step 3 runs; `pending` only before.

  **Per-engine `engine_specific_anchors` schemas:**

  | Engine | Anchors |
  |--------|---------|
  | `opex_funded` | `cash_conversion_margin_y0`, `cash_conversion_margin_guided_y1`, `cash_conversion_margin_mature_per_scenario`, `ramp_anchored_to` |
  | `capex_funded` | `sales_to_capital_y0`, `sales_to_capital_mature_per_scenario`, `capex_intensity_y0_pct_rev`, `incremental_invested_capital_basis` (`ex_goodwill` typically) |
  | `acquisition_funded` | `organic_growth_per_scenario`, `organic_fcff_margin_per_scenario`, `m_a_deployment_pct_fcf`, `roic_acquired_per_scenario`, `m_a_pace_assumption` |
  | `mixed_engine` | `segments[]` — each with `name`, `engine` (one of the 4 non-mixed types), `revenue_weight`, `anchors` (the type's schema) |
  | `mature_cash_cow` | `maintenance_capex_pct_rev_3yr_avg`, `maintenance_fcff_margin_per_scenario`, `growth_via_pricing_power` (bool) |

  **Worked example for an acquisition-funded company** (CSU-shaped):

  ```json
  "growth_engine": {
    "type": "acquisition_funded",
    "forecast_method": "acquisition_track",
    "rationale": "Serial software acquirer. Organic growth ~5-7% YoY (vertical-SaaS market pace). M&A deployment averages 85% of FCF. ROIC-acquired 12-18% (vertical software roll-up). Acquisitions ARE the growth engine; treating them as one-off optionality misses 70%+ of the value.",
    "diagnostic_signals": {
      "capex_intensity_3yr_avg_pct_rev": 0.005,
      "r_and_d_3yr_avg_pct_rev": 0.040,
      "s_and_m_3yr_avg_pct_rev": 0.080,
      "m_a_deployment_3yr_avg_pct_fcf": 0.85,
      "m_a_pattern": "continuous_roll_up",
      "organic_growth_3yr_avg": 0.06,
      "fcff_margin_actual_y0": 0.18
    },
    "engine_specific_anchors": {
      "organic_growth_per_scenario": {"bear": 0.03, "low": 0.05, "base": 0.06, "high": 0.08, "bull": 0.10},
      "organic_fcff_margin_per_scenario": {"bear": 0.16, "low": 0.18, "base": 0.20, "high": 0.22, "bull": 0.25},
      "m_a_deployment_pct_fcf": 0.85,
      "roic_acquired_per_scenario": {"bear": 0.08, "low": 0.12, "base": 0.15, "high": 0.18, "bull": 0.22},
      "m_a_pace_assumption": "continued at 5-yr trailing pace through Y10; fades to 30% deployment by maturity Y25"
    },
    "maintenance_only_fcff_margin": {
      "value_per_scenario": {"bear": 0.16, "low": 0.18, "base": 0.20, "high": 0.22, "bull": 0.25},
      "rationale": "Stop-the-engine = stop M&A. Organic FCFF margin (per scenario above) IS the maintenance view — what shareholders receive if all FCF returns as buybacks/dividends instead of being deployed for acquisitions.",
      "user_confirmed": true
    },
    "user_confirmed": true,
    "audit_status": "completed"
  }
  ```

- **`cash_reality_check`**: results of Step 8 cash-reality reconciliation. Runs after dcf-math Step 7 (forecast generation), before Step 10 (output emission). Compares modeled Y1 and Y2-Y3 FCFF margins against a "comparable" — the tighter of `fy_actual_after_sbc_fcf_margin` (back-solved from latest 10-K disclosed components) and `ny_guided_after_sbc_fcf_margin` (back-solved from management guidance).
  - `comparable`: the bar. Back-solve recipe documented in `fy_actual_basis` + `ny_guided_basis` for auditability.
  - `y1`: per-scenario modeled FCFF margin + delta bp vs `tighter_bar_value`. Halt threshold: >500bp.
  - `y2_y3`: per-scenario AVG modeled FCFF margin Y2-Y3 + delta vs same bar. Halt threshold: >1000bp (wider to accommodate forward uncertainty).
  - `halt_triggered_scenarios`: list of scenario names that exceeded threshold. Resolution: revise assumptions OR log named mechanism in `override.{scenario}.mechanism` OR halt the run.
  - `override.{scenario}.mechanism`: required when accepting a halt-triggering delta. Free-text mechanism logged alongside in `sources.md`. Without a logged mechanism, downstream emission halts.
  - The check is engine-AGNOSTIC: it compares modeled FCFF margin to observed/guided FCFF margin, independent of which forecast_method generated the model. Works equally for opex_funded (cash-conversion direct), capex_funded (NOPAT minus reinvestment), acquisition_funded (organic FCFF after M&A deployment), mature_cash_cow, mixed_engine.
- **`economic_bridge`**: results of Step 2 reported-to-economic bridge.
  - `revenue_side_inherited_from_tam`: mirror of `revenue_basis` and bridge summary from the TAM hand-off (Step 0.3). DCF does not re-audit the revenue side; it consumes whatever TAM declared.
  - `margin_side`: DCF-side audit. `sbc_breakdown` separates run-rate SBC from one-time vintage components. `segment_reclassifications` lists any segments reclassified from "operating" to "strategic" (R&D / distribution / customer acquisition / brand). `peer_normalization_spec` is the binding spec used in Step 2 peer-margin dispatches — both target and peers cleaned the same way.
  - `audit_status`: `completed` after Step 2 runs; `pending` only before. Audit always runs (even when clean) — a confirmed "no quirks" result is itself useful.
  - **Worked example for a quirky company** (CEO performance grant + ad-fund pass-through inherited from TAM + strategic store segment, Wingstop-shaped):

  ```json
  "economic_bridge": {
    "revenue_side_inherited_from_tam": {
      "basis": "economic_adjusted",
      "adjustments_summary": "stripped $250M ad-fund pass-through; reported $467M → economic $217M"
    },
    "margin_side": {
      "audit_status": "completed",
      "reported_ebit_margin_y0": 0.26,
      "economic_ebit_margin_y0": 0.55,
      "sbc_breakdown": {
        "reported_sbc_pct_rev_3yr_avg": 0.04,
        "run_rate_sbc_pct_rev": 0.02,
        "one_time_components": [
          {
            "name": "CEO 2024 performance award",
            "total_grant_$": 80000000,
            "vesting_structure": "10yr cliff at hurdle prices $200/$300/$400 by 2031",
            "probability_weighted_expected_value": 24000000,
            "source_id": "src_<ticker>_def14a_2024",
            "treatment": "contingent_expected_value"
          }
        ]
      },
      "segment_reclassifications": [
        {
          "segment_name": "company-owned stores",
          "reported_revenue_$": 50000000,
          "reported_ebit_margin": 0.12,
          "reclassification": "strategic_rnd_function",
          "reclassified_treatment": "Costs moved to opex-R&D (kitchen innovation, pricing tests, tech rollout); revenue excluded from operating-segment mature-margin benchmark.",
          "rationale": "60 stores serve as R&D for the franchise system — not a stand-alone profit center. Confirmed by 10-K MD&A language on operational testing.",
          "user_confirmed": true
        }
      ],
      "peer_normalization_spec": "Strip ad-fund pass-through from peers where present; use run-rate SBC for all (Domino's, Papa John's, restaurant-franchise comparables); reclassify any peer company-owned segment same way; surface both raw and normalized peer EBIT margins.",
      "bridge_notes": "Reported EBIT margin 26% reflects the operating-segment view inflated by ad-fund pass-through and depressed by strategic store segment. Economic margin 55% reflects the true franchise-royalty engine after stripping ad-fund and reclassifying stores. Step 2 mature-margin assumption anchored on 55%, not 26%."
    }
  }
  ```

## `dcf.md` and `dcf.html`

Generated from `dcf-state.json` by dcf-math (HTML) and by the main thread (markdown — straightforward formatting of the same state). Both should always reflect the current state — regenerate after every assumption revision, don't hand-edit.

## Resume Contract

`/tam-dcf resume <TICKER>`:

1. Glob `~/.investing/companies/<TICKER>/*/dcf-state.json` — pick the most recent.
2. Read it. Check `current_step`.
3. **TAM staleness check**: compute SHA-256 of current `handoff.md` Section G content. Compare to stored `tam_session.tam_handoff_hash`. If different:
   > TAM hand-off has been modified since this DCF was last verified at `<tam_handoff_hash_verified_at>`. The current DCF assumptions may no longer be consistent with the TAM. Options:
   > (a) Re-verify Step 0 against the updated hand-off (re-run all consistency checks).
   > (b) Roll the TAM back to the hash known-good for this DCF (provide path).
   > (c) Archive this DCF as superseded; start fresh against the new TAM.
4. Read the tail of `dialogue.md` (last ~5 turns) to recover conversation.
5. Re-present a one-paragraph summary:
   > Resuming DCF for `<TICKER>` from session `<date>`. TAM loaded from `<TAM date>` (hash verified). Last completed step: `<current_step>`. We were in the middle of `<step>`. Pick up from there, or revise an earlier step?
6. Continue per-anchor from the appropriate point.

## Auto-Detect on Fresh Invocation

`/tam-dcf <TICKER>` when `dcf-state.json` exists:

> Found existing DCF session for `<TICKER>` from `<date>` (TAM from `<TAM date>`). Last completed step: `<current_step>`. Resume that, or start a new DCF in the same TAM session folder?

If no TAM exists at all:

> No TAM analysis found at `~/.investing/companies/<TICKER>/`. Run `/tam-analysis <TICKER>` first — the DCF needs a hand-off block as input. Stopping here.

(Hard fail. Don't offer alternatives.)
