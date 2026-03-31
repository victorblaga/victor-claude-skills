# Step 5: Generate Output Files

## Two Artifacts

Every council session produces:

```
council-report-[timestamp].html      # visual report for scanning
council-transcript-[timestamp].md    # full transcript for reference
```

Save both to the user's working directory (or the directory where context files were found in Step 1). Open the HTML report immediately after generating it.

---

## HTML Report

A single self-contained HTML file with inline CSS. Clean, scannable, professional — like a briefing document, not a dashboard.

### Structure

1. **The question** at the top
2. **The chairman's verdict** prominently displayed (most people read only this)
3. **Agreement/disagreement visual** — a simple grid or spectrum showing which advisors aligned and which diverged. Keep it clean and scannable.
4. **Advisor responses** — collapsible sections per advisor (collapsed by default), labeled by advisor name
5. **Peer review highlights** — collapsible section with the most important points from each review
6. **Footer** — timestamp + the question that was counciled

### Styling Guidelines

- White background, subtle borders, readable sans-serif (system font stack)
- Soft accent colors to distinguish advisor sections (no loud colors)
- Collapsible sections via `<details>`/`<summary>` (no JavaScript required)
- The chairman's verdict should be visually distinct — larger heading, light background, clear section breaks
- Mobile-readable (single column, no fixed widths)

---

## Markdown Transcript

The transcript is the full archival record. It includes:

- Original question (verbatim from user)
- Framed question (what was sent to advisors)
- All 5 advisor responses (labeled by advisor name)
- Anonymization mapping (which letter mapped to which advisor)
- All 5 peer reviews
- Chairman's full synthesis

Future councils on the same topic should reference this transcript to show how thinking evolved.

---

## Example: What Good Output Looks Like

From a product decision council ("$297 Claude Code course for non-technical solopreneurs"):

**Chairman verdict summary:**
- *Agrees:* The beginner solopreneur angle has real demand, but "Claude Code course" framing won't resonate with non-technical buyers
- *Clashes:* Price — Contrarian says $297 is too high vs competition; Expansionist says it's too low for the value
- *Blind spot caught:* The Outsider's point that "Claude Code" means nothing to the target buyer — the most important insight, missed by every other advisor
- *Recommendation:* Don't build the course yet. Validate with a live workshop first. Reframe entirely: sell the outcome, not the tool.
- *One thing first:* Run a $97 live workshop called "How to automate your first business task with AI" to 50 people. Don't mention Claude Code in the title.

This is the target level of specificity and directness.
