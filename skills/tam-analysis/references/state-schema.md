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
  "schema_version": "1.0",
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
        "bear": 0.25, "base": 0.38, "bull": 0.50,
        "precedent": "Costco at 20% of warehouse club; Amazon at ~38% of US e-commerce today; aggressive marketplace network effects support 50%."
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
        "bear": 145000000000,
        "base": 220000000000,
        "bull": 295000000000
      },
      "ramp_schedule": {
        "shared_across_scenarios": true,
        "activation_year": 0,
        "peak_growth_year": 5,
        "maturity_year": 15,
        "curve_shape": "s_curve",
        "per_scenario_overrides": null
      },
      "annual_revenue_today_$": {
        "bear": [125e9, 132e9, 140e9, "..."],
        "base": [125e9, 138e9, 152e9, "..."],
        "bull": [125e9, 145e9, 168e9, "..."]
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
    "revenue_at_maturity_today_$": {"bear": "...", "base": "...", "bull": "..."},
    "revenue_at_maturity_nominal_$": {"bear": "...", "base": "...", "bull": "..."},
    "annual_revenue_today_$_per_scenario": {
      "bear": [1.62e9, 1.85e9, 2.10e9, "..."],
      "base": [1.62e9, 1.96e9, 2.30e9, "..."],
      "bull": [1.62e9, 2.05e9, 2.50e9, "..."]
    },
    "growth_path_cagrs_per_scenario": {
      "bear": {"y1_3": 0.05, "y4_5": 0.06, "y6_10": 0.07, "y11_20": 0.06, "y21_maturity": 0.02},
      "base": {"y1_3": 0.17, "y4_5": 0.20, "y6_10": 0.18, "y11_20": 0.11, "y21_maturity": 0.02},
      "bull": {"y1_3": 0.22, "y4_5": 0.25, "y6_10": 0.22, "y11_20": 0.16, "y21_maturity": 0.02}
    },
    "growth_shape_per_scenario": {
      "bear": "front_loaded",
      "base": "stacked S-curves",
      "bull": "stacked S-curves"
    },
    "peak_growth_year_per_scenario": {
      "bear": 1,
      "base": 5,
      "bull": 5
    },
    "handoff_contract_test": {
      "bear": {"compounded_endpoint": 6.97e9, "stated_endpoint": 6.97e9, "delta_pct": 0.0, "status": "passed"},
      "base": {"compounded_endpoint": 31.11e9, "stated_endpoint": 31.11e9, "delta_pct": 0.0, "status": "passed"},
      "bull": {"compounded_endpoint": 106.09e9, "stated_endpoint": 106.09e9, "delta_pct": 0.0, "status": "passed"}
    },
    "shape_sanity_test": {
      "bear": {"status": "passed", "notes": "monotonic decel after Y1 peak"},
      "base": {"status": "passed", "notes": "stacked-S with SP-A activation Y4 + SP-F Y6 explains mid-cycle plateau"},
      "bull": {"status": "passed", "notes": "stacked-S; mid-cycle elevation Y11-15 traceable to SP-A peak Y10 + SP-F peak Y12"}
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
