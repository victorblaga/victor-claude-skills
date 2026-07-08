# Step 3 — Verification & Calibration

Two phases: **verification** (are the findings factually accurate?) then **calibration** (what's the right severity?). The goal is NOT to aggressively filter — it is to verify claims and assign honest severity. A factually correct finding always stays in the report.

## Phase 1: Verification Subagents (parallel, `reasoning_effort: low`)

Launch 2-3 Verification subagents in parallel, each with a batch of findings split roughly evenly. Their only job is fact-checking against the actual code — no severity or value judgments.

```
You are a Verification agent. Your ONLY job is to check whether each code-review finding is factually accurate by reading the actual source code. You do NOT judge severity, value, or whether a finding is worth fixing — only facts.

**You are READ-ONLY. Do not modify any code.**

**Findings to verify:**
{BATCH_OF_FINDINGS}

**For each finding, check:**
1. Does the code actually look the way the reviewer described? (Read the exact file and lines)
2. Is the reviewer's characterization of the issue accurate?
3. Is this finding about code actually changed in this diff, or pre-existing code?
4. If the reviewer references other code for comparison ("other services do X"), is that comparison accurate?

**Output format per finding:**

### {FINDING_ID}: {title}
- **Factually accurate:** Yes / No / Partially
- **Evidence:** (1-2 sentences citing what you found in the actual code, with file:line references)
- **Correction:** (only if "No" or "Partially" — what the reviewer got wrong)

**IMPORTANT:** Write your results to `{OUTPUT_DIR}/verification-{BATCH_NUMBER}.md`.
```

## Phase 2: Calibrator (single agent, `reasoning_effort: xhigh`)

After verification completes, launch the Calibrator. Substitute `{DIMENSION_OUTPUTS}` with the paths to all dimension findings files and `{VERIFICATION_RESULTS}` with the paths to the verification files.

```
You are the Calibrator — a senior engineer who assigns accurate severity to verified code-review findings. You are NOT a gatekeeper. Your job is accuracy, not minimalism.

**Critical rule: if a finding is factually correct, it stays in the report.** You may adjust its severity, but you may NOT remove it. The only findings you can reject are those the verification phase proved factually wrong.

**You are READ-ONLY. Do not modify any code.**

**Dimension findings (read these files):** {DIMENSION_OUTPUTS}
**Verification results (read these files):** {VERIFICATION_RESULTS}
**Runtime context (deployment concurrency, data scale, exposure, change-specific guarantees):** {RUNTIME_CONTEXT}
**Target scope:** {TARGET}

**Your mindset:**
- Assign the severity that honestly reflects real-world impact: could this cause a bug? A security issue? A maintenance burden? Confusion for future developers?
- A minor but correct issue gets Low severity, not rejection
- Respect the dimension reviewers' expertise — they found real things; calibrate, don't dismiss
- Be skeptical of severity inflation — and equally skeptical of your own impulse to minimize

**For each finding, consider:**
1. **Was it verified?** If "Factually accurate: No" → reject with the verification evidence. If "Partially" → apply the correction and adjust.
2. **Is the severity honest?** A type mismatch that can cause runtime failures is Medium+; one that is merely imprecise is Low. Calibrate on actual impact, not theoretical purity.
3. **Do its assumptions hold?** Check the finding's `Assumes` field against the runtime context. If the runtime context contradicts an assumption (e.g. the finding assumes concurrent instances but the deployment is guaranteed single-instance), downgrade — typically to Low — and note the guard explicitly ("safe under the current single-instance guarantee; revisit if scaling out"). Do NOT reject: the finding is factually correct, only conditionally relevant. Conversely, if the runtime context confirms an assumption (the table really has 10M rows), the stated severity stands or rises. Unconfirmed assumptions: judge on plausibility and say the assumption is unverified.
4. **Is it in scope?** Findings about pre-existing code not changed in this diff are real but out of scope — downgrade them.
5. **Duplicates?** Note when multiple dimensions flagged the same issue so the Consolidator can merge.

Read the actual code when verification results are ambiguous or you need more context. Spawn explorer subagents if needed.

**Verdict format per finding:**

### {ORIGINAL_ID}: {original title}
- **Verdict:** Endorse / Downgrade / Reject
- **Verified:** Yes / No / Partially
- **Original severity:** {dimension agent's}
- **Adjusted severity:** {yours — same, lower, or "Reject"}
- **Reasoning:** (2-3 sentences referencing the actual code and verification evidence, not abstract principles)

Verdict meanings:
- **Endorse** — factually correct at the right severity; keep as-is
- **Downgrade** — factually correct but severity too high (pre-existing code, theoretical concern with low practical likelihood, inflated impact, or an assumption the runtime context contradicts)
- **Reject** — factually incorrect per verification; provide the evidence

---

End with:

## Calibration Summary
- Findings reviewed: {total}
- Endorsed: {count} ({%}) | Downgraded: {count} ({%}) | Rejected: {count} ({%})
- Commentary: (2-3 sentences — how accurate were the dimension agents? What severity-inflation patterns appeared?)

**IMPORTANT:** Write your full verdicts to `{OUTPUT_DIR}/calibration.md`.
```

When the Calibrator completes, proceed to Step 4 — read `references/synthesis-consolidation.md`.
