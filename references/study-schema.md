# Source manifest and evidence ledger

Use these JSON files inside the study folder. They contain pseudonymous but potentially identifying research data; store them under the same restricted controls as the sources. Do not include participant names, contact details, consent records or the identity key. Paths below are relative to the study folder, cannot escape it, and should identify approved source copies. The verifier supports UTF-8 text files for exact quote checks; transcribe other formats into reviewed UTF-8 source copies and register those copies, preserving the provenance in the restricted research records.

## study-manifest.json

```json
{
  "participants": ["P1", "P2"],
  "sources": [
    {"id": "S1", "participant_id": "P1", "session_id": "session-01",
     "path": "transcripts/p1.txt", "sha256": "64 lowercase hex characters"},
    {"id": "S2", "participant_id": "P1", "session_id": "session-02",
     "path": "notes/p1-follow-up.txt", "sha256": "64 lowercase hex characters"}
  ]
}
```

Each source ID and path is unique. Multiple sources may refer to one participant or session. A participant can have no source, for example if they withdrew; do not include them in analyzed-participant counts. Confirm the participant mapping manually. Record hashes from the exact files used for analysis, for example `python <path-to-skill>/scripts/verify_study.py hash <source-file>`. Hashes detect changes, not authorization, authenticity or meaning.

## evidence-ledger.json

```json
{
  "source_snapshot": {"S1": "analysis-time hash of S1", "S2": "analysis-time hash of S2"},
  "themes": [
    {
      "id": "T1",
      "claim": "A source-grounded observation or clearly labeled interpretation.",
      "supporting_participants": ["P1"],
      "counter_evidence": "What was examined and what contradicted or complicated the claim; distinguish not discussed.",
      "evidence": [
        {"source_id": "S1", "source_sha256": "same hash captured when analyzed",
         "locator": "paragraph 12", "polarity": "support",
         "quote": "Exact excerpt from the source."}
      ]
    }
  ]
}
```

Capture every source ID and its hash in `source_snapshot` when analysis begins, including sources not quoted by a theme. A later addition, removal or change invalidates the snapshot. Reconcile and review changes rather than merely updating the hashes. Each theme needs at least one supporting excerpt and a nonempty account of the counter-evidence search. Use `support`, `contradict`, or `context` for polarity; list each supporting participant exactly once in `supporting_participants`. Include counter-excerpts when found, and preserve surrounding context and any necessary qualifications in the analysis. The exact excerpts are restricted evidence, not automatically suitable for sharing. Use a separate source-specific locator (paragraph, line or timestamp) that a researcher can check. Record denominators, people not asked, observations and interpretations in the analysis. Recommendations link to finding IDs and remain proposals rather than source facts.

Run:

```text
python <path-to-skill>/scripts/verify_study.py verify <study-folder>/study-manifest.json <study-folder>/evidence-ledger.json
```

The verifier fails on invalid JSON or structure, duplicate IDs or paths, missing or outside-root source files, changes to the source snapshot, unrecognized source references, incorrect supporting participant sets, missing required fields and exact excerpts not found in their UTF-8 sources. The exit code is 0 on mechanically valid inputs, 1 on validation failures and 2 for command usage errors. It does not validate locator accuracy, permissions, consent, identity mapping, source completeness, contextual fidelity, analytical reasoning, or whether all important findings have been included. A successful run is not research approval. Review each finding and the generated report or deck against the actual sources.
