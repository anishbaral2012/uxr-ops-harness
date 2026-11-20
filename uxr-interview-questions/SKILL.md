---
name: uxr-interview-questions
description: >
  Internal engine invoked by the uxr-ops master skill to generate or critique a
  UX research interview guide (screeners, warm-ups, core questions, task probes,
  closing) for any UXR method (generative, evaluative, concept testing, JTBD,
  diary). Works independently or as part of uxr-ops. Delivers an MS Word `.docx` by default.
---

# UXR Interview Question Generator

Generates research-grade interview guides — or critiques a user's existing draft — and delivers the result as an MS Word `.docx` file.

The bulky pieces live in `references/`:
- `references/worked-example-pm-tools.md` — full reference example to model your output on.
- `references/md-to-docx.py` — the `.docx` converter you'll invoke.

---

## When to Use

**Use when the user:**
- Mentions UXR, user research, discussion/interview guide, screener, research plan, hypotheses.
- Pastes a research brief, study objectives, or recruiting criteria.
- Asks to *review*, *critique*, or *improve* their own draft questions → Review Mode.
- Describes any of: generative/discovery, evaluative/usability, concept testing, JTBD, diary.

**Don't use for:** survey design (Likert / large-N quant), analytics specs, generic Q&A unrelated to a research objective.

---

## Process

1. **Extract inputs.** Read any pasted plan and pull the 7 inputs in *Inputs Required*. List which are missing.
2. **Handle missing inputs.**
   - **3 or more missing** → ask the user once, in a single batched question. No drip-questioning.
   - **1–2 missing** → state reasonable non-critical assumptions inline and proceed. Never assume consent or data-handling commitments.
   - **0 missing** → proceed.
3. **Choose mode.** Generate Mode (default) or Review Mode (when the user pastes their own questions for critique).
4. **Draft.** Use the *Question Budget* table. Map every hypothesis to ≥1 question.
5. **Run the Quality Checklist.**
6. **Deliver.** Render the full guide as markdown inline so the user can read and edit it, then produce the `.docx` (see *Deliverable*). Skip the `.docx` only if the user explicitly asks for "markdown only."

---

## Inputs Required

1. **Research objective** — what decisions will this inform?
2. **Research method** — generative, evaluative, concept testing, JTBD, diary.
3. **Target participants** — role, experience, behaviors, demographics.
4. **Key topic areas** — themes/domains to cover.
5. **Hypotheses or assumptions** — if supplied, trace each to a question that can challenge it. Exploratory studies need not manufacture hypotheses; map research questions to guide questions instead.
6. **Session length** — default 60 min if unstated.
7. **Moderator style** — semi-structured by default.

---

## Deliverable

**Default: MS Word `.docx`.**

1. Render the full guide as markdown inline first — so the user can read, copy quotes, or ask for edits before the file is generated.
2. Write the markdown to a temp file, then convert with the bundled script:

   ```bash
   python3 <path-to-this-skill>/references/md-to-docx.py \
       <input.md> <output.docx>
   ```

3. **Save location:** if uxr-ops passed an absolute save path, it overrides the current working directory and you write the `.docx` there. With no save path passed (standalone use), save to the user's current working directory (the directory shown in the Claude Code session). After writing, surface the **absolute path** so the user can find the file. If no path was passed and the CWD is the user's home (`~`) or otherwise unclear, ask where they'd like it saved before writing.
4. **Filename pattern:** `interview-guide-<short-topic>-<YYYYMMDD>.docx`
   (e.g., `interview-guide-pm-tools-20260604.docx`).
5. **Fallback:** if `python-docx` isn't available (`python3 -c "import docx"` fails), try `pandoc -f markdown -t docx -o <out>.docx <in>.md`. If neither works, surface the error and ask the user how to deliver.
6. **Skip `.docx`** only when the user explicitly says "markdown only," "paste inline," or similar.

The bundled script handles: headings, blockquotes, bullets (with one level of indent), numbered lists, pipe tables, `[ ]`/`[x]` checkboxes (rendered as ☐/☑), inline `**bold**` / `*italic*` / `` `code` `` / `[text](url)`, and `---` horizontal rules.

