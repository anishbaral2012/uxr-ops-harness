# Library room booking sample run

Source snapshot recorded 20 November 2026. This study exercises the UXR Ops harness using a fictional public library scenario. All participant accounts and quotations are synthetic. This is a technical review of the sample outputs.

**Method.** Moderated discovery interviews about a recent study room booking attempt. Six fictional organizers are represented in seven sources. The seventh source is a follow up with P6.

**Decision.** The fictional product lead needs to choose how the prototype handles a time or branch constraint, shows room details and lets organizers share booking information. The three proposals in the readout demonstrate traceability within the scenario.

## Files and status

“Reviewed” means checked for this sample run. The research plan remains a draft for the fictional study.

| Stage | Files | Status | Inputs |
|---|---|---|---|
| Study brief | [brief.md](brief.md) | Reviewed | None. This is the fictional scenario. |
| Research plan | [plan.md](plan.md), [Research Plan - Library Room Booking.docx](Research%20Plan%20-%20Library%20Room%20Booking.docx) | Reviewed | `brief.md` for the plan. `plan.md` for the Word copy. |
| Interview guide | [guide.md](guide.md), [interview-guide-library-room-booking-20261120.docx](interview-guide-library-room-booking-20261120.docx) | Reviewed | `Research Plan - Library Room Booking.docx` for the guide. `guide.md` for the Word copy. |
| Synthetic sessions | [transcripts/](transcripts/) | Reviewed | `Research Plan - Library Room Booking.docx`, `interview-guide-library-room-booking-20261120.docx` |
| Source inventory | [study-manifest.json](study-manifest.json) | Reviewed | All seven files under `transcripts/` |
| Qualitative analysis | [analysis.md](analysis.md), [evidence-ledger.json](evidence-ledger.json) | Reviewed | `Research Plan - Library Room Booking.docx`, `interview-guide-library-room-booking-20261120.docx`, `study-manifest.json` and the seven sources |
| Findings presentation | [research-report.pptx](research-report.pptx), [generate.js](generate.js) | Reviewed | `Research Plan - Library Room Booking.docx`, `analysis.md`, `study-manifest.json`, `evidence-ledger.json`, `transcripts/S07-P6-followup.txt` and `generate.js` for the PowerPoint |

## Verification

- All 13 bundled unit tests passed in the bundled Python runtime through uv.
- The harness verifier accepted the manifest and ledger. Two tests on temporary copies confirmed that it rejected a changed follow up source and a quote absent from its source.
- Spotting an initial fixture failure confirmed that the verifier expects participant codes such as P1, with no leading zeros. The final sample uses P1 through P6.
- Compared 18 ledger excerpts, six quotations in the analysis and seven quotations in the deck against exact lines in their sources. The PowerPoint carries source and participant codes and keeps the counts and counterexamples in context.
- Rendered and inspected the two three page Word documents and all 11 PowerPoint slides in Microsoft Office. The bundled Word converter continues numbering across lists and leaves inline code marks in headings. The sample Word files use adjusted list formatting and cleaned up headings.
- The verifier checks source integrity and evidence structure. It cannot establish research quality, consent or population conclusions. A real study would need approved data handling and researcher review. No fieldwork or recruitment is pending for this exercise.

## Replay

From this sample directory, use Python with python-docx installed and Node with pptxgenjs available. The documented UXR workflow guides the planning and synthesis. The harness provides scripts for the mechanical checks and Word conversion.

```powershell
$harness = Resolve-Path '../..'
python (Join-Path $harness 'scripts/verify_study.py') verify study-manifest.json evidence-ledger.json
python -m unittest discover -s (Join-Path $harness 'tests') -v
```

The bundled converter takes `plan.md` or `guide.md` followed by the desired Word path. Use new output filenames when replaying to preserve these finished examples. Running `node generate.js` recreates the deck in this folder and replaces the existing deck.

## Dependency snapshot

The table records SHA-256 for the files listed above. Compare input hashes before reuse. If an input changes, mark affected stages stale and retain the prior output until the replacement has been reviewed.

| File | SHA-256 |
|---|---|
| [brief.md](brief.md) | `6ecb439ac84e76621b6a7d68bf9913c1bb902665698f44231c009a328c53056d` |
| [plan.md](plan.md) | `26a68a648cbc46f96c35d5aa5cbe09cc27113a9c7f33cb0b0962a3f02e352de8` |
| [Research Plan - Library Room Booking.docx](Research%20Plan%20-%20Library%20Room%20Booking.docx) | `35b679f2628b4cd7ff94674735932bdd07af8413f7e74fd87dd88d3351804d3c` |
| [guide.md](guide.md) | `f240c43e01f7317567b87e4d9369a855c5ed6bb37592cae88e1a52aa12391c96` |
| [interview-guide-library-room-booking-20261120.docx](interview-guide-library-room-booking-20261120.docx) | `417ce38fc5e26826d1b9a83da3fd6b186259d5d23636777f715736d4b1951661` |
| [study-manifest.json](study-manifest.json) | `d6e8e0cc8e78c5c2c20e6a41d5128e3b38a0cd61c8a4876b8f4b37f2642af051` |
| [evidence-ledger.json](evidence-ledger.json) | `8915b065f79a70bafb288293593894c4c465633671617b391d412f63db947c32` |
| [analysis.md](analysis.md) | `1509e73bc9ceae836dcc7b7478e562e0f13b517530c477cef7c19c8c644931f9` |
| [generate.js](generate.js) | `294e7f5e61135e24a181631fd89f1878425f88125d4b24bd30b1bcae14320dd1` |
| [research-report.pptx](research-report.pptx) | `7814ee0e6d7866236408ba4710916d6e6a89365f25b0191f6f3694858fb56846` |
| [transcripts/S01-P1.txt](transcripts/S01-P1.txt) | `734714420c3a388f4d68b0067bfe22ef4b550ac5e49f491d58a12766f5245560` |
| [transcripts/S02-P2.txt](transcripts/S02-P2.txt) | `acb4ee17a50c2402831582c877c9bf8021ba7feb5840a4b753ba77c6442b85aa` |
| [transcripts/S03-P3.txt](transcripts/S03-P3.txt) | `f056e715bd23148723612206ce545dad27a9fbd178466ac09aebf6efc0be45dd` |
| [transcripts/S04-P4.txt](transcripts/S04-P4.txt) | `31fa0272646a40a8c4a7566d15ac4f55efa6ce436a13925a3041e9edd6074caf` |
| [transcripts/S05-P5.txt](transcripts/S05-P5.txt) | `77284633bcf421b8a076326217d3de18b94cb02d6e697aad59226809691a3400` |
| [transcripts/S06-P6.txt](transcripts/S06-P6.txt) | `5266eeefaf01fbc60d450d8d412a5c65c4c742734549f6ae2c095bf5f567cdb0` |
| [transcripts/S07-P6-followup.txt](transcripts/S07-P6-followup.txt) | `6cf2752314ca507a977d3eb7e15fa3fce13a6cda324d8a750ae45943cf59eb6d` |
