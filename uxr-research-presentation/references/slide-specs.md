# Slide Specifications — UX Research Report (Default Professional Design System)

Detailed content and layout rules for each slide. All coordinates assume `LAYOUT_WIDE` (13.33" × 7.5"). The default palette uses a neutral professional blue scheme — see the cheatsheet to swap values for your organization's brand.

---

## Global Rules (apply to every slide)

- **Background:** white `FFFFFF` on all slides.
- **Section title:** navy `002A86`, 20pt, sentence case. `x: 0.55, y: 0.55, w: 12.23`. Height is one line (`h: 0.40`) for short titles and two lines (`h: 0.74`) for long declarative headlines; the `sectionTitle` helper sizes the box to the line count. The thin blue `0070F2` 1.5pt underline sits **just below the actual title box**, not at a fixed y: a one-line title puts it at `y ≈ 1.0`, a two-line title at `y ≈ 1.34`. Use the y the helper returns; never hard-code it. The title owns the full top-left zone; nothing else sits at `y: 0.55` on a content slide.
- **No dark header rectangle** — the title sits directly on white.
- **Logo:** If supplied or explicitly requested, the organization logo appears on the cover slide only. Content slides carry no logo. Do NOT call `addLogo` on any non-cover slide.
- **Content starts at** `y ≈ 1.69` (just below the title underline).
- **Left margin:** `x: 0.55`. **Full content width:** `w: 12.23`.
- **Font:** Default `Calibri`. Override with your organization's font via the `FONT` constant. Body text is black (`000000`).

---

## S1 — Cover Page

| Zone | Content |
|------|---------|
| Cover | White background. Large navy title (36pt), subtitle (16pt), author and date (12pt). Use a logo or image only when supplied or explicitly requested. |
| Optional note | Include a distribution label only when appropriate to the study. |

**Fields:**
- Title: study name (large, 36pt navy)
- Subtitle: product area + research type (e.g. "Platform Name — Generative Research"), primary blue `0070F2`, 16pt
- Author: `"| Researcher Name, Organization"` with `|` in amber `F0AB00`, name in muted `595959`, 12pt
- Date: same pattern as author line

---

## S2 — Table of Contents

Two-column table. No header row. `x: 0.39, y: 1.38, w: 12.54`.