---

## Question Budget

Size the guide to the session length. These numbers are calibrated for *real* 1:1 sessions where each question gets 2 follow-up probes — not for question-pile interviews that never finish.

| Session length | Themes | Core questions | Probes per question |
|----------------|--------|----------------|---------------------|
| 30 min         | 1–2    | 5–7            | 2                   |
| 60 min         | 3      | 9–12           | 2                   |
| 90 min         | 4–5    | 13–18          | 2–3                 |

Treat the budget as a starting point. Use only useful probes and adapt during the session; task observation and follow-up need adequate time.

---

## Output Structure (Generate Mode)

Always produce these sections, in order. See `references/worked-example-pm-tools.md` for a full reference instance.

1. **Study Overview** — objective, method, participant profile, session length, hypotheses being tested, moderator notes.
2. **Screener Questions** (5–8) — closed-ended; mark each option *Qualify / Disqualify / Borderline*.
3. **Intro & Consent** `[~3 min]` — read-aloud consent script (see *Ethics & Consent*).
4. **Warm-Up** (3–5) `[~5 min]` — open-ended, low-stakes, about background or daily context. Never about the product.
5. **Core Questions** — sized to the session; grouped under labeled themes; broad → specific → probing.
6. **Concept / Task Section** (only for evaluative or concept-testing) — see *Concept Testing variants*.
7. **Closing** (4–6) `[~5 min]` — reflection prompt, anything-we-missed, snowball recruiting (*"Anyone else we should talk to?"*), comfort/feedback probe (*"On a 1–10, how did this feel?"*), thank-you and next steps.
8. **Research-to-Question Mapping** — table at the end, covering each objective or supplied hypothesis:

   | Hypothesis | Question IDs that test it |
   |------------|---------------------------|
   | H1: ...    | Q3, Q5                    |
   | H2: ...    | Q7, Q12                   |

   Every hypothesis must appear with at least one question ID. Enforced by the Quality Checklist.

**Time math must sum to the session length** — include intro + transitions (~10 min total for a 60-min session). Show the totals at the end of the guide.

---

## Question Writing Principles

### Always Do
- **Open-ended by default**: "Tell me about…", "Walk me through…", "Describe…", "How do you…"
- **Past behavior over hypothetical**: "Tell me about the last time you…" beats "Would you…?"
- **One idea per question**: never combine two with "and."
- **Neutral framing**: "What's your experience with…?" not "Do you find it frustrating when…?"
- **Layered probes**: provide relevant optional follow-ups and adapt them to the participant's answers.
- **Concrete and specific**: anchor in real scenarios, not abstract preferences.
- **Plain language**: 8th-grade reading level; expand any acronym on first use.

### Never Do
- Leading questions ("Don't you think it would be better if…?")
- Double-barreled questions ("How often do you use it *and* what do you like about it?")
- Yes/no questions in the core section (save for screener).
- Future-behavior asks ("Would you use this?" — reframe to past behavior).
- Jargon or internal product terminology.
- Compound time references ("How often, in the past, did you usually…").
- "Always / never" framing — use frequency questions instead ("How often do you…").

### Question Type Reference

| Type | When to Use | Example Starter |
|------|------------|-----------------|
| **Context-setting** | Opening a new topic | "Walk me through a typical week when it comes to…" |
| **Narrative / story** | Understand full journey | "Tell me about the last time you…" |
| **Comparison** | Surface priorities and tradeoffs | "How does X compare to how you used to…?" |
| **Emotional probe** | Understand affect and motivation | "How did that make you feel?" / "What was going through your mind?" |
| **Clarifying** | Dig into vague answers | "Can you say more about that?" / "What do you mean by…?" |
| **Hypothetical (sparingly)** | Only after establishing real behavior | "If you could change one thing about that…" |
| **Prioritization probe** | Surface implicit priorities qualitatively | "Of everything you mentioned, what matters most — and why?" |

