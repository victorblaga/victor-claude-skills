---
name: tam-analysis
description: >
  Conversational bottom-up Fermi TAM analysis for a single growth stock. Builds defensible
  revenue-at-maturity across 5 scenarios (bear / low / base / high / bull) layer by layer through slow per-anchor dialogue, with
  cited research for every number, code-validated math, per-layer maturity + real pricing
  power, and a final DCF-ingestible hand-off block. Trigger ONLY on explicit invocation:
  "/tam-analysis", "/tam-analysis <TICKER>", "/tam-analysis resume <TICKER>". Do not
  trigger on generic phrases like "let's value X", "analyze TAM for X", "what's the TAM of X" —
  this is a deliberate, multi-session workflow the user opts into by name.
---

# TAM Analysis

Bottom-up Fermi TAM build for a single company. Produces revenue-at-maturity across 5 scenarios (bear / low / base / high / bull) in today's $ and nominal $, plus a clean hand-off block for a downstream long-horizon DCF.

Scenario framing:
- **Bear** = absolute worst plausible (bear mechanism fully materializes; speculative layers = 0 by hard rule)
- **Low** = realistic adverse ("things don't go very well"; partial bear-mechanism materialization)
- **Base** = bottom-up evidence-weighted (the central case, anchored on management guidance for Y1-3)
- **High** = realistic upside ("things go above base expectations"; partial bull-adjacency realization)
- **Bull** = absolute best plausible (bull adjacencies fully active)

The discipline this enforces: a TAM build that could surface a multi-layer compounding trajectory (core → adjacent products → international → speculative new business) without hand-waving. Bull cases asset-backed. Bear cases mechanism-specified. Base case evidence-weighted, never silently conservative. Low and high carry partial-bear and partial-bull intensities respectively. Math-checker enforces `bear < low < base < high < bull` monotonicity.

**This skill does TAM only.** The hand-off block is designed for a future DCF skill or for the user's existing DCF prompt. Do not attempt the DCF here.

## Agentic Execution Notes (Claude Opus 4.7)

