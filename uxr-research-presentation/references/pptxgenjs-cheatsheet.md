# pptxgenjs Cheatsheet — Default Professional Design System

Syntax reference and reusable helpers for generating professional UX research reports. For full pptxgenjs docs see https://gitbrent.github.io/PptxGenJS/. Swap the `C` palette values for your organization's brand colours.

---

## Setup

```bash
npm install pptxgenjs
```

```javascript
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 inches
```

---

## Default Colour Palette

Override these values with your organization's brand colours. All helpers reference the `C` object, so a single swap updates the entire deck.

```javascript
const C = {
  navy:      "002A86",  // all slide headlines and section titles
  blue:      "0070F2",  // sub-labels, bullet highlights, table headers, lines, rec labels
  midBlue:   "1B90FF",  // numbered lists, secondary accents, TOC active row
  lightBlue: "89D1FF",  // tertiary accents
  paleBlu:   "D1EFFF",  // very light tint backgrounds
  red:       "C00000",  // HIGH priority badge
  amber:     "F0AB00",  // cover author name accent, disclaimer strip
  amberAlt:  "FDB913",  // secondary amber used on some cover text
  white:     "FFFFFF",
  black:     "000000",  // all body text
  muted:     "595959",  // secondary / italic text, EXPLORATORY badge
  border:    "D9D9D9",  // card borders and table cell borders
  separator: "E8E8E8",  // light row separators
  pillBg:    "D1EFFF",  // appendix group badge background
  bgGray:    "EAECEE",  // image placeholder panel backgrounds
};
```

---

## Layout Constants

```javascript
// LAYOUT_WIDE = 13.33" × 7.5"
const LM          = 0.55;   // left margin
const FULL        = 12.23;  // full content width (0.55 to 12.78 right edge)
const TOP_TITLE_Y = 0.55;   // section headline y
const TOP_TITLE_H = 0.40;   // section headline height (compact single-line)
const CONTENT_Y   = 1.69;   // content start (below title + underline)
```

---

## Font

```javascript
const FONT = "Calibri";  // Default system font. Replace with your organization's brand font.
// Example: const FONT = "Inter";  or  const FONT = "Source Sans Pro";
```

---

## Reusable Helpers

Copy these helper functions into every generation script.

### addLogo — organization logo (cover slide only)

The logo belongs on the cover slide only. Do NOT call this on content slides: the title owns the top-left zone (`y: 0.55`) and a logo there collides with the headline.

```javascript
function addLogo(slide) {
  // Cover slide only. Never call on a content slide.
  // Replace "org_logo.png" with your logo file. Omit this call if no logo is available.
  slide.addImage({
    path: "./assets/org_logo.png",
    x: 0.55, y: 0.55, w: 3.66, h: 0.39,  // top-left of the cover's white half
  });
}
```

### sectionTitle — large bold navy headline (one or two lines)

Headlines are written as active declarative sentences (see slide-specs), so an insight title often wraps to two lines. A fixed one-line box would let the second line collide with the underline and the "Theme N of N" label. So `sectionTitle` sizes its own box to the line count and **returns the y where the underline (and anything else below the title) should sit**. Always pass that return value to `titleUnderline` and use it to place the theme label; never hard-code the underline at y≈1.0.

```javascript
// Chars that fit on one line at 20pt across the full 12.23" width.
// 20pt Calibri averages ~0.126"/char, so ~97 chars; use 92 as a safe wrap threshold.
const TITLE_ONE_LINE_CHARS = 92;

function sectionTitle(slide, text) {
  const lines = text.length > TITLE_ONE_LINE_CHARS ? 2 : 1;
  const h = lines === 2 ? 0.74 : TOP_TITLE_H;   // 0.74" holds two 20pt lines
  slide.addText(text, {
    x: LM, y: TOP_TITLE_Y, w: FULL, h,
    fontSize: 20, bold: false, color: C.navy,
    fontFace: FONT, valign: "top", wrap: true,
  });
  // y for the underline: just below the actual title box, never above it.
  return TOP_TITLE_Y + h + 0.05;
}
// Returns the underline y. A one-line title returns ~1.00 (unchanged);
// a two-line title returns ~1.34, pushing the underline and theme label down with it.
```

### titleUnderline — thin blue line below title

Pass the y returned by `sectionTitle` so the line tracks a wrapped title instead of sitting under its first line.

```javascript
function titleUnderline(slide, y) {
  slide.addShape(pres.ShapeType.line, {
    x: LM, y, w: FULL, h: 0,
    line: { color: C.blue, width: 1.5 },
  });
}
// Content area still starts at CONTENT_Y=1.69, which clears a two-line title.
```

### participantQuote — plain italic text, no fill

