# State Schema

Files in `~/.investing/companies/<TICKER>/<YYYY-MM-DD>/`:

- `state.json` — machine-readable session state. Source of truth for resume + math-checker input. Updated continuously.
- `dialogue.md` — running transcript. Survives context compaction. Appended-only.
- `sources.md` — every cited anchor with source + quote + retrieval date.
- `handoff.md` — final DCF-ingestible deliverable. Generated from `state.json` at the end.

The session can be reconstructed entirely from these four files.

## `state.json`

```json
{
  "company": {
    "name": "Amazon",
    "ticker": "AMZN",
    "exchange": "NASDAQ",
    "reporting_currency": "USD",
    "analysis_date": "2026-05-18",
    "last_reported_revenue_today_$": 638000000000,
    "geographic_footprint": "US (primary), international across 20+ markets",
    "product_footprint": "e-commerce (1P + 3P), cloud (AWS), advertising, subscription (Prime), grocery, devices"
  },
  "asset_backed_wedges": [
    {"wedge": "Prime household installed base", "evidence": "200M+ paid members; durable retention; payments-on-file"},
    {"wedge": "Fulfillment / logistics network", "evidence": "200+ FCs, last-mile, captive air"},
    {"wedge": "AWS scale + breadth", "evidence": "#1 cloud share; 200+ services; data gravity"},
    {"wedge": "1P shopper data + ad surface", "evidence": "$50bn+ ad revenue at high margin"}
  ],
  "user_supplied_adjacencies": ["AWS-style cloud spin-out", "ad network on shopper data"],
  "current_step": "layer_3_pool_projection",
  "layers": [
    {
      "id": "us-online-retail",
      "name": "US online retail (1P + 3P GMV)",
      "speculative": false,
      "model_type": "retailer + marketplace",
      "demand_unit": "Online retail transactions to US consumers",
      "scope_chosen": "plausible",
      "scope_options": [
        {"name": "tight", "description": "...", "pool_today": "..."},
        {"name": "plausible", "description": "...", "pool_today": "..."},
        {"name": "aggressive", "description": "...", "pool_today": "..."}
      ],
      "anchors": [
        {
          "name": "us_population",
          "value": 335000000,
          "range": [330000000, 340000000],
          "confidence": "high",
          "source_id": "src_us_census_2024",
          "user_confirmed": true,
          "override_reason": null
        },
        {
          "name": "per_capita_online_retail_spend_today",
          "value": 4200,
          "range": [3800, 4600],
          "confidence": "moderate",
          "source_id": "src_census_ecommerce_q4",
          "user_confirmed": true,
          "override_reason": null
        }
      ],
      "pool_today": {
        "value": 1100000000000,
        "range": [950000000000, 1250000000000],
        "confidence": "moderate",
        "formula": "population × per_capita_online_retail_spend"
      },
      "pool_at_maturity": {
        "year": "Y15",
        "value": 2100000000000,
        "confidence": "moderate",
        "drivers": [
          {"name": "population_growth", "cagr": 0.005, "source_id": "src_un_pop_proj"},
          {"name": "per_capita_usage_shift", "cagr": 0.025, "source_id": "src_emarketer_ecommerce_2024"},
          {"name": "online_share_of_retail_shift", "cagr": 0.015, "source_id": "..."}
        ]
      },
      "share": {
        "bear": 0.20, "low": 0.30, "base": 0.38, "high": 0.45, "bull": 0.55,
        "precedent": "Costco at 20% of warehouse club; Amazon at ~38% of US e-commerce today; aggressive marketplace network effects support 50%+."
      },
      "monetization": {
        "metric": "captured revenue / GMV (blended 1P + 3P take rate)",
        "today_$": 0.28,
        "today_$_components": {"1P_margin": 0.40, "3P_take_rate": 0.15, "ad_yield_overlay": 0.04},
        "mix_shift": "Tilt toward 3P + ads over time → blended monetization rises"
      },
      "real_pricing_cagr": {"d1": 0.005, "d2": 0.0, "d3": 0.0},
      "inflation_overlay": 0.02,
      "overlap_haircut": {
        "amount": 0.10,
        "with_layer": "international-retail",
        "reason": "Cross-border buyers double-counted at the household level"
      },
      "layer_revenue_at_maturity_today_$": {
        "bear": 110000000000,
        "low": 165000000000,
        "base": 220000000000,
        "high": 260000000000,
        "bull": 310000000000
      },
      "activation_schedule": {
        "shared_across_scenarios": true,
        "activation_year": 0,
        "peak_contribution_year": 5,
        "maturity_year": 15,
        "per_scenario_overrides": null
      },
      "math_check_status": "passed",
      "math_check_log": ".math-check.log"
    }
  ],
  "overall_hand_off_horizon": {
    "year": "Y25",
    "rationale": "Speculative robotics layer matures Y25; sets the hand-off horizon."
  },
  "aggregated": {
    "last_reported_revenue_today_$": 638000000000,
    "last_reported_yoy_growth": 0.092,
    "y1_3_guidance_anchor": {
      "midpoint": 0.095,
      "range": [0.085, 0.105],
      "source_id": "src_company_guidance_2026",
      "consensus_midpoint": 0.093,
      "consensus_source_id": "src_consensus_2026"
    },
    "revenue_at_maturity_today_$": {"bear": "...", "low": "...", "base": "...", "high": "...", "bull": "..."},
    "revenue_at_maturity_nominal_$": {"bear": "...", "low": "...", "base": "...", "high": "...", "bull": "..."},
    "growth_path_cagrs_per_scenario": {
      "bear": {"y1_3": 0.04, "y4_5": 0.05, "y6_10": 0.05, "y11_20": 0.04, "y21_maturity": 0.02},
      "low":  {"y1_3": 0.07, "y4_5": 0.08, "y6_10": 0.08, "y11_20": 0.07, "y21_maturity": 0.04},
      "base": {"y1_3": 0.095, "y4_5": 0.105, "y6_10": 0.10, "y11_20": 0.09, "y21_maturity": 0.05},
      "high": {"y1_3": 0.11, "y4_5": 0.13, "y6_10": 0.14, "y11_20": 0.11, "y21_maturity": 0.055},
      "bull": {"y1_3": 0.13, "y4_5": 0.17, "y6_10": 0.19, "y11_20": 0.15, "y21_maturity": 0.06}
    },
    "growth_shape_per_scenario": {
      "bear": "smooth_fade",
      "low": "smooth_fade",
      "base": "stay_elevated",
      "high": "stay_elevated",
      "bull": "stay_elevated"
    },
    "peak_growth_year_per_scenario": {
      "bear": 1,
      "low": 3,
      "base": 4,
      "high": 6,
      "bull": 8
    },
    "annual_revenue_today_$_per_scenario": {
      "_provenance": "DERIVED via linear interpolation in growth-rate space; anchored on last_reported_yoy_growth at Y0 and on period-CAGR midpoints. Period CAGRs are the contract; this series is regenerable.",
      "bear": [638e9, 663e9, 690e9, "..."],
      "low":  [638e9, 682e9, 735e9, "..."],
      "base": [638e9, 698e9, 770e9, "..."],
      "high": [638e9, 708e9, 800e9, "..."],
      "bull": [638e9, 721e9, 850e9, "..."]
    },
    "scenario_monotonicity_test": {
      "status": "passed",
      "notes": "revenue_at_maturity_today_$ monotone: bear < low < base < high < bull. Same for layer_revenue_at_maturity_today_$ per layer."
    },
    "handoff_contract_test": {
      "bear": {"compounded_endpoint": 4.80e9, "stated_endpoint": 4.80e9, "delta_pct": 0.0, "status": "passed"},
      "low":  {"compounded_endpoint": 8.10e9, "stated_endpoint": 8.10e9, "delta_pct": 0.0, "status": "passed"},
      "base": {"compounded_endpoint": 13.70e9, "stated_endpoint": 13.70e9, "delta_pct": 0.0, "status": "passed"},
      "high": {"compounded_endpoint": 21.50e9, "stated_endpoint": 21.50e9, "delta_pct": 0.0, "status": "passed"},
      "bull": {"compounded_endpoint": 35.90e9, "stated_endpoint": 35.90e9, "delta_pct": 0.0, "status": "passed"}
    },
    "y1_3_anchor_test": {
      "bear": {"pick": 0.04, "guidance_midpoint": 0.095, "delta_pp": -5.5, "status": "override", "override_reason": "bear assumes full bear-mechanism materialization in Y2-3"},
      "low":  {"pick": 0.07, "guidance_midpoint": 0.095, "delta_pp": -2.5, "status": "override", "override_reason": "low assumes partial bear-mechanism materialization (e.g., payments compression hits but state/federal stays on track)"},
      "base": {"pick": 0.095, "guidance_midpoint": 0.095, "delta_pp": 0.0, "status": "passed"},
      "high": {"pick": 0.11, "guidance_midpoint": 0.095, "delta_pp": 1.5, "status": "passed", "override_reason": "high assumes most adjacencies activate; partial bull-catalyst realization"},
      "bull": {"pick": 0.13, "guidance_midpoint": 0.095, "delta_pp": 3.5, "status": "passed", "override_reason": "bull assumes full bull-adjacency activation including already-announced state enterprise contracts ramping ahead of plan"}
    },
    "layer_schedule_consistency_test": {
      "bear": {"status": "passed", "notes": "no late activator (speculative = 0); post-Y3 CAGRs monotone decreasing"},
      "low":  {"status": "passed", "notes": "speculative layers partial; declared CAGRs reflect muted late-period contribution"},
      "base": {"status": "passed", "notes": "SP-A activates Y4 (contributes 18% of base endpoint); Y4-5 CAGR 10.5% > Y1-3 9.5% — consistent"},
      "high": {"status": "passed", "notes": "SP-A + SP-F both active; mid-cycle elevation traceable to both"},
      "bull": {"status": "passed", "notes": "SP-A activates Y4, SP-F activates Y6; Y6-10 elevation justified"}
    }
  },
  "pacing_mode": "per_anchor",
  "history": [
    {"step": "step_0_setup", "completed_at": "2026-05-18T10:32:00Z"},
    {"step": "speculative_layer_selection", "completed_at": "2026-05-18T10:48:00Z"},
    {"step": "layer_1_demand_unit", "completed_at": "2026-05-18T10:52:00Z"},
    {"step": "layer_1_pool_today", "completed_at": "2026-05-18T11:08:00Z"}
  ]
}
```

