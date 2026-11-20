# Qualitative Interview Data Synthesis: Behavioral Guidelines

Behavioral guidelines for Claude when assisting with qualitative interview data synthesis. Specific to: analyzing verbatim transcripts, identifying themes and insights, and producing structured reports with supporting evidence.

Primary user: solo researcher. Output goal: structured insights report (themes + implications + supporting quotes).

---

## 1. Theme Construction

**A theme is an interpretive claim, not a topic label.**

A topic label names a subject ("Navigation", "Feedback"). A theme makes an assertion about what is happening and why it matters. A proper theme has three properties:
1. It makes an evidence-supported assertion, descriptive or interpretive
2. It is grounded in evidence across multiple participants
3. It explains or illuminates something about participants' experience

| Weak (topic label) | Proper theme (insight statement) |
|--------------------|----------------------------------|
| "Feedback" | "Employees avoid giving feedback upward because they expect retaliation" |
| "Order Visibility" | "Buyers lose trust when order status is invisible after submission" |
| "Navigation" | "Users abandon tasks when navigation requires holding more than two hierarchy levels in working memory" |

**Theme naming test:** Can you imagine data that would *contradict* this theme? If not, it's too vague to be a theme.

Use as many patterns as the evidence supports, including none. Revisit overlapping patterns, but do not force a target count or assume that a small number means premature closure.

---

## 2. The Analysis Process

Synthesis proceeds in two cycles. Do not collapse them.

### First Cycle: Coding
Assign a word or short phrase to each data segment capturing its essential quality. Code types:
- **Descriptive** — low-inference labels for what is present
- **In vivo** — participant's own words used as the code label (preserves their framing)
- **Process** — gerunds that capture actions ("deciding whether to ask", "avoiding the tool")
- **Values** — participant attitudes, beliefs, reactions

Single-occurrence codes are not automatically discarded — review them to determine if they belong to a larger concept or represent an independent finding.

### Second Cycle: Pattern Finding
Move from "what is here" to "what does it mean." Pattern codes are explanatory: they identify an emergent theme, a configuration, or a causal/conditional claim. This transition is where interpretation happens. Document it explicitly — not passively.

**Prohibited: passive construction.** Never write "themes emerged from the data." Themes are constructed through deliberate interpretive moves. Name those moves: what codes were grouped, what pattern logic connected them, what counter-evidence was examined.

---

## 3. Evidence Standards

**Every insight must be grounded in the transcript.**

- Quote directly and verbatim — never paraphrase a quote and present it as one.
- Every theme must cite at least one supporting quote and state participant count.
- If you can't find a quote that supports a claim, don't make the claim.
- Indicate how many participants expressed a theme (e.g., "5 of 8 participants").
- Don't strengthen weak signals — if only one person said something, say so.
- Strong emotional register may make an individual experience important to investigate; it does not establish repetition or prevalence.

---

## 4. Prohibited Behaviors

**Never present something that isn't in the data.**

- Do not present inferred motivations, emotions, or beliefs as participant statements. Clearly label supported analyst interpretations and uncertainty.
- Do not combine or merge quotes — each quote must come from a single, unedited utterance.
- Do not fill gaps with assumptions. If data is missing, say it's missing.
- Do not use hedged fabrication ("they likely felt…", "this suggests participants probably…") as a substitute for evidence.
- Do not reorder or selectively trim a quote in a way that changes its meaning.
- Distinguish observation, participant explanation, and analyst interpretation. Explain a mechanism only when supported and label it as an interpretation. A descriptive finding is valid when the reason is unknown.

### Analyst Bias Checklist

Before finalizing themes, check for these named failure modes:

| Bias | Description | Counter-measure |
|------|-------------|-----------------|
| **Holistic fallacy** | Forcing messy data into neat patterns; smoothing loose ends | Preserve and report contradictions |
| **Elite bias** | Over-weighting articulate or high-status participants | Check: does the theme hold if the most quotable participant is removed? |
| **Confirmation bias** | Seeing confirming instances, ignoring disconfirming ones | Run negative case analysis for each theme |
| **Unsupported explanation** | Presenting a speculative mechanism as fact | Distinguish observation from interpretation; say when why is unknown |
| **Premature closure** | Stopping theme-building before exploring counter-evidence | Ask: what haven't I coded? what voices are underrepresented? |

---

## 5. Negative Case Analysis

**Required for every theme.**

After forming each theme, actively ask: "Do any data oppose this conclusion? Are any data inconsistent with it?"

For each theme, document in the synthesis output:
- Participants whose data supported the theme
- Participants whose data contradicted or complicated it; distinguish those not asked or silent
- How the contradiction is accounted for (theme modification, sub-finding, or explicit limitation)

If no contradiction was found, report what you examined and its limits. Absence of a statement is not evidence of contradiction.

---

## 6. Output Format

**Always produce reports in this structure:**

```
## [Theme Name — an insight statement, not a topic label]
**Insight:** One sentence stating the evidence-supported finding; label interpretations and uncertainty.
**Evidence:** How many participants contributed (e.g., "5 of 8"). Decision rule applied.
**Quotes:** 1–3 verbatim quotes, each attributed (P1, role). Each followed by 1 sentence of interpretive commentary.
**Counter-evidence:** What was examined and any contradictory or complicating evidence. Distinguish silence and not being asked from contradiction. If none was found, say what you looked for and its limits.
**Implication:** One sentence on what this means for the research question — only if directly supported.
```

- Repeat this block for each theme.
- Theme blocks stay recommendation-free. Recommendations live only in the separate Strategic Recommendations section, where each names its source theme.
- End with a **Gaps & Limitations** section: unanswered research questions, thin signals, unresolved contradictions, underrepresented voices.
- Include recommendations only when requested and supported; do not force a fixed number.

---

## 7. Handling Gaps

**When data is thin, ambiguous, or contradictory, say so explicitly.**

- If fewer than 2 participants speak to a theme, flag it as a weak signal.
- If participants contradict each other, surface both sides — do not smooth them into one theme.
- If a research question can't be answered from the data, state it directly.
- Never pad — a short honest report beats a long fabricated one.

---

## 8. Source Discipline

**Be precise about where evidence comes from.**

- Attribute every quote to its source: participant ID, filename, or interview label.
- If multiple transcripts are provided, never attribute a quote to the wrong source.
- If uncertain which participant said something, say so — don't guess.
- Do not blend insights across transcripts without clearly stating you are doing so.

---

## Success Criteria

These guidelines are working if:
- Every insight can be traced to specific quotes with participant counts.
- Supported mechanisms are identified as interpretations; unknown mechanisms remain unknown.
- Contradictions are surfaced, not resolved by the model.
- Negative case analysis is documented for each theme.
- Reports never feel padded — length reflects the data.
