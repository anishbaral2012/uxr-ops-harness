# UXR Ops Harness

UXR Ops is a set of agent instructions and local tools for running a UX research study from a brief to a findings presentation. It keeps findings traceable to source excerpts and tracks which artifacts depend on each other. The workflow is designed for qualitative interviews and moderated usability studies.

## Quick start

1. Clone the repository or download it from the GitHub **Code** menu. Open a terminal at the repository root.
2. Create a study folder in approved storage. If you are starting with a non-sensitive brief, you can use a local folder such as `studies/my-study`.
3. Give an assistant with local file access your brief and point it to the [root SKILL.md](SKILL.md), or follow the instructions manually.

For example, ask your assistant:

> Read the root SKILL.md and use my brief to draft a research plan. Save the plan in my study folder and record decisions and artifact paths in uxr-project.md.

## Run your study

| Stage | What to provide | What to produce |
| --- | --- | --- |
| [Plan](uxr-research-plan/SKILL.md) | Product brief, audience, and decision | Research questions, method, recruiting criteria, and handling decisions |
| [Discussion guide](uxr-interview-questions/SKILL.md) | Research plan and session constraints | Screener, moderator script, and question mapping |
| [Qualitative analysis](uxr-qual-analysis/SKILL.md) | Plan, approved sources, and participant mapping | Manifest, evidence ledger, and findings with counterexamples |
| [Findings presentation](uxr-research-presentation/SKILL.md) | Reviewed analysis and research plan | PowerPoint readout with findings, limits, and evidence links |

For a real study, read the [research operations guidance](references/research-operations.md) before collecting or processing sources. Keep real study files in approved storage. Never commit identifiable transcripts, consent forms, participant contact details, code keys, or restricted quotations to this public repository. A local ignore rule for `studies/` helps avoid accidental staging. It does not provide access control.

The Python tools verify artifacts and convert Markdown to Word. They do not generate research content by themselves. Surveys, experiments, and other quantitative methods need their own analysis workflow.

## Verify your evidence

Follow the [study schema](references/study-schema.md) to create `study-manifest.json` and `evidence-ledger.json`. Register approved UTF-8 source copies relative to the study folder. Assign a unique source ID to each file and use the same participant code for follow-ups. Use codes such as `P1` and `P2`.

The verifier uses the Python standard library and requires no API key. Use Python 3.10 or later and replace the paths below with your study paths. On Windows, use `py -3` if `python` is unavailable. On macOS or Linux, use `python3` if needed.

```bash
python scripts/verify_study.py hash studies/my-study/transcripts/p1.txt
python scripts/verify_study.py verify studies/my-study/study-manifest.json studies/my-study/evidence-ledger.json
```

A valid run prints `PASS: mechanical checks only; researcher review remains required.` The verifier checks source hashes, the source snapshot, participant attribution, and whether the excerpts exist. A reviewer should also follow each `source_id` and locator through the manifest to check the precise source passage, then review interpretation, privacy, and output layout.

## Export documents and run tests

Install [uv](https://docs.astral.sh/uv/) for the commands below. Run them from the repository root.

```bash
uv run --with python-docx==1.2.0 python -m unittest discover -s tests -v
uv run --with python-docx==1.2.0 python uxr-interview-questions/references/md-to-docx.py studies/my-study/guide.md studies/my-study/guide.docx
```

The converter supports common Markdown elements such as headings, prompts, lists, checkboxes, and tables. Review the Word output, especially headings with inline formatting and adjacent numbered lists. To create a PowerPoint, follow the [findings presentation instructions](uxr-research-presentation/SKILL.md), which use Node.js and PptxGenJS.

The [example GitHub Actions workflow](.github/examples/checks.yml) runs the Python tests on Windows and Linux when enabled. To enable it in a repository you maintain, copy it to `.github/workflows/checks.yml`.

## Help and contributions

Open a GitHub issue for setup questions, bugs, or feature ideas. Include your OS, Python version, the command you ran, and steps to reproduce the issue. For a pull request, run the tests above and update the relevant documentation.

## License

Released under the [MIT License](LICENSE).
