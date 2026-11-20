# UXR Ops Harness

UXR Ops is a set of agent instructions and local tools for running a UX research study from a brief to a findings presentation. It keeps findings traceable to source excerpts and tracks which artifacts depend on each other. The workflow is designed for qualitative interviews and moderated usability studies.

Start with the [library room booking sample](samples/library-room-booking/uxr-project.md) to see a completed run. It includes a [Word research plan](samples/library-room-booking/Research%20Plan%20-%20Library%20Room%20Booking.docx), [discussion guide](samples/library-room-booking/interview-guide-library-room-booking-20261120.docx), [qualitative analysis](samples/library-room-booking/analysis.md), and [PowerPoint readout](samples/library-room-booking/research-report.pptx). All seven source excerpts represent fictional sessions with six fictional participants.

## Quick start

1. Clone the repository or download its ZIP from the GitHub **Code** menu. Open a terminal at the repository root.
2. Use Python 3.10 or later to verify the supplied study. The verifier uses the Python standard library and works without an AI account or API key.

   ```bash
   python scripts/verify_study.py verify samples/library-room-booking/study-manifest.json samples/library-room-booking/evidence-ledger.json
   ```

   On Windows, use `py -3` if `python` is unavailable. On macOS or Linux, use `python3` if needed. A valid run prints `PASS: mechanical checks only; researcher review remains required.`

3. Open the [sample evidence ledger](samples/library-room-booking/evidence-ledger.json). Follow a `source_id` and line locator through the [manifest](samples/library-room-booking/study-manifest.json) to its [transcript](samples/library-room-booking/transcripts/S01-P1.txt). This is how a reviewer can check where a finding came from.

The verifier checks source hashes, the complete source snapshot, participant attribution, and whether quoted excerpts exist in their registered sources. Review locators, interpretations, privacy, and document layout separately.

## Run your own study

Create a separate study folder. Open it with an assistant that can read local files and point it to the [root SKILL.md](SKILL.md). The workflow also works as a manual checklist. The Python commands verify artifacts or convert Markdown to Word. They do not generate research content by themselves.

| Stage | What to provide | What to produce |
| --- | --- | --- |
| [Plan](uxr-research-plan/SKILL.md) | Product brief, audience, and decision | Research questions, method, recruiting criteria, and handling decisions |
| [Discussion guide](uxr-interview-questions/SKILL.md) | Research plan and session constraints | Screener, moderator script, and question mapping |
| [Qualitative analysis](uxr-qual-analysis/SKILL.md) | Plan, approved sources, and participant mapping | Manifest, evidence ledger, and findings with counterexamples |
| [Findings presentation](uxr-research-presentation/SKILL.md) | Reviewed analysis and research plan | PowerPoint readout with findings, limits, and evidence links |

For example, ask your assistant:

> Follow the root SKILL.md. Use my brief to draft a research plan in studies/my-study. Record key decisions and artifact paths in uxr-project.md.

Before analyzing real sources, read the [research operations guidance](references/research-operations.md) and the [manifest and ledger format](references/study-schema.md). Register approved UTF-8 source copies relative to the study folder. Assign a unique source ID to each file and use the same participant code for follow-ups. Use codes such as `P1` and `P2`.

```bash
python scripts/verify_study.py hash studies/my-study/transcripts/p1.txt
python scripts/verify_study.py verify studies/my-study/study-manifest.json studies/my-study/evidence-ledger.json
```

Keep real study files in approved storage. Never commit identifiable transcripts, consent forms, participant contact details, code keys, or restricted quotations to this public repository. A local ignore rule for `studies/` helps avoid accidental staging. It does not provide access control. Surveys, experiments, and other quantitative methods need their own analysis workflow.

## Export documents and run tests

Install [uv](https://docs.astral.sh/uv/) for the commands below. Run them from the repository root.

```bash
uv run --with python-docx==1.2.0 python -m unittest discover -s tests -v
uv run --with python-docx==1.2.0 python uxr-interview-questions/references/md-to-docx.py samples/library-room-booking/guide.md sample-guide.docx
```

The converter supports common Markdown elements such as headings, prompts, lists, checkboxes, and tables. Review the Word output, especially headings with inline formatting and adjacent numbered lists.

To rebuild the sample PowerPoint, use Node.js and npm in a disposable checkout. The generator writes over the sample PowerPoint in that checkout. Open the result and review the layout and quotations.

```bash
npm install --no-save --package-lock=false pptxgenjs@4.0.1
node samples/library-room-booking/generate.js
```

The [example GitHub Actions workflow](.github/examples/checks.yml) runs the Python tests and verifies the sample on Windows and Linux when enabled. To enable it in a repository you maintain, copy it to .github/workflows/checks.yml. The checked-in sample preserves its exact bytes across checkouts so the SHA-256 evidence hashes stay valid.

## Help and contributions

Open a GitHub issue for setup questions, bugs, or feature ideas. Include your OS, Python version, the command you ran, and a minimal example using fictional data. For a pull request, run the tests above and update documentation or the sample if the workflow changes.

No open-source license has been specified for this repository.