### Field Notes

- **`current_step`**: must always reflect the latest completed step. Resume reads this. Valid values:
  - `step_0_setup`
  - `speculative_layer_selection`
  - `layer_<id>_demand_unit`
  - `layer_<id>_pool_today`
  - `layer_<id>_pool_projection`
  - `layer_<id>_scope_chosen`
  - `layer_<id>_sized`
  - `layer_<id>_overlap_checked`
  - `multiplication_started`
  - `multiplication_done_for_<layer_id>`
  - `final_aggregation`
  - `horizon_proposed`
  - `handoff_emitted`
- **`anchors[]`**: every confirmed anchor logged here, with `source_id` linking to `sources.md`. `user_confirmed: true` means the user accepted (after pushback if any). If user overrode the source range, `override_reason` is populated.
- **Scenarios**: five — `bear`, `low`, `base`, `high`, `bull`. `bear` = absolute worst plausible (named bear mechanism fully materializes; speculative layers contribute zero by hard rule). `low` = realistic adverse ("things don't go very well" — partial bear-mechanism materialization). `base` = bottom-up evidence-weighted. `high` = realistic upside ("things go above base expectations" — partial bull-adjacency realization). `bull` = absolute best plausible (full bull adjacencies + named catalysts). Math-checker enforces monotonicity `bear < low < base < high < bull` for headline revenue and per-layer revenue.
- **`activation_schedule`** (per layer): metadata describing when the layer contributes meaningful revenue (`activation_year`), the year of peak %-contribution to consolidated growth (`peak_contribution_year`), and the year the layer is mostly built out (`maturity_year`). This is **discipline metadata**, not a revenue-path generator — the consolidated growth path is declared per scenario via `aggregated.growth_path_cagrs_per_scenario`. The math-checker runs a `layer_schedule_consistency_test` that flags when the declared CAGRs are incompatible with the activation schedule (e.g., a layer activating Y4 with ≥15% contribution but Y4-5 CAGR < Y1-3 CAGR — layer would be invisible).
- **`aggregated.last_reported_revenue_today_$`** + **`aggregated.last_reported_yoy_growth`**: today's actuals. Anchor the Y0 point of the derived annual revenue series. Must be cited (latest 10-K/20-F).
- **`aggregated.y1_3_guidance_anchor`**: mandatory anchor researched at the multiplication step. Management guidance midpoint + range + consensus midpoint. The **base** scenario's Y1-3 CAGR is constrained to ±3pp of `midpoint`. Other scenarios (bear / low / high / bull) take reasoned spreads from base — typical: bear -4 to -6pp; low -2 to -3pp; high +1 to +2pp; bull +3 to +5pp. Each non-base deviation logs an `override_reason`.
- **`aggregated.growth_path_cagrs_per_scenario`**: the contract. User-confirmed period CAGRs per scenario (bear/low/base/high/bull), declared at the multiplication step, validated by math-checker against (a) `handoff_contract_test` (compound-to-endpoint, all five), (b) `y1_3_anchor_test` (base within ±3pp of guidance, others reasoned spreads with override), (c) `layer_schedule_consistency_test` (compatible with activation schedule per scenario), (d) `scenario_monotonicity_test` (bear < low < base < high < bull).
- **`aggregated.annual_revenue_today_$_per_scenario`**: DERIVED via linear interpolation in growth-rate space between period-CAGR midpoints, anchored on `last_reported_yoy_growth` at Y0, with per-period renormalization to hit each stated CAGR exactly. Provided for DCF-consumer convenience. Regenerable from the CAGRs.
- **`math_check_status`**: `pending` / `passed` / `failed`. If `failed`, surface to user immediately.
- **`history[]`**: append-only log of completed steps. Useful for debugging resume.