```javascript
function participantQuote(slide, x, y, w, h, text) {
  slide.addText(text, {
    x, y, w, h,
    fontSize: 11, color: C.black, fontFace: FONT,
    italic: true, wrap: true, valign: "top",
  });
}
```

### bulletSection — blue label + indented black bullets

```javascript
function bulletSection(slide, x, y, w, label, items) {
  slide.addText(label, {
    x, y, w, h: 0.32,
    fontSize: 16, bold: true, color: C.blue, fontFace: FONT,
  });
  let cy = y + 0.36;
  items.forEach(item => {
    slide.addText("•  " + item, {
      x: x + 0.1, y: cy, w: w - 0.1, h: 0.38,
      fontSize: 13, color: C.black, fontFace: FONT, wrap: true,
    });
    cy += 0.42;
  });
  return cy; // returns y position after last bullet for chaining
}
```

### recBar — recommendation line at slide bottom

```javascript
function recBar(slide, text) {
  slide.addShape(pres.ShapeType.line, {
    x: LM, y: 6.62, w: FULL, h: 0,
    line: { color: C.blue, width: 1 },
  });
  slide.addText([
    { text: "Design Recommendation:  ", options: { bold: true, fontSize: 12, color: C.blue } },
    { text: text, options: { fontSize: 12, color: C.black, italic: true } },
  ], {
    x: LM, y: 6.68, w: FULL, h: 0.72,
    fontFace: FONT, wrap: true, valign: "top",
  });
}
```

---

## Cover Page Pattern

The default cover uses text on a white background and needs no image. Include branding only when supplied or explicitly requested.

```javascript
const s = pres.addSlide();
s.background = { color: C.white };

// Optional: organization logo top-left (omit if no logo file)
// addLogo(s);

// Title (36pt, sentence case, navy)
s.addText("Study Title", {
  x: LM, y: 2.96, w: 5.58, h: 1.09,
  fontSize: 36, bold: true, color: C.navy, fontFace: FONT, wrap: true,
});

// Subtitle (primary blue, 16pt) — replace with your product area and research type
s.addText("Product Area — Research Type", {
  x: LM, y: 4.15, w: 5.58, h: 0.45,
  fontSize: 16, color: C.blue, fontFace: FONT,
});

// Author name — amber accent prefix + muted name
s.addText([
  { text: "| ", options: { color: C.amber, bold: true } },
  { text: "Researcher Name, Organization", options: { color: C.muted } },
], { x: LM, y: 4.67, w: 5.91, h: 0.24, fontSize: 12, fontFace: FONT });

// Date
s.addText([
  { text: "| ", options: { color: C.amber, bold: true } },
  { text: "Month Date, Year", options: { color: C.muted } },
], { x: LM, y: 4.96, w: 5.91, h: 0.24, fontSize: 12, fontFace: FONT });

// Optional: disclaimer strip at very bottom-left — replace or remove as needed
s.addShape(pres.ShapeType.rect, { x: 0, y: 7.1, w: 6.5, h: 0.4, fill: { color: C.amber } });
s.addText("INTERNAL — Do not distribute", {
  x: 0.15, y: 7.12, w: 6.2, h: 0.28,
  fontSize: 10, color: C.white, bold: true, fontFace: FONT,
});
```

---

## Table of Contents Pattern

Build the table row by row. The active (currently highlighted) section gets a `1B90FF` fill on its title cell and bold text; all other rows have no fill and non-bold text.

```javascript
// sections: array of { num: "1", title: "Objectives & Methodology", active: true/false }
const rows = sections.map(sec => [
  {
    text: sec.num,
    options: {
      fontSize: 24, align: "center", fontFace: FONT,
      // No explicit color — inherits theme (near-black). Do NOT set to any blue.
      bold: false,
    },
  },
  {
    text: sec.title,
    options: {
      fontSize: 18, color: C.navy, fontFace: FONT,
      bold: sec.active ? true : false,
      fill: sec.active ? { color: C.midBlue } : { type: "none" },
    },
  },
]);

s.addTable(rows, {
  x: 0.39, y: 1.38, w: 12.54,
  rowH: 0.68,
  colW: [1.09, 11.45],
  border: { type: "none" },
  fontFace: FONT,
});
```

> **Active row color:** Use `C.midBlue` (`1B90FF`) for the active section accent. Do NOT use `00B0F0`.

> **Number column:** Do NOT colorize number cells. They inherit the theme dark color.

---

## Participant Table Pattern