> *A "prioritization probe" is qualitative. True max-diff / forced-ranking is a quantitative technique and out of scope.*

---

## Accessibility & Inclusion

- 8th-grade reading level; avoid idioms that don't translate.
- Don't assume gender, family structure, employment status, tech literacy.
- Open with: *"Is there anything that would make this conversation easier or more comfortable for you?"*
- For video: *"Camera on or off — whatever's comfortable."*
- Offer a break in sessions over 45 minutes.
- Mirror the participant's language and pronouns.

---

## Ethics & Consent

Use the organization's approved consent material and verified study-specific practices. Consult [research operations](../references/research-operations.md). Never promise a retention period, deletion right, internal transcription, anonymity, or restricted access unless confirmed and operationally supported. Explain the study, voluntary participation, uses and sharing, recording, transcription and any AI processing; offer a non-recording alternative where possible. Obtain and document explicit recording permission separately. If essential details are unknown, mark them for confirmation before use instead of producing a ready-to-read promise. A participant may skip a question or stop; describe withdrawal and deletion terms only as confirmed by the responsible team.

**For sensitive domains** (finance, health, workplace conflict, immigration, family):
- Add explicit data-handling disclosure (where data is stored, who else may see it, whether AI tools touch it).
- Frame questions in terms of *experiences and decisions*, not identity.
- Ask permission before probing: *"Would it be okay to ask a bit more about that?"*
- Never push when the participant deflects.
- End sensitive sections with a neutral question to ease back to baseline.
- Consider legal review of the consent language.

**Right-to-skip language to surface during the session:** *"If any question feels too personal or you'd rather not answer, just say 'pass' — no explanation needed."*

---

## Bias Awareness

- **Confirmation bias** — drafting questions that only test the "happy path" of a hypothesis. *Mitigation:* include at least one question per hypothesis that could disprove it.
- **Social desirability bias** — participants saying what sounds good. *Mitigation:* anchor in specific past events, not generalities.
- **Recency bias** — over-weighting last week's experience. *Mitigation:* ask for two examples — "the last time" and "a memorable time."
- **Acquiescence bias** — agreeing with the moderator. *Mitigation:* avoid "Does that make sense?" and tag-questions like "Right?"

---

## Moderator Do/Don't-Say Cheat Sheet

| ❌ Don't say | ✅ Do say |
|-------------|----------|
| "Does that make sense?" | "Tell me what you're thinking." |
| "Would you use this?" | "Tell me about the last time you needed something like this." |
| "Why?" (alone — can feel interrogative) | "What was behind that?" / "Say more about that." |
| "Most people say…" | (omit — leading) |
| "Right?" / "Yeah?" at sentence ends | (omit — invites acquiescence) |
| "We designed it so that…" | "What do you think this is for?" |
| "Is this clear?" | "How would you explain this to a colleague?" |

---

## Formatting Rules (for the markdown the script will convert)

- Markdown headers (`##`, `###`) for each section.
- **Bold** every main question.
- `>` blockquotes for moderator notes and read-aloud scripts.
- Indented bullets for follow-up probes.
- Section time estimates in backticks: `` `[~10 min]` ``.
- Times must sum to the requested session length (count intro + transitions, ~10 min for 60 min total).
- Hypothesis-mapping table is a real markdown table (the script renders it as a Word table).

---

## Adapting by Research Method

### Generative / Discovery
Focus: behaviors, mental models, pain points, workarounds, context of use.
Avoid: showing any solution until the very end (or not at all).
Framing: *"Help me understand their world before showing them ours."*

### Evaluative / Usability
Focus: task completion, first impressions, comprehension, friction.
Structure: intro → tasks → post-task reflection → debrief.
Include explicit think-aloud instructions and observation checkboxes.

### Concept Testing — variants
- **Standard**: prototype + tasks + think-aloud + observation checklist + post-task questions.
- **5-second test**: show stimulus for 5 s → "What do you remember?" / "What's it for?" / "Who's it for?"
- **First-click test**: present a screenshot → "Where would you click first to do X?" → record click + reasoning.