| Column | Content |
|--------|---------|
| Col 1 (w: 1.09") | Section number. 24pt, default font, centred, inherits dark theme color. All rows same style. |
| Col 2 (w: 11.45") | Section title. 18pt, default font, navy `002A86`. Active/highlighted row: bold, cell fill `1B90FF`. Non-highlighted rows: not bold, no fill. |

**Row height:** 0.68" for all rows.

**Active row highlighting:**
- The currently active section row gets a solid `1B90FF` fill on the title cell. Number cell has no fill.
- Active row title text: bold.
- All other rows: no fill, non-bold.

**No sub-items / no indentation.**

---

## S3 — Objectives & Methodology *(combined)*

**Two-column layout** with a light grey divider line between columns.

### Left column (`x: 0.55, w: 5.8"`)

1. **"Objectives"** — primary blue `0070F2` bold, 18pt
2. 2–3 sentence summary of why the research was conducted — black, 13pt
3. **"Research Questions"** — primary blue `0070F2` bold, 16pt
4. Bulleted list of 4–6 research questions — black 12pt, bullet `•  ` prefix, indented

Footer: italic muted note on expected impact, 11pt.

### Divider
Vertical line `x: 6.65`, `y: 1.69`, `h: 5.0"`, grey `D9D9D9`, 1pt.

### Right column (`x: 7.0, w: 6.0"`)

1. **"Methodology"** — primary blue `0070F2` bold, 18pt
2. Key-value rows for each method attribute. Bold blue `0070F2` label (12pt) on left ~1.7", plain black detail on right. Light grey separator line between rows.

Method attributes: Research Type, Format, Duration, Sessions, Date Range, Recruitment, Notes.

---

## S4 — Participant Overview

Full-width table `x: 0.55, w: 12.23`, starts `y: 1.69`.

| Column | Header |
|--------|--------|
| ID | "Participant" |
| Location | "Location" |
| Role | "Role" |
| Industry | "Industry" |
| Primary Responsibility | "Primary Responsibility" |
| Systems Used | "Systems Used" |

**Header row:** Primary blue `0070F2` fill, white bold text, 13pt.
**Data rows:** white fill, black 11.5pt text, grey `D9D9D9` border.
**Row height:** ~1.0" to accommodate multi-line cells.

Include only context needed for the decision, generalized when appropriate. Never include names or employers. Assess whether combinations of role, location, systems and quotations could identify someone. Footer: participant count and relevant sample limitations.

---

## S5 — Executive Summary

**No right column.** Full-width content (`w: 12.23`), starts `y: 1.69`.

**Body:** 4–5 key findings. Each finding is a single paragraph of mixed-weight text:
- Plain black 14pt for context words.
- Bold primary blue `0070F2` 14pt for the core concept/term.
- Small blue filled circle (`ShapeType.ellipse`, 0.12" × 0.12", `fill: 0070F2`) as the bullet, left of each paragraph.

Paragraph spacing: ~0.9" per finding.

**Footer:** italic muted note on design implication and sample-size caveat, 10pt, `y ≈ 6.6`.

---

## S6–S10 — Insight Slides (one per theme)

**Repeat this layout for each theme.**

### Slide Header
- **Headline:** navy `002A86`, 20pt, full-width, sentence case. Written as an active declarative sentence.
- **Theme label:** small muted text "Theme N of N", right-aligned, sitting just above the underline (`y = underlineY - 0.24`), so it tracks a wrapped title instead of overlapping it.
- Thin blue `0070F2` underline below the headline at the y returned by `sectionTitle` (one line `y ≈ 1.0`, two lines `y ≈ 1.34`).

### Left Column (`x: 0.55, w: 7.9"`)

Repeat 2–4 **section blocks**, each consisting of:

```
[Section label — primary blue 0070F2, bold, 16pt]
  •  [Insight bullet — black 13pt]
  •  [Insight bullet — black 13pt]
```

Use `bulletSection(slide, x, y, w, label, items[])` helper from the cheatsheet.

### Right Column (`x: 8.45, w: 4.6"`)

Stack **participant quotes** (plain italic text, no fill). Each quote:
- Plain black italic text, 11pt, default font.
- Attribution at end: `— Px, Role`.
- Height: auto-sized to content (~0.8–1.6").
- Gap between quotes: ~0.3".

Use only as many accurately attributed, consented quotes as support the finding. Preserve counts, limitations and meaningful counter-evidence; do not invent quotes to fill the layout.

**Do NOT** use coloured filled rectangles or boxes. Quotes are plain text only.

### Bottom Bar (full width)

Optional only when a reviewed recommendation is supported by this finding:

1. Thin blue `0070F2` horizontal line at `y: 6.62`, full width.
2. `Design Recommendation:` in bold primary blue `0070F2` (12pt) followed by 1–2 italic black sentences.

---

## S11 — Opportunity Areas

**2×2 card grid.** Each card is a bordered white rectangle.

Card dimensions: `w: 5.85", h: 2.65"`.
Card positions: top-left `(0.55, 1.69)`, top-right `(7.0, 1.69)`, bottom-left `(0.55, 4.45)`, bottom-right `(7.0, 4.45)`.

**Per card:**
- Grey border `D9D9D9`, 1pt.
- Primary blue `0070F2` left accent stripe: `w: 0.06", h: 2.65"`.
- Title: bold navy `002A86`, 13pt, `x+0.15`, `y+0.1`.
- Body text: black 10.5pt, 2–3 sentences.
- Signal line: italic muted `595959` 9.5pt.
- Design directions: primary blue `0070F2` `→  direction` lines, 10pt.

---

## S12 — Strategic Recommendations

Full-width list, starts `y: 1.69`. Small italic muted caveat line at top.

**Per recommendation:**
- Priority badge: filled rectangle `w: 1.45", h: 0.36"`.
  - HIGH → red `C00000`
  - MEDIUM → primary blue `0070F2`
  - EXPLORATORY → muted grey `595959`
  - White bold text inside badge, 9.5pt, centred.
- Recommendation: bold navy `002A86` 12pt, `x: 1.85`.
- Rationale: black 10.5pt, `x: 1.85`, below recommendation.
- Light grey `E8E8E8` separator line between items.

Row spacing: ~0.82" per recommendation. Include only supported recommendations, sorted by stated priority.

---

## S13 — Appendix

Title: "Appendix — Peripheral & Low-Signal Insights"

**Header note:** Explain the actual limitations of the evidence. A single serious usability or safety issue can justify action; frequency alone does not determine importance.

**Per item:**
- Blue pill badge: light blue fill `D1EFFF`, blue bold text `0070F2`, 9.5pt, `w: 1.45"`, centred — holds the topic group label.
- Insight statement: bold navy `002A86` 12pt, right of badge.
- Quote block below the insight: plain italic text (no fill box), 11pt, grey `595959`.

Row spacing: ~1.3" per item. 4–6 appendix items typical.