- **Effort**: Use `xhigh` for orchestration and pushback reasoning. Use `medium` (Sonnet) for anchor-research subagents. Use `medium` for math-checker (it runs code, doesn't need deep reasoning).
- **Subagents are a budget tool**: Dispatch anchor-research and math-check work to subagents so the main thread stays clean across a long multi-layer session. The main thread holds the dialogue and the state.
- **Parallel research only when independent**: If a layer needs three anchors (e.g., population, per-capita usage, online conversion %), dispatch them in parallel. Do not parallelize when one anchor's range determines the next anchor's scope.
- **Slow by default**: This skill is intentionally per-anchor. Do not batch multiple anchors into one turn unless the user issued `faster` or `autopilot`.
- **Save before talking**: Every confirmed anchor, every layer summary, every multiplication result is written to disk before being summarized in chat. The dialogue is recoverable from `dialogue.md` after a context compaction.

## Invocation

Explicit only. Triggers:

- `/tam-analysis` — ask which company
- `/tam-analysis <TICKER>` — start fresh on TICKER
- `/tam-analysis resume <TICKER>` — load latest session for TICKER and continue
- `/tam-analysis <TICKER>` when a session already exists → ask: "resume latest from `<date>`, or start fresh?"

## Output Location

```
~/.investing/companies/<TICKER>/<YYYY-MM-DD>/
├── state.json      # machine-readable session state (resumable)
├── dialogue.md     # running transcript (survives context compaction)
├── sources.md      # every cited anchor: value, source URL, quoted snippet, retrieval date
└── handoff.md      # final DCF-ingestible block + human-readable summary
```

Create the folder on Step 0 confirmation. Write to all four files continuously throughout the session — never wait until the end.

Schema details: `references/state-schema.md`.

## Working Pattern: Per-Anchor Confirm

The skill walks the analysis one anchor at a time. An "anchor" is any number that materially shapes the result: population, per-capita usage, online penetration, average price, take rate, market share at maturity, real pricing CAGR, inflation rate, geographic split, segment mix.

For each anchor:

1. State what you're about to size and why it matters at this point in the build.
2. Dispatch the anchor-researcher subagent (`agents/anchor-researcher.md`) with the specific question.
3. Receive value + cited range + confidence + URL + quote.
4. Save to `sources.md`.
5. Present to user: value, range, source, confidence, your proposed pick within the range, reasoning.
6. Wait for user response. User may: accept, pick a different number in-range, pick a number out-of-range (triggers pushback — see below), defer, or jump.

Do NOT proceed to the next anchor without a confirmed value. Do NOT silently fill gaps. If the user is ambivalent, ask one clarifying question; if still ambivalent, log the choice as "unverified, low confidence" and proceed.

### Pacing Override Commands

User can issue these at any turn:

| Command | Effect |
|---------|--------|
| `faster` | Finish current layer without per-anchor confirms; present layer summary; resume per-anchor for next layer |
| `autopilot` | Run all remaining layers without confirms; produce full hand-off at the end |
| `pause` | Return to per-anchor confirms (cancel a prior `faster`/`autopilot`) |
| `back` | Re-open the last confirmed anchor for revision |

Apply commands immediately. Announce the new mode. When `autopilot` or `faster` is active, still write to `sources.md` and run the math-checker — discipline does not relax with pace.

## Step 0 — Setup

First message of every fresh session. Confirm the following before proposing any layer structure:

1. **Company identification**. Name, ticker, exchange, reporting currency. Always confirm: "To confirm, this is the `<TICKER>` stock — `<short company description>`?" Wait for user yes.
2. **Current state**. Last reported annual revenue and the geographic + product footprint. Source from the latest 10-K, 20-F, or annual report. Cite. This is the anchor today's-$ figure.
3. **Asset-backed wedge today**. What does the company have that others don't? Run through the standard inventory: customer relationships, data, distribution, installed base, real estate, regulatory position, brand, technology, network effects, payments / financial flows, workflow ownership. Surface 2-3 strongest wedges; ask user to confirm or correct. The wedge inventory drives the speculative layer later — do not skip.
4. **Adjacencies on the user's mind (optional)**. Ask: "Any adjacencies you already want me to size for this company, or should I surface them as we go?" This is the only optional input — if the user has nothing in mind, say "no" and the skill surfaces adjacencies organically from the asset-backed wedge inventory.

**Do NOT ask for a directional thesis (bull / bear / uncertain).** The point of this skill is to *discover* a thesis through the bottom-up build, not to defend a prior. Default to "challenge me" mode — push back on both wishful thinking and silent conservatism for every anchor.

**Do NOT pick the maturity horizon here.** Horizon is proposed at the END, after all layers and per-layer maturities are known.

After confirmation, propose the layer structure adapted to the business model — see `references/layer-protocols.md`. Wait for user approval before starting Layer 1.

## Step 0.5 — Speculative Layer Proposal

Before walking the layers, surface speculative adjacency candidates from the Step 0 wedge inventory. The skill proposes a list of 2-4 candidates; user picks which (if any) to include, can add their own, can include multiple.

Each candidate must include:
- **Capability or asset forming today**: what's emerging that points to the new business.
- **Credible commercial expression**: the named product / service / market the capability could enter.
- **Why this isn't free**: what would have to be true for it to materialize.

Tag accepted speculative layers as `speculative: true` in `state.json`. They get priced conservatively in base, generously in bull, **zero in bear**.

This is the slot that catches the "core retailer building datacenters for itself → cloud-services business" pattern. The skill must surface at least one candidate even when the user doesn't ask.

## Per-Layer Protocol

Walk each layer through these eight steps. Full details and examples in `references/per-layer-protocol.md`. Summary:

1. **Define the demand unit precisely**. What's counted? Who buys? What drives usage? How is it monetized? Confirm with user.
2. **Build the pool today**. Top-down from authoritative sources via anchor-researcher. Cite. Show ranges. For consumer / retail, ground in regional demographic decomposition (population × per-capita usage by region) before aggregating.
3. **Project to per-layer maturity**. Pool growth = population × per-capita usage × structural shifts. Show pool today, Y10, Y20, at this layer's maturity. Per-layer maturity year is set here, not globally. Confidence label per driver. Math-checker validates compounding.
3.5. **Set the layer activation schedule**. Each layer captures `activation_year` (when revenue begins ≥1% of layer maturity), `peak_contribution_year` (year of peak %-contribution to consolidated growth), and `maturity_year`. Most layers share the schedule across all 5 scenarios — only differ when a specific catalyst drives different timing per scenario. **Why this matters**: the per-scenario growth path is declared per scenario at the multiplication step (period CAGRs), and the activation schedule feeds a math-checker consistency test that flags when declared CAGRs are incompatible with the layer thesis (e.g., a layer activating Y4 contributing ≥15% of endpoint but Y4-5 CAGR < Y1-3 — layer is invisible).
4. **Propose 2-3 scope options** — tight / plausible / aggressive. Explain the structural difference, not just the number. Don't pick — user picks.
5. **Wait for user scope**. Geography, segment, product breadth, adjacency inclusion are judgment calls dependent on the thesis.
6. **Size with explicit confidence**. high / moderate / low / unknown per anchor. Push back when user is too generous AND when user is too conservative (silent conservatism is as bad as wishful thinking).
7. **Check overlap with adjacent layers**. Apply explicit haircuts. Track them in `state.json` so we don't double-haircut in the multiplication step.

After every layer's step 3 (the pool projection), dispatch the math-checker subagent (`agents/math-checker.md`) to validate the pool compounding via Python. Do this even in `autopilot` mode.

## Multiplication Step

Only after ALL layers are pool-sized. Four sub-steps per layer per scenario (bear / low / base / high / bull). Full reference: `references/multiplication-protocol.md`.

1. **Mature share / penetration**. Anchor on real category-leader precedents (table in references). Don't pick a number without citing precedent. Pick all 5 scenario values per layer. Math-checker enforces monotonicity `bear ≤ low ≤ base ≤ high ≤ bull`.
2. **Mature monetization in today's $, today's mix**. Use the metric appropriate to the model (ARPU / sales-per-store / take rate / ASP / NIM / etc.) — full mapping in references. Build from current actuals, peer benchmarks, explicit mix shift. All 5 scenarios.
3. **Real pricing power per year (above inflation)**. Per layer. Express as fading profile in real %. All 5 scenarios. Math-checker validates compounding.
4. **Inflation overlay (apply LAST)**. Today's-$ output → nominal $ at the per-layer maturity year. Anchor inflation on the long-run expectation for the reporting currency. Math-checker validates real→nominal conversion.

Before declaring per-scenario CAGRs, **dispatch anchor-researcher for Y1-3 guidance + consensus** (mandatory). The dispatch payload: "For `<TICKER>`, fetch (a) latest management revenue guidance for next FY (range + midpoint, with source), (b) 2-3 year consensus analyst revenue estimates. Express both as implied YoY growth rates from the last reported FY." Result saved to `aggregated.y1_3_guidance_anchor`. The **base** scenario's Y1-3 CAGR is picked within ±3pp of guidance midpoint, OR with a named `override_reason` logged in `sources.md`. The other 4 scenarios take reasoned spreads from base, each with a named `override_reason` describing the bear-mechanism / bull-adjacency intensity that drives the spread (typical: bear -4 to -6pp; low -2 to -3pp; high +1 to +2pp; bull +3 to +5pp).

Walk the user through declaring per-scenario period CAGRs (Y1-3, Y4-5, Y6-10, Y11-20, Y21-maturity), one period at a time across all 5 scenarios. Per-anchor confirm. Later periods reflect the layer thesis (stay-elevated when adjacencies activate; smooth-fade when no late activators).

Dispatch math-checker after each layer's multiplication. Dispatch again at final aggregation to:

- Validate the cross-layer sum per scenario (5 scenarios).
- Run the **hand-off contract test**: per-scenario declared CAGRs compound to per-scenario endpoint within 2%. Fail-stop if any scenario violates.
- Run the **Y1-3 anchor test**: base within ±3pp of guidance midpoint (or override); non-base scenarios carry their own `override_reason` for the spread.
- Run the **layer-schedule consistency test**: for each of the 5 scenarios, the declared CAGRs are compatible with the per-layer activation schedule (late-activator check + smooth-fade check, see `agents/math-checker.md`).
- Run the **scenario monotonicity test**: `bear < low < base < high < bull` at aggregated and per-layer levels. Strict inequality; equality requires logged justification.
- Run the **speculative-bear-zero check**: any layer flagged `speculative: true` must have `layer_revenue_at_maturity_today_$.bear == 0`. Hard rule.
- Derive per-scenario annual revenue series via linear interpolation in growth-rate space, anchored on `last_reported_yoy_growth`, with per-period renormalization. Saved to `aggregated.annual_revenue_today_$_per_scenario` as a derived artifact regenerable from the CAGRs.

The hand-off block in `handoff.md` emits per-scenario period CAGRs (bear/low/base/high/bull rows) as the contract. Downstream `/tam-dcf` consumes the CAGRs and the derived annual series directly — no silent rescaling permitted.

## Pushback Discipline

When the user picks a number outside the cited source range — too high OR too low — the skill soft-blocks:

> Your `<anchor>` of `<X>` is `<N>%` above the cited range `[<low>, <high>]`. The sources support `<Y>` as a defensible counter, because `<one-line reasoning>`. What's your mechanism?

Accept the user's number after they name a mechanism. Log the mechanism in `sources.md` next to the override. Same pattern when user is too low — silent conservatism is the more common failure on growth-stock TAMs.

## No Magic Haircuts — Disagreement Must Land in the Numbers

**Hard rule. Read it once, follow it always.**

When a domain-expert subagent (or an analyst review) disagrees with the bottom-up base case, the disagreement MUST be resolved in one of three ways, never as a parallel "haircut scenario" living alongside the base:

1. **Revise the actual layer assumptions.** If the expert says "L1 mature ASP $1,236 is aggressive — defensible is $1,000," and the user agrees: the base-case ASP becomes $1,000. The old $1,236 disappears from the analysis. Log the revision + reasoning in `sources.md` for the affected anchors.
2. **Reject the expert view.** If the user disagrees with the expert: the base stays as-is, and the user's reason for rejecting goes into `sources.md`. The expert's concern is *not* preserved as a "conservative alternative."
3. **Fold the concern into the bear / low mechanism.** If the expert's concern is "this *could* fail to materialize, and here's why," that's a bear-case mechanism — strengthen the bear scenario (full materialization) and the low scenario (partial materialization) accordingly. The base does not get a defensive haircut; bear and low absorb the risk at their respective intensities.

**Never** output a "conservative alternative base" or "analyst-haircut base" alongside the bottom-up base. There is ONE bear, ONE low, ONE base, ONE high, ONE bull. If two bases exist in the output, the analysis is broken.

The reasoning: parallel scenarios are an excuse to avoid the decision. The 5-scenario spread (bear/low/base/high/bull) already exists to capture upside and downside; layering an additional "haircut base" on top of the spread is double-dipping on conservatism, undefined under the model, and corrosive to downstream DCF discipline.

Apply the same rule to math-checker discrepancies, user pushback, and any other source of revision: the numbers in `state.json` and `handoff.md` change, or they don't. Don't carry both.

This applies to: pool anchors, mature share, monetization metric, real pricing CAGR.

## Domain-Expert Subagent (On-Demand)

When the user wants an expert opinion, sanity check, or pressure-test on a specific question — most commonly while sizing a speculative layer, contesting a mature-share precedent, or judging real pricing power — dispatch the domain-expert subagent (`agents/domain-expert.md`).

Trigger phrases from the user:

- "Ask an expert about X"
- "Get a domain expert opinion on this"
- "What would a [X] analyst say?"
- "Pressure-test this with an expert"
- "Is this layer credible? Get an expert take."
- "Confirm this with someone who knows the space"

The skill **may also proactively offer** dispatch when a speculative layer is being sized or a contested precedent surfaces:

> "Want me to dispatch a [specific persona] to pressure-test the speculative cloud-services layer before we size it?"

Dispatch is always user-confirmed — never run silently.

**Persona is picked by the main flow** to match the specific question, not the company overall. AMZN's ad-network layer → ad-tech expert. AMZN's logistics moat → supply-chain operator. The persona composition pattern: "veteran [primary domain] analyst + ex-[adjacent operator role]" — forces triangulation between markets view and operator view. Full persona examples in `agents/domain-expert.md`.

Model tier: opus xhigh. This subagent is purchased for judgment.

Output is saved (appended) to `~/.investing/companies/<TICKER>/<DATE>/expert-opinions.md` for later reference. The opinion is presented to the user immediately and may shift the analysis — log how it shifted in `dialogue.md`.

## Math-Checker

Dispatched to a fresh Sonnet subagent (`agents/math-checker.md`). Runs at:

- After every layer's **pool projection** (step 3): validates pool compounding from today → maturity.
- After every layer's **multiplication step**: validates real-pricing compounding, today's-$ math, real→nominal conversion.
- At **final aggregation**: validates cross-layer sum, per-period CAGRs for the growth path, hand-off block numbers.
- **On-demand**: if the user says "check the math" or "recheck" at any turn, dispatch immediately on the current state.

The math-checker writes a Python script in a temp file, runs it, reports any discrepancy. If it finds one, present to user before continuing.

## Horizon Proposal (Final Step Before Hand-Off)

After every layer has its own maturity year, propose the **overall hand-off horizon** for DCF consumption. Logic:

- Take the latest per-layer maturity (longest-running layer drives the horizon).
- Cap at Y40 unless the user has a specific reason for longer.
- Floor at Y15 unless every layer matures earlier.
- Announce: "Longest-running layer is `<X>` at Y`<N>`. Propose Y`<N>` (or round to Y15/Y25/Y40) as the hand-off horizon. Accept?"

The hand-off block reports revenue-at-maturity at this single horizon. Each layer's contribution at that horizon is its mature revenue (if already mature) or its still-ramping projection at that year.

## Final Output

Save to `handoff.md`. Structure:

- **A. Layer summary table** — pool today (range, confidence), pool at maturity, mature share (bear/low/base/high/bull), mature monetization in today's $, real pricing CAGR, layer revenue at maturity in today's $ (bear/low/base/high/bull).
- **B. Headline numbers** — total revenue at maturity in today's $ (5 scenarios); same in nominal $ at Y`<N>`; implied share of total addressed pool at maturity (base).
- **C. Dominant Fermi drivers** — the 2-3 inputs that move the answer most.
- **D. Growth path declaration** — per-scenario period CAGRs (5 rows: bear/low/base/high/bull) for Y1-3 / Y4-5 / Y6-10 / Y11-20 / Y21-maturity. Y1-3 base anchored on management guidance + consensus. Per-scenario growth shape labels (stay-elevated / smooth-fade / front-loaded / back-loaded). Layer activation schedule listed alongside for the consistency check.
- **E. Scenario mechanisms** — bear (absolute worst: substitution / commoditization / disintermediation / regulatory / value-pool-migration / customer-insourcing path); low (which elements of the bear mechanism partially materialize); high (which bull adjacencies partially realize); bull (each adjacency named with its asset-backed wedge).
- **F. Three-error check** — did we silently haircut? real-vs-nominal accounted for separately? do declared CAGRs match the layer activation schedule (layer-schedule consistency)? Plus monotonicity (bear < low < base < high < bull) and speculative-bear-zero. Fix before emitting hand-off.
- **G. Hand-off block** — the clean DCF-ingestible block. Exact format in `references/handoff-format.md`.

Tell user: "Hand-off saved to `<path>/handoff.md`. Pass that block into your DCF prompt. Sources in `sources.md`, full transcript in `dialogue.md`. Want me to dispatch a final math-check?"

## Resume

`/tam-analysis resume <TICKER>` workflow:

1. Find the most recent `~/.investing/companies/<TICKER>/<DATE>/` folder.
2. Read `state.json` — identify the last completed step (Step 0 done? which layers complete? at multiplication? at horizon-proposal?).
3. Read tail of `dialogue.md` to recover the most recent conversational context.
4. Re-present a one-paragraph summary of where we left off.
5. Ask: "Pick up from `<last-step>`, or revise an earlier step?"
6. Continue per-anchor from the appropriate point.

Resume must survive context compaction within a session too. After any context compaction, re-read `state.json` and the dialogue tail before responding.

## Auto-Detect on Fresh Invocation

When user runs `/tam-analysis <TICKER>` without `resume`, but a folder already exists:

> Found existing session for `<TICKER>` from `<date>`. Last step: `<last-step>`. Resume that, or start fresh in a new dated folder?

Never silently start fresh — losing in-progress state on a typo would be expensive.

## Throughout the Conversation

These hold for every turn:

- **Challenge wishful thinking**: if user assumes entry to a market with no asset-backed wedge, force them to name the wedge or downgrade the layer to speculative.
- **Challenge silent conservatism**: flat penetration in a compounding category? haircutting for competition that doesn't actually exist? push back.
- **Use real peer data**: pull competitor TAM claims with scope notes. Tell user which look promotional vs defensible. Don't sum overlapping vendor TAMs — reconcile scope first.
- **Anchor on actuals**: today's prices, back-solved ARPU and unit economics from disclosed financials, observed take rates, store-level sales density, current GMV.
- **Track confidence honestly**: tell user which assumptions you'd defend to a hostile reader and which are speculative.

## What Not to Do

- Don't multiply pool × share × monetization × pricing until ALL layers are pool-sized. Early anchoring destroys discipline.
- Don't pick scope for the user. Propose tight / plausible / aggressive; let them choose.
- Don't apply inflation at intermediate steps. Real first, nominal last.
- Don't fold a speculative adjacency into the base case at the same weight as proven layers. Conservative in base, generous in bull, zero in bear.
- Don't claim a number is sourced when it's assumed. Confidence label: `unknown` is a valid answer.
- Don't quietly haircut a layer's revenue at the multiplication step "for safety". Margin of safety lives in the bear/bull spread and downstream in the DCF, not in silent base-case haircuts.
- **Don't output a parallel "analyst-haircut base" or "conservative alternative base"** alongside the bottom-up base. ONE bear, ONE low, ONE base, ONE high, ONE bull. Expert disagreements get resolved by revising the numbers, rejecting the expert, or strengthening the bear / low — never by carrying both. See "No Magic Haircuts — Disagreement Must Land in the Numbers."

## Files in This Skill

| File | Purpose |
|------|---------|
| `SKILL.md` | This file. Main flow. |
| `references/layer-protocols.md` | Layer structures by business model (retailer, marketplace, SaaS, industrial, consumer-sub, financial services, payments) |
| `references/per-layer-protocol.md` | Full 7-step protocol with examples for each step |
| `references/multiplication-protocol.md` | Mature share precedents, monetization metric mapping, real-pricing tiers, inflation rules |
| `references/handoff-format.md` | Exact hand-off block schema + output sections A-G |
| `references/state-schema.md` | `state.json` structure, `sources.md` / `dialogue.md` / `handoff.md` formats, resume contract |
| `agents/anchor-researcher.md` | Subagent prompt for cited anchor lookup |
| `agents/math-checker.md` | Subagent prompt for code-validated math discipline |
| `agents/domain-expert.md` | On-demand opus-xhigh subagent for expert opinion / pressure-test (persona picked per question) |

Read references on demand — do not preload everything. Read `references/layer-protocols.md` at Step 0 (you need it to propose the layer structure). Read `references/per-layer-protocol.md` when you enter Layer 1. Read `references/multiplication-protocol.md` at the multiplication step. Read `references/handoff-format.md` at hand-off. Read `references/state-schema.md` once at session start (you need the schema to write `state.json` correctly).
