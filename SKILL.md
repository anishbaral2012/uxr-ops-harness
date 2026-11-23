---
name: uxr-ops
description: Coordinate a UX research study in a project folder, from planning and fieldwork through evidence review and reporting.
---

# UXR operations

Coordinate one study at a time. Respect the user's requested stage and existing authorization. If asked what comes next, inspect the study, explain the proposed inputs and stage, and wait for direction. A direct request to perform a stage is authorization to perform it; ask only for missing decisions or before replacing an existing deliverable. Never infer permission to share participant information or contact participants.

## Start and route

Identify the study folder and method. For a new study, run `python scripts/uxrops.py init <study-folder>` (paths relative to this file) to create the skeleton without overwriting anything. Inspect `uxr-project.json`, any `uxr-project.md` notes and `study-manifest.json` if present, run `python scripts/uxrops.py status <study-folder>`, then reconcile their declared paths with the files. Ask when the folder, study, or intended inputs are ambiguous. Do not treat an arbitrary Word or PowerPoint file as a completed stage, or count files as participants. Preserve previous outputs and mark affected outputs stale when inputs or decisions change.

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

Before completing analysis, run `python scripts/uxrops.py verify <study-folder>` as described in the schema. Before delivering a report or deck, run `python scripts/uxrops.py check-report --study <study-folder> <documents>` on the rendered files. These check a limited set of mechanical invariants and report failures and warnings; it does not certify consent, anonymization, interpretation, completeness, or visual quality. Resolve failures or explicitly report an unresolved blocker, and report the warnings you reviewed. A researcher must review evidence, negative cases, privacy, and interpretations. Verify generated documents and decks by opening or rendering them, checking content, layout and accessibility. Verify source fidelity again in the deck; do not infer deck correctness solely from the generation script.

## State and handoff

Keep the machine-readable record in `uxr-project.json`: study name, method, source snapshot date, `style` settings, decisions, open questions, and one entry per artifact with its `paths`, its upstream `inputs` and a declared `status` (`planned`, `in progress`, `review needed`, `reviewed`, or `stale`). Keep a short `uxr-project.md` only for human notes if the researcher wants one. Do not store direct identifiers or consent forms in either file. Actual files alone do not establish review or completion.

After the researcher reviews an artifact, run `python scripts/uxrops.py record <artifact> --project <study-folder> --status reviewed`. This stores the hashes of its files and inputs and replaces the file atomically. It refuses while an input is not ok. Before reusing any artifact, run `status`. It marks an artifact `modified` when its own files changed and `stale` when an input changed or is itself not ok, following the whole chain. Use `status --mark-stale` to record that, retain the stale artifacts, and explain the impact before reuse. Do not re-record an artifact merely to clear a warning; record it only after review. Capture research-source hashes in the evidence ledger and compare the complete source snapshot at verification time, not only counts.

Apply the study's `style` settings to authored prose. For example, `"avoid_mid_sentence_dashes": true` means rephrasing with a comma, colon, parentheses or two sentences; `check-report` warns about dashes outside quotations when it is set.

Before delivering, report what was created, what was verified, limitations of those checks, and any unresolved privacy or research decisions. Never describe a draft or a mechanically valid ledger as independently verified research.
