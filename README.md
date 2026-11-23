# UXR Ops Harness

UXR Ops is a set of agent instructions and local tools for running a UX research study from a brief to a findings presentation. It keeps findings traceable to source excerpts and tracks which artifacts depend on each other. The workflow is designed for qualitative interviews and moderated usability studies.

**Version 2.0.** See [What's new in 2.0](#whats-new-in-20).

## What's new in 2.0

- **One command-line tool, `uxrops`.** It covers `init`, `hash`, `verify`, `check-report`, `status`, `record` and `docx`, and needs only the Python standard library (Word export also needs python-docx). Run it from a checkout with `python scripts/uxrops.py`, or install it with `pip install .`.
- **Report and deck checks.** `check-report` traces every quotation in an analysis, Word report or PowerPoint deck back to a registered source and the evidence ledger. It catches wrong participant or source attributions, unknown theme and research question IDs, and mismatched "N of M" counts.
- **Stale-artifact tracking.** `uxr-project.json` records which files each artifact is built from. `status` follows the chain and flags anything modified or stale. `record` saves hashes after review and writes atomically.
- **Sturdier verification.**
  - Edited quotes (`…` cuts and `[inserts]`) are supported through `display_quote`.
  - Line, paragraph and timestamp locators are checked.
  - Warnings are reported separately from failures, with `--strict`.
  - `--format json` gives output for automation, and `--normalize` ignores quote-mark and whitespace differences.
  - Research questions and recommendations are linked to themes.
- **Deck template.** [generate-deck.js](uxr-research-presentation/assets/generate-deck.js) renders the findings deck from a `deck-content.json` file, so each study no longer needs a hand-written script.
- **Fixes.**
  - Study files are excluded from line-ending conversion, so source hashes no longer drift after checkout on another OS.
  - The quote-editing rules now match what the verifier accepts.
  - Word headings keep inline formatting.
  - JSON files saved with a Windows byte-order mark load correctly.
- **Continuous integration.** Tests run on Windows, macOS and Linux with Python 3.10 to 3.13, and a separate job renders and checks the fixture deck.

Studies started with 1.x keep working: `scripts/verify_study.py` still accepts its old commands, and the new ledger fields are optional. To add stale tracking to an existing study, run `python scripts/uxrops.py init <study-folder>`. It adds `uxr-project.json` and `.gitattributes` without overwriting your files.

## Quick start

1. Clone the repository, or download it from the GitHub **Code** menu, and open a terminal at the repository root:

   ```bash
   git clone https://github.com/anishbaral2012/uxr-ops-harness.git
   cd uxr-ops-harness
   ```

2. Create a study folder in approved storage. If you are starting with a non-sensitive brief, you can use a local folder such as `studies/my-study`:

   ```bash
   python scripts/uxrops.py init studies/my-study --name "My study"
   ```

3. Give an assistant with local file access your brief and point it to the [root SKILL.md](SKILL.md), or follow the instructions manually.

For example, ask your assistant:

> Read the root SKILL.md and use my brief to draft a research plan. Save the plan in my study folder and record decisions and artifact status in uxr-project.json.

## Run your study

| Stage | What to provide | What to produce |
| --- | --- | --- |
| [Plan](uxr-research-plan/SKILL.md) | Product brief, audience, and decision | Research questions, method, recruiting criteria, and handling decisions |
| [Discussion guide](uxr-interview-questions/SKILL.md) | Research plan and session constraints | Screener, moderator script, and question mapping |
| [Qualitative analysis](uxr-qual-analysis/SKILL.md) | Plan, approved sources, and participant mapping | Manifest, evidence ledger, and findings with counterexamples |
| [Findings presentation](uxr-research-presentation/SKILL.md) | Reviewed analysis and research plan | PowerPoint readout with findings, limits, and evidence links |

For a real study, read the [research operations guidance](references/research-operations.md) before collecting or processing sources. Keep real study files in approved storage. Never commit identifiable transcripts, consent forms, participant contact details, code keys, or restricted quotations to this public repository. A local ignore rule for `studies/` helps avoid accidental staging. It does not provide access control.

The Python tools verify artifacts, track which outputs are stale and convert Markdown to Word. They do not generate research content by themselves. Surveys, experiments, and other quantitative methods need their own analysis workflow.

## Commands

| Command | What it does |
| --- | --- |
| `init <folder>` | Creates a study folder skeleton without overwriting anything |
| `hash <files>` | Prints SHA-256 hashes for source files |
| `verify <study-folder>` | Checks the manifest and evidence ledger against the sources |
| `check-report <documents>` | Checks analysis, Word and PowerPoint outputs against the ledger |
| `status [study-folder]` | Shows which artifacts are ok, modified or stale |
| `record <artifact>` | Records hashes after an artifact has been reviewed |
| `docx <input.md> <output.docx>` | Converts Markdown to Word (needs python-docx) |

Run any command as `python scripts/uxrops.py <command>`, or as `uxrops <command>` after `pip install .`. Exit codes are 0 for pass, 1 for a check failure and 2 for a usage or input error.

## Set up a study folder

The `uxrops` tools use only the Python standard library (Word export also needs python-docx). Use Python 3.10 or later. On Windows, use `py -3` if `python` is unavailable; on macOS or Linux, use `python3` if needed. Run them from a checkout without installing anything:

```bash
python scripts/uxrops.py init studies/my-study --name "My study"
```

`init` creates `uxr-project.json`, an empty `study-manifest.json` and `evidence-ledger.json`, a `transcripts/` folder and a `.gitattributes` that turns off line-ending conversion for the study. It never overwrites existing files. To install the command instead, run `pip install .` (or `pip install ".[docx]"`) and use `uxrops` in place of `python scripts/uxrops.py`.

## Verify your evidence

Follow the [study schema](references/study-schema.md) to fill in `study-manifest.json` and `evidence-ledger.json`. Register approved UTF-8 source copies relative to the study folder. Assign a unique source ID to each file and use the same participant code for follow-ups. Use codes such as `P1` and `P2`.

```bash
python scripts/uxrops.py hash studies/my-study/transcripts/p1.txt
python scripts/uxrops.py verify studies/my-study
```

A valid run prints `PASS: mechanical checks only; researcher review remains required.` The verifier checks:

- source hashes and the source snapshot
- participant attribution
- that each excerpt exists in its source, including excerpts edited with `…` cuts and `[inserts]`
- that `line`, `paragraph` and timestamp locators point at the excerpt
- links between themes, research questions and recommendations

Warnings, such as single-participant themes or research questions no theme answers, need review but do not fail the run. Use `--strict` to make them fail, `--format json` for agents and CI, and `--normalize` to ignore curly versus straight quote marks and whitespace.

Then check the outputs people will read against the ledger:

```bash
python scripts/uxrops.py check-report --study studies/my-study studies/my-study/analysis.md studies/my-study/research-report.pptx
```

`check-report` reads Markdown, Word and PowerPoint files. It fails when a quotation is not in any registered source, when a quotation is attributed to the wrong participant or source, or when a theme or research question ID does not exist. It warns when a quotation is not recorded in the ledger, a ledger theme is missing from a document, or an "N of M" count does not match the theme's supporting participants.

A reviewer should still follow each `source_id` and locator to the precise source passage, then review interpretation, privacy and output layout.

## Track what is stale

`uxr-project.json` lists each artifact's files and the artifacts it is built from. After reviewing an artifact, record its hashes, then check the study at any time:

```bash
python scripts/uxrops.py record plan --project studies/my-study --status reviewed
python scripts/uxrops.py status studies/my-study
```

`status` reports each artifact as `ok`, `planned`, `unrecorded`, `missing`, `modified` (its own files changed) or `stale` (an input changed or is not ok), following the dependency chain. It exits with 1 when anything needs attention. `--mark-stale` writes the stale status back to the file, and `--format markdown` prints a table for `uxr-project.md` notes. `record` refuses to record an artifact while its inputs are not ok, and every write replaces the file atomically.

## Export documents and run tests

Install [uv](https://docs.astral.sh/uv/) for the commands below. Run them from the repository root.

```bash
uv run --with python-docx==1.2.0 python -m unittest discover -s tests -v
uv run --with python-docx==1.2.0 python scripts/uxrops.py docx studies/my-study/guide.md studies/my-study/guide.docx
```

The converter supports common Markdown elements such as headings (including inline formatting), prompts, lists, checkboxes and tables. Review the Word output, especially adjacent numbered lists, which continue their numbering.

To create a PowerPoint, fill in a `deck-content.json` and render it with the bundled [deck template](uxr-research-presentation/assets/generate-deck.js), which uses Node.js and PptxGenJS 4.0.1. See the [findings presentation instructions](uxr-research-presentation/SKILL.md).

The [GitHub Actions workflow](.github/workflows/checks.yml) runs the tests on Windows, macOS and Linux with Python 3.10 to 3.13. It also verifies the fixture study after checkout, renders the fixture deck from the template, and checks that deck against the ledger.

## Repository layout

| Path | Contents |
| --- | --- |
| `SKILL.md` and the four stage folders | Agent instructions for planning, guides, analysis and the findings deck |
| `references/` | Research operations checklist and the study schema |
| `uxrops/` | The command-line tool (standard library only) |
| `scripts/` | `uxrops.py` to run the tool from a checkout, and the 1.x `verify_study.py` entry point |
| `uxr-research-presentation/assets/` | The deck template |
| `tests/` | Unit tests and the synthetic `mini-study` fixture |

## Help and contributions

Open a GitHub issue for setup questions, bugs, or feature ideas. Include your OS, Python version, the command you ran, and steps to reproduce the issue. For a pull request, run the tests above and update the relevant documentation.

## License

Released under the [MIT License](LICENSE).
