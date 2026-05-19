# Hand-Off Format

`handoff.md` is the single deliverable that gets passed downstream into a long-horizon DCF. It must be self-contained — a reader who has not seen the dialogue should be able to value the company from it (with reference to `sources.md` for verification).

The file has two sections:

1. **Human-readable summary** (sections A-F below) — the layer table, headline numbers, dominant drivers, growth path, bear/bull mechanisms, three-error check.
2. **DCF hand-off block** (section G below) — strict format the downstream DCF prompt ingests.

Write both. Order: A → B → C → D → E → F → G.

## A. Layer Summary Table

Table with one row per layer. Columns:

| Layer | Speculative? | Pool today (range, confidence) | Pool at maturity | Mature share (bear/low/base/high/bull) | Mature monetization (today's $) | Real pricing CAGR (D1/D2/D3) | Maturity year | Layer revenue at maturity, today's $ (bear/low/base/high/bull) |
|-------|--------------|-------------------------------|------------------|----------------------------------------|--------------------------------|-------------------------------|---------------|---------------------------------------------------------------|

Speculative layers tagged explicitly. Bear column shows zero for speculative layers (hard rule). Low/base/high/bull values for speculative layers come from per-layer analysis (no top-down weighting).

## B. Headline Numbers

**Revenue basis**: `<reported | economic_adjusted>`. If `economic_adjusted`, one-line bridge summary (e.g., "stripped $250M ad-fund pass-through; reported $467M → economic $217M"). If `reported`, line reads "no adjustments — reported = economic." Full bridge in `state.json` `economic_bridge.revenue_side`. All revenue figures below are on the stated basis.

```
Revenue at maturity, today's $:
  Bear:  $X     (absolute worst plausible)
  Low:   $X     (realistic adverse)
  Base:  $X     (bottom-up evidence-weighted)
  High:  $X     (realistic upside)
  Bull:  $X     (absolute best plausible)

Revenue at maturity, nominal $ at Y<N>:
  Bear:  $X
  Low:   $X
  Base:  $X
  High:  $X
  Bull:  $X

Implied share of total addressed pool at maturity (base): X%
```

Cross-check: nominal = today's-$ × (1 + inflation)^N. Scenario monotonicity: `bear < low < base < high < bull`. If either fails, math-checker has not run or has been ignored. Re-run before saving.

## C. Dominant Fermi Drivers

The 2-3 inputs that move the answer most. Identified by sensitivity in the final aggregation.

Format: short paragraph naming the driver, its current confidence label, and what range of values produces the bear→bull spread. Example:

> Real pricing power in the speculative cloud-services layer is the dominant driver. Base case assumes +1.5% real / decade for two decades. Pushing this to +2.5% (bull) moves revenue at maturity by ~$X bn; dropping to 0% (bear) moves it by ~$Y bn. Low and high lie between accordingly.

If we got these wrong, the whole estimate is wrong. Surface them prominently.

## D. Growth Path Declaration

Per-scenario period CAGRs. The **base** scenario's Y1-3 is anchored on management guidance + consensus (±3pp tolerance); the other four scenarios take reasoned spreads from base, each with a named mechanism (bear-mechanism intensity for bear/low; bull-adjacency intensity for high/bull).

| Period | Bear | Low | Base | High | Bull | Dominant contributing layer(s) | Layers saturating |
|--------|------|-----|------|------|------|-------------------------------|-------------------|
| Y1-3 | X% | X% | X% | X% | X% | ... | ... |
| Y4-5 | X% | X% | X% | X% | X% | ... | ... |
| Y6-10 | X% | X% | X% | X% | X% | ... | ... |
| Y11-20 | X% | X% | X% | X% | X% | ... | ... |
| Y21-maturity | X% | X% | X% | X% | X% | ... | ... |

**Y1-3 anchor**: cite management guidance midpoint + range and consensus analyst midpoint. Base must be within ±3pp of midpoint or carry an override mechanism. Non-base scenarios log their `override_reason` in `sources.md`.

**Growth shape per scenario**: stay-elevated / smooth-fade / front-loaded / back-loaded. Stay-elevated means later-period CAGRs do not fade dramatically because layer adjacencies are still contributing; smooth-fade means a single monotonically-decaying CAGR profile (typical for mature businesses with no late activators).

**Layer activation schedule** (drives the layer-schedule consistency check, not series generation):

| Layer | Activation year | Peak contribution year | Maturity year |
|-------|-----------------|------------------------|----------------|
| ... | ... | ... | ... |

The math-checker enforces that the declared CAGRs are compatible with this schedule (see "Validation Before Saving" below).

## E. Bear and Bull Mechanisms

### Bear (one specific path, not "things could go wrong")

Name the mechanism: substitution, commoditization, disintermediation, regulatory, value-pool migration, customer insourcing. Each layer's bear case shares the umbrella mechanism or names its own.

Format:

> **Bear mechanism**: substitution by `<named substitute>` in `<layer>`. Triggered by `<specific catalyst>`. Net effect: layer mature share drops from `<base>` to `<bear>`, with `<layer>` losing `<X%>` of revenue at maturity.

### Bull (each adjacency named with asset-backed wedge)

For each layer beyond core, name the asset-backed wedge that makes the layer credible:

> **Bull adjacencies**:
> - Layer `<X>`: wedge = `<customer data / installed base / network effect / etc.>`. Mature share `<bull>` vs `<base>` because `<wedge mechanism>`.
> - Layer `<Y>`: wedge = ...

Speculative adjacencies must include the **capability or asset forming today** (not "could plausibly enter X").

## F. Pre-Emit Checks

Before emitting the hand-off block, confirm:

1. **Single set of scenarios, no silent haircut.** Output contains exactly ONE bear, ONE low, ONE base, ONE high, ONE bull. No parallel "alternative haircut base", "analyst-conservative base", or duplicate scenarios. Fermi output passes through as actual revenue at maturity — no silent reduction. If an expert review pushed numbers down and the user accepted, the old numbers are removed from `handoff.md` (live in `state.json` history only). ✅ / ❌
2. **Real pricing power and inflation accounted for separately.** ✅ / ❌
3. **Per-scenario CAGRs match the layer activation schedule.** Layers activating Y4+ with ≥15% endpoint contribution require elevated CAGRs in their activation/peak-contribution period; scenarios with no late activator require monotonically decreasing post-Y3 CAGRs. ✅ / ❌
4. **Scenario monotonicity**: `bear < low < base < high < bull` for `revenue_at_maturity_today_$` and per-layer `layer_revenue_at_maturity_today_$`. ✅ / ❌
5. **Revenue hygiene check completed (Step 1)**: `economic_bridge.revenue_side.audit_status == "completed"`. `basis_used_in_layers` populated. If `economic_adjusted`, bridge table non-empty and rationale-cited. If `reported`, audit ran and found no quirks (not skipped). ✅ / ❌

All five must pass. If any fails, fix the underlying model first, re-run math-checker, then re-emit. If the audit was skipped, halt and run Step 1 before re-emitting.

## G. Hand-Off Block (DCF Input)

Strict format. The downstream DCF prompt parses this. Do not reword the labels.

```
Company: <NAME>
Ticker: <TICKER>
Exchange: <EXCHANGE>
Reporting currency: <CURRENCY>
Analysis date: <YYYY-MM-DD>
Maturity year (hand-off horizon): Y<N>

Last reported revenue (Y0, today's $): $<X>
Last reported YoY growth: <%>
(Y0 base + Y0 growth anchor the derived annual revenue series interpolation.)

Revenue basis: <reported | economic_adjusted>
Economic bridge summary: <one line — e.g., "stripped $250M ad-fund pass-through; reported $467M → economic $217M" — OR "no adjustments — reported = economic">
Full bridge: <absolute path to state.json> .economic_bridge.revenue_side
(All revenue figures above and below are on the stated basis. Downstream DCF must apply margin assumptions on the same basis. If economic_adjusted, the DCF normalizes peer benchmarks the same way at /tam-dcf Step 1.5 + Step 2.)

Revenue at maturity, today's $ (bear / low / base / high / bull): <X> / <Y> / <Z> / <W> / <V>
Revenue at maturity, nominal $ at Y<N> (bear / low / base / high / bull): <X> / <Y> / <Z> / <W> / <V>
Inflation assumption used: <%>

Scenario framing:
  Bear = absolute worst plausible (bear mechanism fully materializes; speculative layers = 0)
  Low  = realistic adverse (partial bear-mechanism materialization)
  Base = bottom-up evidence-weighted
  High = realistic upside (partial bull-adjacency realization)
  Bull = absolute best plausible (bull adjacencies fully active)

Implied revenue CAGR by period (PER SCENARIO — all 5 rows REQUIRED):
                    Y1-3      Y4-5      Y6-10     Y11-20    Y21-maturity
  Bear:             <%>       <%>       <%>       <%>       <%>
  Low:              <%>       <%>       <%>       <%>       <%>
  Base:             <%>       <%>       <%>       <%>       <%>
  High:             <%>       <%>       <%>       <%>       <%>
  Bull:             <%>       <%>       <%>       <%>       <%>

Y1-3 anchor: management guidance midpoint <%> (range <%> – <%>); consensus analyst
midpoint <%>. Base scenario's Y1-3 is within ±3pp of guidance midpoint OR carries an
`override_reason`. Bear / low / high / bull take reasoned spreads from base, each
with a named mechanism logged in `sources.md`.

Each row must compound to its scenario endpoint within 2% — verified by hand-off
contract test in math-checker. No silent rescaling.

Growth shape per scenario:
  Bear: <stay-elevated | smooth-fade | front-loaded | back-loaded>
  Low:  <...>
  Base: <...>
  High: <...>
  Bull: <...>

Peak-growth year per scenario:
  Bear: Y<N>
  Low:  Y<N>
  Base: Y<N>
  High: Y<N>
  Bull: Y<N>

Layer activation schedule (drives layer-schedule consistency check, not series generation):
  - <layer name>: activation Y<N>, peak-contribution Y<N>, maturity Y<N>
  - <layer name>: ...
  Per-scenario overrides (only when a specific catalyst differs):
    - <layer name>: bull activation Y<N> vs base Y<N> (reason: <one line>)

Layer-schedule consistency: for each of the 5 scenarios, the declared CAGRs must be
compatible with the activation schedule. Layers activating Y4+ contributing ≥15% of
endpoint require elevated CAGRs in their activation/peak-contribution period;
scenarios with no late activator require monotonically decreasing post-Y3 CAGRs.
Verified by math-checker.

Scenario monotonicity: bear < low < base < high < bull, both at the aggregated
revenue level and per-layer. Verified by math-checker.

Dominant Fermi drivers:
  - <driver 1>: <one-line description>
  - <driver 2>: <one-line description>
  - <driver 3>: <one-line description>

Bear mechanism: <one line — what has to go wrong for bear to materialize>
Low mechanism: <one line — partial-bear: which elements of the bear mechanism bite, which don't>

Bull adjacencies (asset-backed):
  - <layer name>: wedge = <wedge>
  - <layer name>: wedge = <wedge>
High realization: <one line — partial-bull: which adjacencies activate in high but not in bull>

Speculative layers per scenario (today's $ at maturity):
  - <layer name>: bear $0 / low $<X> / base $<Y> / high $<Z> / bull $<W>
  (Bear = 0 is hard rule. Other scenarios reflect per-layer analysis, not top-down weighting.)

Per-layer maturity years (for reference):
  - <layer name>: Y<N>
  - <layer name>: Y<N>
  ...

Real pricing CAGR by layer (base, D1/D2/D3 in real %):
  - <layer name>: <%> / <%> / <%>
  - <layer name>: <%> / <%> / <%>
  ...

Per-scenario annual revenue series (DERIVED — interpolated from period CAGRs):
  Path: <absolute path to per-scenario annual revenue series JSON in state.json>
  Note: derived via linear interpolation in growth-rate space, anchored on
        last-reported YoY growth at Y0, with per-period renormalization to honor
        each stated period CAGR exactly. Period CAGRs are the contract; this
        series is provided for DCF-consumer convenience and is regenerable.

Sources file: <absolute path to sources.md>
Dialogue file: <absolute path to dialogue.md>
State file: <absolute path to state.json>
```

## Validation Before Saving

Run the math-checker one last time before saving `handoff.md`:

- Headline numbers reconcile against the layer table (per scenario).
- Nominal = today's-$ × inflation compounding (per scenario).
- **Per-scenario period CAGRs compound to per-scenario endpoint within 2%.** Hand-off contract test. Run for bear, low, base, high, AND bull independently.
- **Y1-3 anchor test**: the **base** scenario's Y1-3 CAGR is within ±3pp of `aggregated.y1_3_guidance_anchor.midpoint`, OR carries a named `override_reason`. Bear / low / high / bull carry their own `override_reason` describing the bear-mechanism / bull-adjacency intensity that drives the spread from base.
- **Layer-schedule consistency test**: for each of the 5 scenarios, the declared CAGRs are compatible with the per-layer activation schedule. Layers activating Y4+ contributing ≥15% of endpoint require elevated CAGRs in their activation/peak-contribution period; scenarios with no late activator require monotonically decreasing post-Y3 CAGRs.
- **Scenario monotonicity test**: `revenue_at_maturity_today_$` and per-layer `layer_revenue_at_maturity_today_$` satisfy `bear < low < base < high < bull`. Strict violation = halt.
- Scenario spreads non-degenerate (bear < low < base < high < bull, strict inequalities).
- Speculative layers zero in bear.
- Hand-off contains exactly one bear, one low, one base, one high, one bull. No parallel "alternative haircut base" or duplicate scenarios anywhere in the document. If math-checker finds two distinct base totals, fail the check and force resolution.
- Per-layer `activation_schedule` populated for every layer. If any layer is missing the schedule, the layer-schedule consistency check cannot run — halt.
- **Revenue hygiene check completed**: `economic_bridge.revenue_side.audit_status == "completed"` and `basis_used_in_layers` populated. Hand-off block carries the `revenue_basis` field and the bridge summary. If absent, halt and run Step 1.

Math-checker writes its validation report to `~/.investing/companies/<TICKER>/<DATE>/.math-check.log`. Reference it in `handoff.md` footer.

## After Saving

Tell user:

> Hand-off saved to `~/.investing/companies/<TICKER>/<DATE>/handoff.md`. Pass the hand-off block (section G) into your DCF prompt. Sources in `sources.md`, full transcript in `dialogue.md`. Math-check log at `.math-check.log`.

If user asks for revision (e.g., wants a different horizon, a more aggressive bull case, a tougher bear mechanism), apply the change to `state.json`, re-run multiplication + math-checker, re-emit `handoff.md`. Don't edit `handoff.md` by hand — regenerate from state.
