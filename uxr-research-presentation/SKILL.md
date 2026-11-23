---
name: uxr-research-presentation
description: Create a UX research findings presentation from reviewed, source-linked analysis and a research plan.
---

# UX Research Presentation Skill

Generates a polished PowerPoint research report from structured analysis input (themes, insights, participant data, recommendations), using a clean professional design system with a neutral palette you can swap for your organization's brand.

## Quick Reference

| Step | Action |
|------|---------|
| 0 | Gather and validate inputs |
| 1 | Generate PowerPoint using pptxgenjs |

Reference files (read on demand):
- [references/slide-specs.md](references/slide-specs.md) — exact layout and content rules per slide.
- [references/pptxgenjs-cheatsheet.md](references/pptxgenjs-cheatsheet.md) — pptxgenjs syntax, default palette, and reusable helper patterns.

> ⚠️ **Common generation mistakes — check these before writing a single line of code:**
> 1. ❌ Filled blue rectangle as a sub-heading bar on content slides → ✅ `titleUnderline()` (1.5pt line) only
> 2. Add a recommendation strip only when the research supports a reviewed recommendation for that finding.
> 3. ❌ Plain dash/circle bullets on Executive Summary → ✅ filled blue ellipse + bold blue term + black sentence
> 4. ❌ Opportunity cards missing the blue left accent stripe → ✅ 0.06"-wide blue rect on every card
> 5. ❌ HIGH/MEDIUM as coloured text only → ✅ filled badge rectangles (`C00000` / `0070F2`), white text inside
> 6. ❌ Purple filled quote boxes on insight slides → ✅ plain black italic text, no fill, 11pt
> 7. ❌ Logo on content slides (collides with the title at y:0.55) → ✅ Logo on the cover slide only; no logo anywhere else
> 8. ❌ Old navy `0E2841` or old blue `0070C0` → ✅ Use `002A86` navy and `0070F2` primary blue
> 9. ❌ Font Aptos or Arial as primary → ✅ Set the `FONT` constant to your organization's font (default: `Calibri`)
> 10. Use a text-led cover. Include a logo or image only when the user provides or explicitly requests it.

---

## Step 0 — Gather and Validate Inputs

### Required
This skill requires structured analysis input. Accepted forms:
- Output produced by **uxr-qual-analysis** (preferred).
- Reviewed analysis containing source-linked findings, appropriate supporting evidence, participant codes and relevant limitations. Include recommendations or opportunities only where supported.
- A research plan (used to populate the Objectives slide).

### Asset check
The default cover is text-only and requires no bundled or project image. Include an organization logo or other image only when supplied or explicitly requested for the report. Do not search for or silently reuse unrelated branded assets. Do not overwrite a study asset.

**If a sample `.pptx` was provided:**
When the user asks to match a sample, inspect its design and use only the assets they authorize:
```bash
unzip -o "path/to/sample.pptx" "ppt/media/*" -d /tmp/pptx_media
```

### If inputs are missing
- If **no structured analysis** is provided: ask the user to run uxr-qual-analysis first, or to share their existing analysis document.
- If **research plan is missing**: infer Objectives slide content from the analysis document if enough context exists; otherwise ask.
- If **participant overview is missing**: ask the user to provide it or note "Not available" on the slide.

### Clarifying questions
Ask the user **only** if the following remain unclear after reading the materials. Group into one message:
1. Are there any screenshots or video clips to embed in insight slides? (usability studies only)
2. Is there a sample `.pptx` file to match in design? If yes, extract its palette and layout before generating.
3. Where should the output `.pptx` be saved? (If uxr-ops passed an absolute save path, use it and do not ask. Standalone default: `./output/` in the current working directory.)

---

## Step 1 — Generate the PowerPoint

Render decks with the bundled template [assets/generate-deck.js](assets/generate-deck.js) instead of writing a new generation script. It implements the slide order and layout rules below and validates its input. Write the study content to `deck-content.json` in the study folder, modeled on [the fixture example](../tests/fixtures/mini-study/deck-content.json):

- `meta` (title, subtitle, author, date, optional footer and distribution label)
- `objective` and `research_questions`
- `methodology` rows
- `participants` columns and rows
- `executive_summary`
- `themes`, each with an ID, headline, blocks, quotes and callout
- optional `opportunities`, `recommendations` and `appendix`
- `limitations`

Copy each quote's `text` from the ledger's `display_quote` or `quote`, without its own quotation marks, and give its `participant`, `source_id` and `locator`. The template adds the quotation marks and attribution that `check-report` traces.

```bash
node <path-to-harness>/uxr-research-presentation/assets/generate-deck.js <study-folder>/deck-content.json <study-folder>/research-report.pptx
python <path-to-harness>/scripts/uxrops.py check-report --study <study-folder> <study-folder>/research-report.pptx
```

