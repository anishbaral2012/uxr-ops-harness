---
name: uxr-ops
description: Coordinate a UX research study in a project folder, from planning and fieldwork through evidence review and reporting.
---

# UXR operations

Coordinate one study at a time. Respect the user's requested stage and existing authorization. If asked what comes next, inspect the study, explain the proposed inputs and stage, and wait for direction. A direct request to perform a stage is authorization to perform it; ask only for missing decisions or before replacing an existing deliverable. Never infer permission to share participant information or contact participants.

## Start and route

Identify the study folder and method. Inspect `uxr-project.md` and `study-manifest.json` if present, then reconcile their declared paths with the files. Ask when the folder, study, or intended inputs are ambiguous. Do not treat an arbitrary Word or PowerPoint file as a completed stage, or count files as participants. Preserve previous outputs and mark affected outputs stale when inputs or decisions change.

Read the local stage instructions below by paths relative to this file. This works even when a runtime cannot register nested skills; if the runtime supports registered skills, those may also be used. Follow the instructions in the selected file and the user's requested format.

| Work | Local instructions | Main inputs |
| --- | --- | --- |
| Research plan | [uxr-research-plan/SKILL.md](uxr-research-plan/SKILL.md) | Brief and existing evidence |
| Interview or moderated usability guide | [uxr-interview-questions/SKILL.md](uxr-interview-questions/SKILL.md) | Plan and decisions |
| Qualitative analysis | [uxr-qual-analysis/SKILL.md](uxr-qual-analysis/SKILL.md) | Plan, manifest, consented source material |
| Findings deck | [uxr-research-presentation/SKILL.md](uxr-research-presentation/SKILL.md) | Reviewed analysis and plan |

Interview transcripts are not prerequisites for every method. For surveys, experiments, analytics, card sorts, tree tests, or diaries, agree on method-specific collection, analysis, and reporting artifacts with the researcher; do not force the interview pipeline or present a qualitative synthesis as quantitative inference. The plan skill helps scope such work; this package does not implement a full statistical analysis engine.

## Operational controls

Read [references/research-operations.md](references/research-operations.md) before planning recruitment or processing participant data. Record only verified handling commitments and the minimum necessary information. Keep identifying records and the code key separately in the organization's approved restricted location; do not place them in the study manifest or presentation. A local folder or these instructions do not themselves provide encryption, access control, retention enforcement, or deletion.

Use [references/study-schema.md](references/study-schema.md) to create a pseudonymous source manifest and analysis evidence ledger. Explicitly record participant IDs separately from sessions and files; a participant can have multiple sources. Maintain the evidence ledger as a restricted artifact because quotations and source locations can identify people. Ask the researcher to resolve duplicate identities and missing or uncertain sources rather than guessing.

Before completing analysis, run the bundled `scripts/verify_study.py` on the manifest and evidence ledger as described in the schema. It checks a limited set of mechanical invariants and reports failures; it does not certify consent, anonymization, interpretation, completeness, or visual quality. Resolve failures or explicitly report an unresolved blocker. A researcher must review evidence, negative cases, privacy, and interpretations. Verify generated documents and decks by opening or rendering them, checking content, layout and accessibility. Verify source fidelity again in the deck; do not infer deck correctness solely from the generation script.

## State and handoff

Maintain a small `uxr-project.md` listing the study name, method, decisions, confirmed paths for each artifact, status (`planned`, `in progress`, `review needed`, `reviewed`, or `stale`), source snapshot date, and unresolved questions. Record each deliverable's upstream artifact paths and content hashes, including the plan, guide, manifest, ledger and analysis as applicable, and compare them before reuse. Do not store direct identifiers or consent forms in this status file. Actual files alone do not establish review or completion. When saving, write to a temporary file and replace the status file after the write succeeds. On upstream changes, mark affected artifacts stale, retain them, and explain the impact before reuse. Capture research-source hashes in the evidence ledger; compare the complete source snapshot at verification time, not only counts. Document which downstream artifacts were reviewed after a change. The verifier checks research sources, not these other artifact dependencies, which require a separate comparison.

Before delivering, report what was created, what was verified, limitations of those checks, and any unresolved privacy or research decisions. Never describe a draft or a mechanically valid ledger as independently verified research.
