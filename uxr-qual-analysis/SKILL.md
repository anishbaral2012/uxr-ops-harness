---
name: uxr-qual-analysis
description: Synthesize qualitative research into traceable findings, preserving uncertainty, counter-evidence, and participant privacy.
---

# UX Qualitative Analysis Skill

Synthesizes raw user research inputs (interview scripts, discussion guides, research plans) into structured themes and insights ready for reporting.

Use the source manifest, evidence ledger and mechanical verification in [study schema](../references/study-schema.md). Human review remains necessary; a passing script cannot validate the interpretation or consent.

## Quick Reference

| Step | Action |
|------|---------|
| 0 | Gather and validate inputs |
| 1 | Read and synthesize all interview scripts |
| 2 | Build themes + insights linked to research plan |

Reference files (read on demand):
- [references/synthesis-rules.md](references/synthesis-rules.md) — pseudonymization, quote handling, and evidence assessment.
- [references/synthesis-behavior.md](references/synthesis-behavior.md) — evidence standards, prohibited behaviors, output format, and gap handling.
- [examples/sample-theme.md](examples/sample-theme.md) — one fully-worked theme to model output on.

---

## Step 0 — Gather and Validate Inputs

### Required
- **Research plan** (minimum required) — establishes *why* the research was done, expected outcomes, and success criteria.

### Optional but valuable
- **Discussion guide** — reveals intended question flow and probing areas.
- **Consented research data** — transcripts, notes, observations, diary entries, or other appropriate source material. No synthesis of findings is possible without actual research data.

### If inputs are missing
- If **no research plan** is provided: ask for it before proceeding. Explain that the research plan is needed to frame insights against objectives. Do not proceed without it.
- If **discussion guide is missing**: that's fine — infer research context from the research plan.
- If **some transcripts are missing**: note this in the analysis output and proceed with what's available.

### Clarifying questions
**First, derive what you can from the documents** before asking. Specifically:
- Participant count → count distinct participant IDs in the reviewed manifest, not files or sessions. Report the number represented in the analyzed sources separately from the number recruited.
- Study type → usually stated in the research plan.
- Date range → from session metadata or the plan.

Ask the user **only** if the following remain unclear after reading the materials. Group into one message:
1. Is this a usability study or generative research? (affects how task success/failure is tracked)
2. Are there specific research objectives to prioritize if not all can be answered from the data?

---

## Step 1 — Read and Synthesize Interviews

Go through each interview script individually. For each one:

- Identify the participant's role, location, industry, and primary responsibilities (for the Participant Overview table).
- Note key statements, pain points, mental models, behaviors, and reactions.
- Flag direct quotes that are vivid, specific, and attributable to a participant (Px).
- Note tasks where the participant succeeded or struggled (usability studies).
- Track single-occurrence findings separately — don't discard, but don't elevate prematurely.

For pseudonymization, quote selection, evidence assessment, and decision rules, see [references/synthesis-rules.md](references/synthesis-rules.md). For evidence standards and bias checks, see [references/synthesis-behavior.md](references/synthesis-behavior.md).

---

## Step 2 — Build Themes and Structure

Synthesis proceeds in two cycles. Do not skip the second.

**First cycle (per transcript):** Assign short codes to data segments. Use the participant's own words where possible. Track what each participant said.

**Second cycle (across sources):** Cluster first-cycle codes into patterns. Name each pattern as an evidence-supported statement, not just a topic label. State why only when the evidence supports it.

### Themes
A theme:
- Relates to a research objective or is identified as an unexpected finding.
- Has a headline that is an *insight statement* (not a topic label).
  - ✅ "Buyers lose trust when order status is invisible"
  - ❌ "Order Visibility"
- Groups related insights where the data supports them.
- Has traceable supporting excerpts and a distinct participant count where applicable.
- Documents the counter-evidence search and distinguishes contradiction from silence or not being asked.

Theme blocks stay recommendation-free. The design implication of each theme is carried forward and consolidated in the separate Strategic Recommendations section, where each recommendation names its source theme. Do not place a recommendation field inside a theme block.

Describe observed patterns accurately. Offer mechanisms as interpretations only when supported, label uncertainty, and distinguish observation, participant explanation, and analyst inference. A descriptive finding is preferable to an unsupported causal claim.

**Recommendation chain:** Each recommendation must trace back through: research question → finding → mechanism → implication → recommended action. A recommendation without a supporting finding is an opinion.

See [examples/sample-theme.md](examples/sample-theme.md) for a fully-worked example. Output format per theme must follow [references/synthesis-behavior.md](references/synthesis-behavior.md).

### Negative Case Check (required before finalizing themes)
For each theme ask: "What data contradicts or complicates this?" Either modify the theme to accommodate counter-evidence or report the contradiction explicitly. Do not finalize any theme without completing this check.

### Opportunity Areas
Cross-cutting patterns that represent design or product opportunities, drawn from multiple themes.

### Appendix insights
Findings mentioned by only 1 participant, edge cases, or contradictions that don't fit main themes but are worth preserving.

### Sample-size context
Carry forward the actual number of participants and the denominator relevant to each finding, including how many were asked or observed where known. State sampling, coverage and method limitations for every study. Counts from purposive qualitative samples do not estimate population prevalence.

---

## Output

Produce a structured analysis document containing:

1. **Participant Overview** — participant codes and only contextual attributes needed for interpretation, generalized to reduce re-identification risk. Do not include names or employers.
2. **Themes** — one block per theme, following the format in [references/synthesis-behavior.md](references/synthesis-behavior.md).
3. **Opportunity Areas** — cross-cutting patterns ready for a dedicated slide.
4. **Strategic Recommendations** — only where the evidence and requested scope support them. Trace each recommendation to source findings, distinguish design proposals from observations, and state unresolved assumptions.
5. **Appendix Insights** — weak-signal findings with supporting quotes.
6. **Gaps & Limitations** — unanswered research questions, thin signals, unresolved contradictions, underrepresented voices.

Maintain the restricted evidence ledger alongside the report and run the mechanical verifier. A researcher reviews the ledger and report before use in a deck. If requested, read the presentation instructions and pass the reviewed analysis forward.