Don't ask "do you like it?" — ask "what questions does this raise for you?"

### Jobs-to-be-Done — Switch Interview
Use the **4 Forces** framing (Bob Moesta). One question per force, minimum:

- **Push of the current situation** — "Take me back to when you first realized your old way wasn't working. What was happening?"
- **Pull of the new solution** — "When you started looking for something new, what were you imagining it would do for you?"
- **Habit of the present** — "What were you used to that you didn't want to give up?"
- **Anxiety of the new** — "What worried you about switching? What almost stopped you?"

Build the timeline backwards from the moment of switch: *first thought → passive looking → active looking → decision → first use → outcome.*

### Diary / Longitudinal
Generate a **prompt set**, not a single guide. Default cadence: **1 daily prompt for 2 weeks + 1 weekly reflection.**

Daily prompts (rotate or repeat; under 60 seconds to answer):
1. "What stood out about your experience with [topic] today? Share only what you are comfortable sharing."
2. "Did you do anything today that you wish were faster or simpler? Walk me through it."
3. "What's one thing that worked well today? What made it work?"

Weekly reflection (under 5 minutes):
- "Looking back at the week, what stood out — good or bad? Did anything change in how you approached [topic] compared to last week?"

---

## Review Mode

Triggered when the user pastes their own questions and asks for review/critique.

Steps:
1. Score each question against the *Always Do* / *Never Do* lists.
2. Flag: leading, double-barreled, hypothetical-without-prior-behavior, jargon-heavy, yes/no in core, compound time references, "always/never" framing.
3. Suggest a rewrite for every flagged question.
4. Note structural gaps: missing screener / warm-up / probes / hypothesis coverage / time totals don't sum.
5. Output as a critique table, then optionally as `.docx` per the default deliverable rule.

**Critique table format:**

| # | Original question | Issue(s) | Suggested rewrite |
|---|-------------------|----------|-------------------|
| 1 | "Don't you think the dashboard is confusing?" | Leading; yes/no | "Walk me through your first impression of the dashboard." |
| 2 | "How often do you use it and what do you like?" | Double-barreled | Split into two questions. |

End with a structural summary: *"Missing warm-up section. 2 of 3 hypotheses untested. Time estimates sum to 45 min but session is 60 min."*

---

## Quality Checklist (run before delivering)

- [ ] All 7 inputs captured, or assumptions explicitly stated.
- [ ] Every research objective or supplied hypothesis maps to a relevant question.
- [ ] Every core question is open-ended (no yes/no in core).
- [ ] No leading, double-barreled, compound-time, or "always/never" questions.
- [ ] Probes are useful and the session has time for observation and follow-up.
- [ ] The guide fits the session length, including tasks and adaptive follow-up.
- [ ] Each theme matches a stated research objective.
- [ ] Concept/task section present if evaluative or concept-testing.
- [ ] Screener has explicit Qualify / Disqualify / Borderline flags.
- [ ] Approved recording-consent language and right-to-skip language included, or unresolved details clearly marked before fieldwork.
- [ ] Time estimates sum to the requested session length (incl. intro + transitions).
- [ ] `.docx` file produced (or user explicitly opted out) and absolute path surfaced to the user.
- [ ] Moderator notes included for sensitive or tricky topics.
- [ ] No mid-sentence hyphen or dash in the authored prose (user writing rule). Rephrase with a comma, colon, parentheses, or two sentences. Em-dash attributions inside verbatim quotes are fine.

---

## Worked Example

A complete 60-min generative discovery guide for engineering leads / project tracking is in `references/worked-example-pm-tools.md`. It's the canonical reference instance — model your output on it for shape and depth, but always tailor the content.

---

## Further Reading

- **Erika Hall** — *Just Enough Research* (research strategy, scoping).
- **Steve Portigal** — *Interviewing Users* (interview craft, fieldwork).
- **Indi Young** — *Practical Empathy* / *Time to Listen* (deep listening sessions).
- **Bob Moesta** — *Demand-Side Sales* / JTBD switch-interview methodology (4 forces).