## `sources.md`

One section per cited anchor. Format:

```markdown
## src_us_census_2024

- **Value**: US population, 335M (as of 2024)
- **Range**: 330M-340M (point estimate vs latest projection)
- **Source**: US Census Bureau, 2024 Population Estimates
- **URL**: https://www.census.gov/...
- **Quote**: "The resident population of the United States was 335,893,238 as of July 1, 2024."
- **Retrieved**: 2026-05-18
- **Confidence**: high
- **Used in**: layer-1 (us-online-retail), anchor `us_population`
- **Override**: none
```

If user overrode the source range:

```markdown
## src_xyz_anchor

(... as above ...)
- **Override**: user picked 0.45 vs source range [0.20, 0.35]. Reason: "Asset-backed wedge from data flywheel justifies higher mature share than precedent — Visa's network-effect moat reached 60% globally in payments."
```

Every override has a reason. No silent overrides.

## `dialogue.md`

Append-only running transcript. Survives context compaction.

Format:

```markdown
# TAM Analysis: AMZN — 2026-05-18

## Step 0 — Setup

**User**: ...
**Skill**: ...
(continues)

## Step 1 — Speculative Layer Selection

(continues)

## Layer 1 — US Online Retail

### Demand Unit
**User**: ...
**Skill**: ...

### Pool Today — Anchor: US Population
**Skill**: dispatching anchor-researcher for "US population today"
**Skill (research result)**: 335M, range 330-340M, source US Census 2024, confidence high.
**User**: confirmed.

(continues)
```