```javascript
const hOpts = (t) => ({ text: t, options: { bold: true, color: C.white, fill: C.blue, fontSize: 13, fontFace: FONT } });
// C.blue = "0070F2" — primary blue used for table headers
const rows = [
  [hOpts("Participant"), hOpts("Context")],
  ["P1", "Generalized context relevant to the research"],
  // ...
];
s.addTable(rows, {
  x: LM, y: CONTENT_Y, w: FULL,
  fontSize: 11.5, fontFace: FONT, color: C.black,
  border: { type: "solid", color: C.border },
  rowH: 1.0,
  colW: [1.5, 10.73],
});
```

---

## Insight Slide Pattern

```javascript
const s = pres.addSlide();
s.background = { color: C.white };
// No logo on content slides — the title owns the top-left zone.

// Title first — it returns the underline y (tracks a one- or two-line headline).
const uy = sectionTitle(s, "Active headline summarising the theme");
titleUnderline(s, uy);

// Theme label — right-aligned, sitting just above the underline wherever it landed.
s.addText("Theme N of N", {
  x: 10.0, y: uy - 0.24, w: 2.73, h: 0.22,
  fontSize: 10, color: C.muted, fontFace: FONT, align: "right",
});

// Left column: section labels + bullets
const LX = LM, LW = 7.9, LY = CONTENT_Y + 0.1;
let cy = LY;
cy = bulletSection(s, LX, cy, LW, "Section Label", ["Bullet one", "Bullet two"]);
cy += 0.2; // gap between sections
cy = bulletSection(s, LX, cy, LW, "Second Section Label", ["Bullet one", "Bullet two"]);

// Right column: plain italic participant quotes (no fill)
const RX = 8.45, RW = 4.6;
const quotes = [
  '"Sure, so we have this tool or this window called Purchase Order Entry..." — P1, Role',
  '"Another participant insight here." — P2, Role',
  '"Third observation from research." — P3, Role',
];
let qY = CONTENT_Y + 0.1;
quotes.forEach((q, i) => {
  const qH = 0.9 + Math.ceil(q.length / 80) * 0.2;
  participantQuote(s, RX, qY, RW, Math.min(qH, 1.6), q);
  qY += Math.min(qH, 1.6) + 0.3;
});

// Add recBar only for a reviewed recommendation supported by this theme.
```

---

## Opportunity Card Pattern

```javascript
const opp = { title: "...", body: "...", signal: "...", directions: ["...", "..."] };
const x = 0.27, y = CONTENT_Y, w = 5.85, h = 2.65;

s.addShape(pres.ShapeType.rect, { x, y, w, h, fill: { color: C.white }, line: { color: C.border, width: 1 } });
s.addShape(pres.ShapeType.rect, { x, y, w: 0.06, h, fill: { color: C.blue } }); // accent stripe
s.addText(opp.title,  { x: x+0.15, y: y+0.1,  w: w-0.25, h: 0.3,  fontSize: 13,   bold: true, color: C.navy, fontFace: FONT });
s.addText(opp.body,   { x: x+0.15, y: y+0.44, w: w-0.25, h: 0.88, fontSize: 10.5, color: C.black, fontFace: FONT, wrap: true });
s.addText("Signal: " + opp.signal, { x: x+0.15, y: y+1.36, w: w-0.25, h: 0.24, fontSize: 9.5, color: C.muted, fontFace: FONT, italic: true });
opp.directions.forEach((d, di) => {
  s.addText("→  " + d, { x: x+0.15, y: y+1.65+di*0.38, w: w-0.25, h: 0.34, fontSize: 10, color: C.blue, fontFace: FONT });
});
```

---

## Save

```javascript
pres.writeFile({ fileName: "./output/research-report.pptx" })
  .then(f => console.log("Saved:", f))
  .catch(e => { console.error(e); process.exit(1); });
```

---

## Layout Coordinate Reference (LAYOUT_WIDE: 13.33" × 7.5")

| Zone | x | w | Notes |
|------|---|---|-------|
| Full content | 0.55 | 12.23 | Standard content area |
| Left column (insight) | 0.55 | 7.9 | ~65% — labels + bullets |
| Right column (insight) | 8.45 | 4.6 | ~35% — quote boxes only |
| Left card (opportunity) | 0.55 | 5.85 | 2×2 grid |
| Right card (opportunity) | 7.0 | 5.85 | 2×2 grid |
| Cover text | 0.55 | 5.98 | Title, subtitle and study metadata |
| Logo (cover slide only) | 0.55, y=0.55 | 3.66, h=0.39 | Only when supplied or explicitly requested; no logo on content slides |
| Section title | 0.55, y=0.55 | 12.23, h=0.40 | 20pt navy, sentence case |
| Content start | — | y=1.69 | Below title + underline |
| Rec line | — | y=6.62 | Blue horizontal rule |
| Rec text | 0.55, y=6.68 | 12.23, h=0.72 | Bold blue label + italic black |