To brand the deck, change only the palette and `FONT` block at the top of a copy of the template, and keep that copy next to the deck. Read [references/pptxgenjs-cheatsheet.md](references/pptxgenjs-cheatsheet.md) only when a layout the template does not cover is genuinely needed.

If uxr-ops passed an absolute save path, write `deck-content.json` and the `.pptx` there. With no save path passed (standalone use), the default output path is `./output/research-report.pptx`.

Before running, verify pptxgenjs 4.0.1 is available, for example `npm install --prefix <approved-tools-folder> pptxgenjs@4.0.1` with `NODE_PATH` pointing at its `node_modules`. Use an existing approved runtime or ask how to proceed if the dependency is unavailable; do not silently modify the study folder's dependencies.

Resolve every `check-report` failure before delivering. Then inspect the generated deck itself, including source fidelity, privacy, slide layout and accessibility; neither the script nor the check verifies rendered layout.

### Slide Order

1. Cover Page
2. Table of Contents
3. Objectives & Methodology *(combined on one slide)*
4. Participant Overview
5. Executive Summary
6. Insight Slides (one per theme)
7. Opportunity Areas
8. Strategic Recommendations
9. Appendix

See [references/slide-specs.md](references/slide-specs.md) for exact layout, content rules, and field specifications per slide.

### Design System — Default Professional Theme

The default design system uses a clean, neutral professional palette. Users can swap every colour value and the logo for their organization's brand by editing the `C` palette object at the top of the generated script.

**No filled header bars on content slides.** The section title sits directly on a white background — compact, sentence-case, navy (`002A86`), 20pt. A thin blue (`0070F2`) underline line sits below it.
❌ Do NOT add any filled rectangle as a section divider or sub-heading.
✅ Use `titleUnderline()` helper (1.5pt blue line) below the main title only.

**Colour roles (default palette — override freely):**
- `002A86` deep navy — all slide headlines, section titles
- `0070F2` primary blue — sub-labels, bullet highlights, table headers, underline lines, rec labels
- `1B90FF` mid-blue — numbered list accents, TOC active row fill
- `89D1FF` light blue — tertiary step indicators, light backgrounds
- `D1EFFF` pale blue — very light tint, pill badge backgrounds
- `F0AB00` amber — cover author name pipe accent, disclaimer strip
- `FFFFFF` white — slide background throughout
- `595959` muted — secondary italic text, EXPLORATORY badge

**Font:** System default (`Calibri`). Override with your organization's font by setting the `FONT` constant.

**Cover page:** Text-led cover on a white background with study title, research type, author and date. Add only user-supplied or explicitly requested branding.

**Logo placement:** If supplied or explicitly requested, place the organization logo on the cover only. Content slides carry no logo, so the section title owns the top-left zone (`x:0.55, y:0.55`) without collision.

**Participant quotes on insight slides.**
✅ Use plain italic text, 11pt, black, em-dash attribution.
✅ Place quotes in the right column (~35% width), stacked vertically.
❌ Do NOT use solid filled rectangles for quotes.

**Insight slide layout:** Left ~65% = section labels (blue `0070F2` bold) + bullet body text (black). Right ~35% = stacked participant quotes (plain italic text).

**Recommendation bars are optional.** Use one only when there is a reviewed, evidence-linked recommendation for the theme. Otherwise omit it.

**Recommendation bar style:** Thin blue `0070F2` horizontal line at `y≈6.62`, then `Design Recommendation:` label (bold blue) + italic black text. No filled bar.

**Executive Summary bullets use filled blue circles.**
✅ Small filled blue ellipse (0.12"×0.12", fill `0070F2`) + bold primary-blue term + black sentence.
❌ Do NOT use plain dash bullets or all-black text.

**Opportunity cards require a blue left accent stripe.**
✅ 0.06"-wide blue (`0070F2`) filled rectangle as the leftmost element of each card.
❌ Do NOT render cards without this stripe.

### Sample-size note
State distinct participant count, method, relevant denominators, sampling limitations, uncertainty, and consequential counter-evidence on the relevant slides or accompanying notes. Qualitative counts are not population estimates regardless of sample size. Protect against re-identification; do not include participant names or unnecessary attributes.

---

## Output

- File: `research-report.pptx` saved to the agreed path (default `./output/`).
- After generation, print the absolute path and suggest opening it with the platform's default app: `start "" "<path>"` on Windows, `open "<path>"` on macOS, or `xdg-open "<path>"` on Linux.
- Report the `check-report` result, including warnings reviewed.
- Briefly summarize: slide count, themes included, participant count, and any slides where assets were missing or content was thin.
