# Hand-Off Format

`handoff.md` is the single deliverable that gets passed downstream into a long-horizon DCF. It must be self-contained — a reader who has not seen the dialogue should be able to value the company from it (with reference to `sources.md` for verification).

The file has two sections:

1. **Human-readable summary** (sections A-F below) — the layer table, headline numbers, dominant drivers, growth path, bear/bull mechanisms, three-error check.
2. **DCF hand-off block** (section G below) — strict format the downstream DCF prompt ingests.

Write both. Order: A → B → C → D → E → F → G.

## A. Layer Summary Table

Table with one row per layer. Columns:

| Layer | Speculative? | Pool today (range, confidence) | Pool at maturity | Mature share (bear/base/bull) | Mature monetization (today's $) | Real pricing CAGR (D1/D2/D3) | Maturity year | Layer revenue at maturity, today's $ (bear/base/bull) |
|-------|--------------|-------------------------------|------------------|-------------------------------|--------------------------------|-------------------------------|---------------|--------------------------------------------------------|

Speculative layers tagged explicitly. Bear column shows zero for speculative layers (that's the discipline).

## B. Headline Numbers

```
Revenue at maturity, today's $:
  Bear:  $X
  Base:  $Y
  Bull:  $Z

Revenue at maturity, nominal $ at Y<N>:
  Bear:  $X
  Base:  $Y
  Bull:  $Z

Implied share of total addressed pool at maturity: X%
```

Cross-check: nominal = today's-$ × (1 + inflation)^N. If the cross-check fails, math-checker has not run or has been ignored. Re-run before saving.

## C. Dominant Fermi Drivers

The 2-3 inputs that move the answer most. Identified by sensitivity in the final aggregation.

Format: short paragraph naming the driver, its current confidence label, and what range of values produces the bear→bull spread. Example:

> Real pricing power in the speculative cloud-services layer is the dominant driver. Base case assumes +1.5% real / decade for two decades. Pushing this to +2.5% (bull) moves revenue at maturity by ~$X bn; dropping to 0% (bear) moves it by ~$Y bn.

If we got these wrong, the whole estimate is wrong. Surface them prominently.

## D. Growth Path Shape

State explicitly: stacked S-curves vs smooth fade. If stacked, the path stays elevated longer than a smooth geometric fade — preserve this in the period CAGRs.

Per-period summary:

| Period | CAGR (base) | Dominant contributing layer(s) | Layers saturating |
|--------|-------------|-------------------------------|-------------------|
| Y1-3 | X% | ... | ... |
| Y4-5 | X% | ... | ... |
| Y6-10 | X% | ... | ... |
| Y11-20 | X% | ... | ... |
| Y21-maturity | X% | ... | ... |

This feeds directly into the DCF's revenue ramp. If the table looks like a smooth geometric fade where the layer thesis is sequential, the model has been forced — fix before emitting.

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

## F. Three-Error Check

Before emitting the hand-off block, confirm:

1. **Did we pass the Fermi output through as actual revenue at maturity, or silently haircut it further?** ✅ / ❌
2. **Did we account for real pricing power AND inflation separately?** ✅ / ❌
3. **Does the growth path reflect stacked S-curves matching the layer thesis, or did we force a smooth fade?** ✅ / ❌
4. **Does the output contain exactly ONE bear, ONE base, ONE bull — with no parallel "alternative haircut base", "analyst-conservative base", or other duplicate scenarios?** ✅ / ❌

All four must pass. If any fails, fix the underlying model first, re-run math-checker, then re-emit. For check #4 specifically: if an expert review pushed the base down and the user accepted, the layer numbers must be updated in `state.json` and the old numbers removed from `handoff.md` — never both preserved.

## G. Hand-Off Block (DCF Input)

Strict format. The downstream DCF prompt parses this. Do not reword the labels.

```
Company: <NAME>
Ticker: <TICKER>
Exchange: <EXCHANGE>
Reporting currency: <CURRENCY>
Analysis date: <YYYY-MM-DD>
Maturity year (hand-off horizon): Y<N>

Revenue at maturity, today's $ (bear / base / bull): <X> / <Y> / <Z>
Revenue at maturity, nominal $ at Y<N> (bear / base / bull): <X> / <Y> / <Z>
Inflation assumption used: <%>

Implied revenue CAGR by period (PER SCENARIO — bear / base / bull rows REQUIRED):
                    Y1-3      Y4-5      Y6-10     Y11-20    Y21-maturity
  Bear:             <%>       <%>       <%>       <%>       <%>
  Base:             <%>       <%>       <%>       <%>       <%>
  Bull:             <%>       <%>       <%>       <%>       <%>

Per-scenario CAGRs derived from per-layer ramp schedules × per-scenario layer endpoints
(see "Per-layer ramp schedules" section below). Each row must compound to its
scenario endpoint within 2% — verified by hand-off contract test in math-checker.

Growth shape per scenario:
  Bear: <stacked S-curves | smooth fade | front-loaded | back-loaded>
  Base: <stacked S-curves | smooth fade | front-loaded | back-loaded>
  Bull: <stacked S-curves | smooth fade | front-loaded | back-loaded>

Peak-growth year per scenario:
  Bear: Y<N>
  Base: Y<N>
  Bull: Y<N>

Shape sanity: post-peak CAGRs must be monotonically decreasing per scenario, UNLESS a
mid-cycle reacceleration is traceable to a specific layer activating at that year.
Reacceleration without a named layer = math artifact = halt.

Dominant Fermi drivers:
  - <driver 1>: <one-line description>
  - <driver 2>: <one-line description>
  - <driver 3>: <one-line description>

Bear mechanism: <one line>

Bull adjacencies (asset-backed):
  - <layer name>: wedge = <wedge>
  - <layer name>: wedge = <wedge>

Speculative layers and weighting:
  - <layer name>: <% of base revenue at maturity> / <% of bull revenue at maturity> / 0 in bear

Per-layer maturity years (for reference):
  - <layer name>: Y<N>
  - <layer name>: Y<N>
  ...

Real pricing CAGR by layer (base, D1/D2/D3 in real %):
  - <layer name>: <%> / <%> / <%>
  - <layer name>: <%> / <%> / <%>
  ...

Per-layer ramp schedules:
  - <layer name>: activation Y<N>, peak Y<N>, maturity Y<N>, shape <s_curve | linear | front_loaded | back_loaded | stepped>
  - <layer name>: ...
  Per-scenario overrides (only if material catalyst differs by scenario):
    - <layer name>: bull activation Y<N> vs base Y<N> (reason: <regulatory acceleration / etc.>)

Per-scenario annual revenue series (RECOMMENDED — feeds DCF directly without rescale):
  Path: <absolute path to per-scenario annual revenue series JSON in state.json>
  Or inline (compact form, today's $):
    Bear: [Y0, Y1, Y2, ..., Y<maturity>] (today's $ M)
    Base: [Y0, Y1, Y2, ..., Y<maturity>] (today's $ M)
    Bull: [Y0, Y1, Y2, ..., Y<maturity>] (today's $ M)

Sources file: <absolute path to sources.md>
Dialogue file: <absolute path to dialogue.md>
State file: <absolute path to state.json>
```

## Validation Before Saving

Run the math-checker one last time before saving `handoff.md`:

- Headline numbers reconcile against the layer table.
- Nominal = today's-$ × inflation compounding.
- **Per-scenario period CAGRs compound to per-scenario endpoint within 2%.** This is the hand-off contract test. Run for bear, base, AND bull independently.
- **Per-scenario shape sanity**: peak-growth year identified per scenario; post-peak CAGRs monotonically decreasing OR mid-cycle reacceleration explicitly traceable to a named layer activating at that year. Unexplained U/W-shapes = halt.
- Bear / base / bull spreads non-degenerate (bear < base < bull).
- Speculative layers zero in bear.
- Hand-off contains exactly one bear, one base, one bull. No parallel "alternative haircut base" or duplicate scenarios anywhere in the document. If math-checker finds two distinct base totals, fail the check and force resolution.
- Per-layer ramp schedules populated for every layer. If a layer has `null` ramp, it cannot be aggregated to the per-scenario annual series — halt.

Math-checker writes its validation report to `~/.investing/companies/<TICKER>/<DATE>/.math-check.log`. Reference it in `handoff.md` footer.

## After Saving

Tell user:

> Hand-off saved to `~/.investing/companies/<TICKER>/<DATE>/handoff.md`. Pass the hand-off block (section G) into your DCF prompt. Sources in `sources.md`, full transcript in `dialogue.md`. Math-check log at `.math-check.log`.

If user asks for revision (e.g., wants a different horizon, a more aggressive bull case, a tougher bear mechanism), apply the change to `state.json`, re-run multiplication + math-checker, re-emit `handoff.md`. Don't edit `handoff.md` by hand — regenerate from state.