Append after every turn. Never overwrite. If context compacts, re-read the tail of this file before next response.

## `handoff.md`

Generated from `state.json` at the end. Format per `handoff-format.md`. Do not hand-edit — regenerate from state.

## Resume Contract

`/tam-analysis resume <TICKER>`:

1. Glob `~/.investing/companies/<TICKER>/*/` — pick the most recent dated folder.
2. Read `state.json`. Check `current_step`.
3. Read the tail of `dialogue.md` (last ~5 turns) to recover conversational context.
4. Re-present a one-paragraph summary:
   > Resuming TAM analysis for `<TICKER>` from session `<date>`. Last completed step: `<current_step>`. We were in the middle of `<layer name / section>` at confidence `<confidence>`. Pick up from there, or revise an earlier step?
5. On user confirmation, continue per-anchor from the appropriate point.

## Auto-Detect on Fresh Invocation

`/tam-analysis <TICKER>` when folder exists:

1. Glob `~/.investing/companies/<TICKER>/*/`.
2. If exists, do NOT silently start fresh.
3. Present:
   > Found existing session for `<TICKER>` from `<date>`. Last completed step: `<current_step>`. Resume that, or start a new session in `~/.investing/companies/<TICKER>/2026-05-18/`?
4. Wait for user.

## Within-Session Context Compaction

After any context compaction within a single session:

1. Re-read `state.json` to reload session state.
2. Re-read tail of `dialogue.md` (last ~10 turns) to recover conversational thread.
3. Continue from where you left off. Do not announce the compaction unless the user asks.

The discipline: skill behavior must be identical pre-compaction and post-compaction. The files are the memory.
