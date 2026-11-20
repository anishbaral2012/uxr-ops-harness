---
name: uxr-research-plan
description: Produce a decision-focused UX research plan from a brief or research artifacts, including method, participants, and limitations.
---

# UXR Research Plan from Documents

## Overview

Transforms product artifacts (PRDs, design docs, personas, OKRs, competitor analysis) into a structured UX Research plan. Always follows the canonical template structure below. Annotates each field as **[Required]** or **[Optimal]** so researchers know what to complete under tight timelines.

---

## Step 0 — Check What You Have Before Starting

Ground the plan in supplied artifacts, distinguish facts from assumptions, and do not invent missing context. Ask for missing critical inputs. Use this skill directly for a standalone request or read it as a local reference when routed by uxr-ops.

Before doing anything else, assess whether the minimum inputs are present.

**Minimum required to write a meaningful plan:**
- A product or feature description (what is being built or changed)
- A target user or audience (who it's for)
- At least one decision or unknown the research must address

**If documents are shared**, extract the inputs in Step 1, then identify and ask about missing critical inputs before treating the plan as ready for execution.

**If no documents are shared** (user described the need in their message only), check whether the three minimum inputs above are present in their message. If any are missing, ask for them before proceeding:

> "Before I draft the research plan, I need a few details that weren't included:
> - [List each missing input specifically, e.g., 'Who is the target user for this feature?']
>
> If you have a PRD, design doc, or any brief you can share, that would also help me write a more grounded plan."

Do not generate a plan with placeholder TBDs for critical inputs like target user or product description — these will produce a plan that isn't actionable. It is better to ask once upfront than to deliver a plan the team can't use.

**If some inputs are present but others are missing**, call out the gaps explicitly at the top of the plan under a **"Missing Inputs"** heading, and note what the researcher will need to fill in before the plan is usable.

---

## Step 1 — Extract Signals from the Shared Documents

Before writing a single word of the plan, read the documents and note:

| Signal | Where to look | Used in plan section |
|--------|---------------|---------------------|
| Product/feature description | Intro, summary, feature list | Background |
| Target audience | Personas, "Who is this for", onboarding docs | Background → Target audience |
| Business goals / OKRs | Goals, metrics, KPIs, success criteria | Background → Business objectives |
| Open questions / TBDs | "We need to validate", debates, unresolved items | Research questions |
| Team assumptions | "Users will...", "We expect...", "We believe..." | Research objectives → Hypotheses |
| Previous research | Related studies, data, cited analytics | Background → Previous research |
| Timeline / milestones | Launch date, design delivery, decision gates | Background → Timeline and scope |
| New or changed flows | Wireframes, user flows, feature descriptions | Methodology selection |

**Internal checklist before writing:**
1. What does the product/feature do?
2. Who is the intended user?
3. What does the team assume users will do or feel?
4. What is explicitly uncertain or unresolved?
5. What decisions depend on user input before shipping?

### Working with Multiple Documents

Users often share several artifacts at once (a PRD, personas, analytics screenshots, competitor analysis). When multiple documents are provided:

1. **Extract signals from each document independently** using the table above before synthesizing.
2. **Cross-reference and layer signals** — different documents illuminate different parts of the plan. A persona doc enriches the Participants section; a PRD enriches Background and Research Questions; analytics data sharpens the Problem Statement.
3. **Flag contradictions explicitly.** If the PRD defines the target user differently than the persona doc, or if OKRs conflict with the stated timeline, call this out in the Background section as an open question. Do not silently pick one version — the contradiction itself is often a research-worthy finding.
4. **Weight documents by recency and specificity.** A recent design spec with concrete flows carries more weight than a stale strategy doc when defining tasks. But for business objectives, strategy docs are primary.

---

## Step 2 — Select Methodology

First determine whether the primary unknown calls for a **qualitative** or **quantitative** approach, then select the specific method.

### Qualitative Methods

Use qualitative methods when the goal is to understand *why* — motivations, mental models, pain points, and behaviors in context.

```
What is the primary unknown?
├── Can users understand or complete a task?
│   ├── Prototype / mockups available?                → Moderated usability test
│   └── No prototype yet?                             → Task-based concept test (walk through scenarios verbally)
├── Why do users behave a certain way?                → Semi-structured interviews / contextual inquiry
├── How do users behave over time / in real context?  → Diary study / field study
├── What don't we know we don't know?                 → Discovery interviews / Jobs-to-be-Done
├── How do users categorize or label things?           → Card sorting (open or closed)
├── Can users find things in the navigation?           → Tree testing
├── Which design direction resonates more?             → Preference test / concept test
└── Where do users look or click first?                → First-click testing (unmoderated)
```

| Method | Best for | Typical sample | Moderation |
|--------|----------|---------------|------------|
| Moderated usability test | Evaluating task flows with a prototype | 5–8 per segment | Moderated |
| Unmoderated usability test | Quick task-level validation at scale | 10–20 | Unmoderated |
| Semi-structured interviews | Exploring motivations, needs, pain points | 6–10 | Moderated |
| Contextual inquiry | Understanding behavior in natural environment | 4–8 | Moderated (in situ) |
| Discovery / JTBD interviews | Mapping unmet needs before a solution exists | 8–12 | Moderated |
| Diary study | Longitudinal behavior, habits, context shifts | 8–15 over 1–4 weeks | Self-reported |
| Card sorting | Information architecture, labeling, mental models | 15–30 (open), 30+ (closed) | Either |
| Tree testing | Findability within navigation structure | 30–50 | Unmoderated |
| Concept test | Early-stage reaction to ideas or directions | 5–8 | Moderated |
| First-click testing | Where users expect to start a task | 30–50 | Unmoderated |
| Preference test | Comparing 2–3 design alternatives | 20–50 | Unmoderated |

### Quantitative Methods

Use quantitative methods when the goal is to measure *how much*, *how many*, or *which* — prevalence, satisfaction, task success rates, and statistical comparisons.

```
What needs to be measured?
├── Attitudes, satisfaction, or preferences at scale?  → Survey (Likert, NPS, SUS, CSAT)
├── Which design variant performs better (live)?        → A/B test
├── Task completion rate or time on task?               → Unmoderated benchmark study
└── Behavioral patterns in existing product?            → Analytics / log analysis review
```

| Method | Best for | Typical sample | Key consideration |
|--------|----------|---------------|-------------------|
| Survey | Attitude measurement, segmentation, prioritization | 100–500+ | Screener quality determines data quality |
| A/B test | Comparing live variants on a real metric | Depends on effect size and traffic | Requires sufficient traffic and a clear success metric |
| Unmoderated benchmark study | Measuring task success, time, error rates | 20–50 per condition | Needs well-defined tasks and working prototype |
| Analytics / log analysis | Understanding current behavior patterns | Existing user base | No new recruitment — uses existing product data |

### Mapping Document Types to Methods

| Doc type shared | Method to consider, subject to the research question |
|----------------|---------------|
| PRD with new feature flows | Moderated usability test |
| Persona / target audience doc | Discovery interviews |
| Competitor analysis | Comparative usability or preference test |
| OKRs / strategy doc | Discovery interviews or survey |
| Design mockups / prototype | Moderated usability test |
| Existing product with friction | Contextual inquiry or diary study |
| Information architecture / site map | Card sorting or tree testing |
| Multiple design alternatives | Preference test or first-click testing |
| Live product with traffic | A/B test or analytics review |
| Post-launch validation | Survey (SUS, NPS, CSAT) |

---

## Common Mistakes — Self-Check Before Writing

Review this before drafting the plan. These are the most common ways a plan fails.

| Mistake | Fix |
|---------|-----|
| Objectives describe tasks, not intent ("We will conduct 5 interviews") | Objectives explain WHY and WHAT will be decided — not HOW |
| Research questions are too broad ("Do users like this?") | Tie each to a specific behavior, task, or decision |
| Recruiting too broadly | Tight screener = valid findings; wrong participants = wasted sessions |
| Writing tasks as instructions ("Click checkout") | Write as goals: "You want to buy this item — show me what you'd do" |
| Skipping the pilot | One pilot catches broken tasks and bad timing every time |
| Plan written before reading the docs | Re-run Step 1 extraction — the plan should be traceable to the document |
| Too many primary research questions | Limit to 3 primary; rest are secondary |

---

## Output Format

Deliver the research plan as a **Microsoft Word document (.docx)**. Do not output it as inline markdown in the chat. Use the template below to structure the document, preserving all headings, tables, and formatting. Save the file as `Research Plan - [Project Name].docx` and share it with the user.

---

## Step 3 — Write the Research Plan (Follow this template exactly)

---

# Research Plan: [Project Name]

| | |
|---|---|
| **Date** | [Date] |
| **Researcher** | [Name] |
| **Status** | Draft |

---

## Background

*[Required]* Summarize the product/feature context, goals, and what prompted this research. Pull directly from the shared document.

### Primary goals for this product or feature
*[Required]* What are the main product or business goals?

### Problem statement
*[Required]* What problem are we trying to solve, or what opportunity are we exploring?

### Target audience
*[Required]* Who is this product for? Reference personas or audience segments from the document.

### Business objectives and metrics
*[Optimal]* What metrics are we trying to move? What does success look like for the business? Create this section only if data is provided. Don't assume anything.

### Previous research and existing data
*[Optimal]* What has been studied before on this topic? What user data already exists, and what does it tell us? If none, state "No prior research identified." Create this section only if there is any data provided while creating the research plan.

---

## Research Objectives

*[Required] High-level, action-oriented statement explaining WHY this research is being conducted and HOW the findings will be used. Not a list of tasks — a statement of intent.*

Write 2–4 objectives using this structure:

"We want to [action] [user behavior or perception] in order to [decision or outcome]."

Examples:
- We want to evaluate whether new users can complete account setup without assistance in order to decide if the current flow is launch-ready
- We want to understand how customers interpret pricing options in order to improve conversion

Avoid vague objectives like "understand user behavior" without context.

Use these stakeholder questions to shape the objectives:

- What product or design decisions are you trying to make based on this research?
- What specific questions do we need to answer to make that decision?
- What do we want to learn about our users?
- What are the core hypotheses (about needs, pain points, and behaviors) that we need to validate or invalidate?

**[Optimal] Hypotheses to validate/invalidate:**
List the team's assumptions explicitly. Each becomes a research objective target.

---

## Research Questions

*[Required] Specific, unbiased inquiries that, when answered, will fulfill the research objectives. These are NOT interview questions — they are what the study needs to find out.*

Guidelines:
- Be specific: define the scope, audience, and context
- Focus on one core idea per question
- Avoid leading or yes/no questions

**Primary questions (must answer — tied to a go/no-go decision):**
1. [Question]
2. [Question]
3. [Question]

**Secondary questions [Optimal] (exploratory — enrich findings but don't block decisions):**
1. [Question]
2. [Question]

---

## Methodology

*[Required]* State the chosen method (from Step 2) and justify in 1–2 sentences referencing the specific gap in the documents.

- **Method:** [e.g., Moderated remote usability test]
- **Format:** [Remote / In-person] | [Moderated / Unmoderated]
- **Sample and unit of analysis:** [Participants, sessions, responses, events, or experimental units as appropriate; justify the target and its limits]
- **Rationale:** [Why this method fits the primary unknown identified in the docs]

Sample sizes in the method table are starting points, not guarantees of coverage or precision. Explain the rationale, segments and practical limits. For estimates or comparisons, specify the metric, desired precision or detectable effect, analysis plan and an appropriate sample-size calculation. Verbal concept walkthroughs explore understanding; they do not establish task completion.

---

## Participants

*[Required]*

| Attribute | Criteria |
|-----------|----------|
| User type | [From persona/target audience in doc] |
| Experience level | [Novice / Intermediate / Expert — with product or domain] |
| Device / platform | [If relevant to the feature being tested] |
| Key screener question | [One qualifying question — e.g., "Have you purchased X in the last 3 months?"] |

**Exclude:** Only groups whose exclusion is justified by the target population or study design. Employees and UX professionals may be appropriate participants when they are actual target users.

**Legal:** Share your organization's privacy statement or informed-consent document with all participants before the session. If recruiting external participants for studies involving unreleased designs, prototypes, or confidential features, obtain the required NDA or confidentiality agreement before scheduling. Consult your legal or research-ops team for the correct documents.

*[Optimal] Diversity considerations:* Note any demographic, accessibility, or locale requirements.

### Research operations and data handling

Identify the owner, decision date, recruitment channels and eligibility criteria, quotas or coverage goals, accessibility accommodations, compensation and scheduling process, and pilot. Record actual consent, recording, transcription, AI processing, access, storage, retention, withdrawal and deletion procedures before collection. Do not invent organizational policies. Use the consent and handling guidance in `../references/research-operations.md`.

---

## Timeline

*[Required]*

> **Note:** All durations below are tentative and subject to change based on participant availability and scheduling.

| Phase | Duration |
|-------|----------|
| Planning and instrument preparation | [Estimate for the selected method] |
| Recruitment or data access and collection | [Estimate for the selected method] |
| Analysis and reporting | [Estimate for the selected method] |
| Readout / decision | [Estimate for the decision date] |

---

## Deliverables

*[Required]*
- Research plan (this document)
- Discussion guide / Task script / Survey Questions
- Research report

*[Optimal]*
- Session recordings (with participant consent)
- Synthesis document (themes, quotes, key clips)

*Include the following only if explicitly scoped as a research objective — do not include by default:*
- Persona *(only if the objective is to build or update user personas)*
- Journey map *(only if the objective is to map the end-to-end user experience)*
- JTBD map *(only if the objective is to identify jobs-to-be-done)*

---

## Stakeholders

*[Required]*

| Designation | Name |
|-------------|------|
| Product Manager | [Name] |
| Designer | [Name] |
| Other | [Name] |

---

## Risks & Limitations

*[Required]* Identify what could go wrong or constrain the findings. Being upfront about risks builds credibility and helps stakeholders calibrate how much to rely on the results.

**Recruitment risks:**
- [e.g., Narrow screener criteria may slow recruitment — consider backup criteria if timeline is tight]
- [e.g., Target users are internal enterprise admins with limited availability — may need extended recruitment window]

**Timeline risks:**
- [e.g., Prototype delivery is a dependency — if delayed past [date], data collection shifts accordingly]
- [e.g., Compressed timeline means fewer sessions; findings may surface themes but not reach saturation]

**Method limitations:**
- [e.g., Remote moderated sessions cannot capture physical environment context that may influence behavior]
- [e.g., Self-reported diary entries may under-represent habitual or unconscious behaviors]
- [e.g., Sample size of N is sufficient for identifying usability issues but not for statistical generalization]

**Scope limitations:**
- [e.g., Study focuses on [segment] only — findings may not transfer to [other segment] without further research]
- [e.g., Prototype covers the happy path; error states and edge cases are out of scope for this round]

Remove any bullet that doesn't apply and add risks specific to this project. A plan with no risks listed is a plan that hasn't been thought through.

---

## Final Validation Checklist

Before delivering the research plan, verify:

- All [Required] sections are complete
- Objectives describe intent, not activities
- Research questions are specific and decision-linked
- Method matches the primary unknown
- Participants match the target audience from the documents
- Risks are realistic and specific (not generic placeholders)
- No mid-sentence hyphen or dash in the authored prose (user writing rule). Rephrase with a comma, colon, parentheses, or two sentences.

If any check fails, revise before finalizing.
