# Source manifest and evidence ledger

Use these JSON files inside the study folder. They contain pseudonymous but potentially identifying research data; store them under the same restricted controls as the sources. Do not include participant names, contact details, consent records or the identity key. Paths below are relative to the study folder, cannot escape it, and should identify approved source copies. The verifier supports UTF-8 text files for quote checks; transcribe other formats into reviewed UTF-8 source copies and register those copies, preserving the provenance in the restricted research records.

`python <path-to-harness>/scripts/uxrops.py init <study-folder>` creates empty versions of both files.

## Line endings and hashes

Hashes are computed from the exact bytes on disk. If a study folder is kept in a git repository, line-ending conversion on checkout changes those bytes and every hash reports drift. `uxrops init` writes a `.gitattributes` containing `* -text` into the study folder to prevent this; keep it, or add an equivalent rule, before committing study files.

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

Each source ID and path is unique. Multiple sources may refer to one participant or session. A participant can have no source, for example if they withdrew; the verifier warns about such participants, and they must not be counted as analyzed. Confirm the participant mapping manually. Record hashes from the exact files used for analysis, for example `python <path-to-harness>/scripts/uxrops.py hash <source-file>...`. Hashes detect changes, not authorization, authenticity or meaning.

## evidence-ledger.json

```json
{
  "source_snapshot": {"S1": "analysis-time hash of S1", "S2": "analysis-time hash of S2"},
  "research_questions": [
    {"id": "RQ1", "question": "How do organizers confirm and share a booking?"}
  ],
  "themes": [
    {
      "id": "T1",
      "claim": "A source-grounded observation or clearly labeled interpretation.",
      "research_questions": ["RQ1"],
      "supporting_participants": ["P1"],
      "counter_evidence": "What was examined and what contradicted or complicated the claim; distinguish not discussed.",
      "evidence": [
        {"source_id": "S1", "source_sha256": "same hash captured when analyzed",
         "locator": "line 12", "polarity": "support",
         "quote": "Exact excerpt from the source.",
         "display_quote": "Optional edited version … with [clarifying inserts]."}
      ]
    }
  ],
  "recommendations": [
    {"id": "R1", "theme_ids": ["T1"], "proposal": "A design proposal, not a source fact."}
  ]
}
```

Capture every source ID and its hash in `source_snapshot` when analysis begins, including sources not quoted by a theme. A later addition, removal or change invalidates the snapshot. Reconcile and review changes rather than merely updating the hashes.

Each theme needs at least one supporting excerpt and a nonempty account of the counter-evidence search. Use `support`, `contradict`, or `context` for polarity. List each supporting participant exactly once in `supporting_participants`. Include counter-excerpts when found, and preserve surrounding context and any necessary qualifications in the analysis. The exact excerpts are restricted evidence, not automatically suitable for sharing. Record denominators, people not asked, observations and interpretations in the analysis.

`research_questions` and `recommendations` are optional. When research questions are listed, link each theme to the questions it answers. A theme with no link is reported so it can be labeled as an unexpected finding, and a question no theme answers is reported as a gap. Each recommendation names the theme IDs it rests on and remains a proposal rather than a source fact.

### Quotes

- `quote` is copied from the source without changes. A long excerpt may drop words only where an ellipsis (`...` or `…`) marks the cut.
- `display_quote` is optional. It is the version shown in reports when filler is trimmed or a clarifying `[insert]` is added. Mark every cut with an ellipsis, including removed filler such as "um" or "you know". Every remaining fragment must appear in the source in order, a short distance apart.
- Edited quotes that span several source lines are flagged, so a reviewer can confirm they come from one utterance.

### Locators

Use a separate source-specific locator that a researcher can check. The verifier checks these forms and reports a mismatch as a failure:

- `line 12`, `lines 12-14`, `L12`: 1-based line numbers.
- `paragraph 3`, `para 3-4`, `¶3`: blocks separated by blank lines, or lines when the source has no blank lines.
- `00:12:34`, `12:34`, `00:12:30-00:13:10`: the timestamp segment of the source that contains the excerpt.

Other locator text is accepted with a warning that it is not machine-checkable.

## Run the checks

```text
python <path-to-harness>/scripts/uxrops.py verify <study-folder>
python <path-to-harness>/scripts/uxrops.py check-report --study <study-folder> <analysis.md> <report.docx> <deck.pptx>
```

`verify` fails on:

- invalid JSON or structure, and missing required fields
- duplicate IDs or paths, and missing or outside-root source files
- changes to the source snapshot
- unrecognized source, theme or research question references
- incorrect supporting participant sets
- excerpts not found in their UTF-8 sources
- locators that point somewhere else

A missing excerpt's message names the closest source line, or says when the quote matches only after normalizing quote marks and whitespace (use `--normalize` to accept that). Warnings flag weak signals, unchecked locators, unlinked themes and unanswered research questions; `--strict` makes them fail. `--format json` prints `{"ok", "errors", "warnings"}` for automation.

`check-report` runs the same checks, then reads each document. Every quotation of four or more words (in straight or curly double quotes) must be found in a registered source. A source ID or participant code written just after the quotation must match where it was found. Theme and research question IDs must exist in the ledger. It also warns when:

- a quotation is not recorded in the ledger
- a ledger theme is absent from a document
- an "N of M" count near a theme does not match its supporting participants
- the study style in `uxr-project.json` asks to avoid mid-sentence dashes and authored prose contains them

Exit codes are 0 for mechanically valid inputs, 1 for validation failures, and 2 for command usage errors.

These checks do not validate permissions, consent, identity mapping, source completeness, contextual fidelity, analytical reasoning, or whether all important findings have been included. They also do not check quotations shown without quotation marks. A successful run is not research approval. Review each finding and the generated report or deck against the actual sources.
