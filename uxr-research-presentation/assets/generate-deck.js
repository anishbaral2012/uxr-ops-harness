#!/usr/bin/env node
/*
 * UXR findings deck template.
 *
 *   node generate-deck.js <deck-content.json> <output.pptx>
 *
 * The layout follows references/slide-specs.md. All study content comes from the JSON
 * file, so the same reviewed script renders every deck; change only the brand block
 * below. Quotations are wrapped in curly quotes and followed by their attribution
 * (participant, role, source ID and locator) so `uxrops check-report` can trace each
 * one back to the evidence ledger and source. See deck-content.example.json.
 *
 * Requires pptxgenjs (tested with 4.0.1). Resolve it from an approved local install,
 * for example: npm install --prefix <tools-folder> pptxgenjs@4.0.1 and set NODE_PATH.
 */
"use strict";

const fs = require("node:fs");
const path = require("node:path");

// ---- Brand block: replace with your organization's palette and font. -------------
const C = {
  navy: "002A86", blue: "0070F2", midBlue: "1B90FF", lightBlue: "89D1FF", paleBlue: "D1EFFF",
  red: "C00000", amber: "F0AB00", white: "FFFFFF", black: "000000", muted: "595959", border: "D9D9D9",
};
const FONT = "Calibri";
// ------------------------------------------------------------------------------------

const LM = 0.55;
const FULL = 12.23;
const CONTENT_Y = 1.69;
const PRIORITY_COLORS = { HIGH: C.red, MEDIUM: C.blue, EXPLORATORY: C.muted };

function fail(message) {
  console.error("deck-content error: " + message);
  process.exit(2);
}

function loadPptx() {
  try {
    return require("pptxgenjs");
  } catch (error) {
    fail("pptxgenjs is not installed. Install pptxgenjs@4.0.1 in an approved tools folder and set NODE_PATH.");
  }
}

function need(value, where, type = "string") {
  const ok = type === "array" ? Array.isArray(value) && value.length > 0
    : type === "object" ? value && typeof value === "object" && !Array.isArray(value)
      : typeof value === "string" && value.trim() !== "";
  if (!ok) fail(`${where} must be a nonempty ${type}.`);
  return value;
}

function validate(content) {
  need(content, "content", "object");
  const meta = need(content.meta, "meta", "object");
  ["title", "subtitle", "author", "date"].forEach(k => need(meta[k], `meta.${k}`));
  need(content.objective, "objective");
  need(content.research_questions, "research_questions", "array").forEach((rq, i) => {
    need(rq.id, `research_questions[${i}].id`); need(rq.question, `research_questions[${i}].question`);
  });
  need(content.methodology, "methodology", "array").forEach((row, i) => {
    if (!Array.isArray(row) || row.length !== 2) fail(`methodology[${i}] must be [label, detail].`);
  });
  const people = need(content.participants, "participants", "object");
  need(people.columns, "participants.columns", "array");
  need(people.rows, "participants.rows", "array").forEach((row, i) => {
    if (!Array.isArray(row) || row.length !== people.columns.length) fail(`participants.rows[${i}] must have ${people.columns.length} cells.`);
  });
  need(content.executive_summary, "executive_summary", "array").forEach((item, i) => {
    need(item.lead, `executive_summary[${i}].lead`); need(item.detail, `executive_summary[${i}].detail`);
  });
  need(content.themes, "themes", "array").forEach((theme, i) => {
    const where = `themes[${i}]`;
    need(theme.id, `${where}.id`); need(theme.headline, `${where}.headline`);
    need(theme.blocks, `${where}.blocks`, "array").forEach((b, j) => {
      need(b.label, `${where}.blocks[${j}].label`); need(b.text, `${where}.blocks[${j}].text`);
    });
    need(theme.callout, `${where}.callout`);
    (theme.quotes || []).forEach((q, j) => checkQuote(q, `${where}.quotes[${j}]`));
  });
  (content.opportunities || []).forEach((o, i) => ["title", "detail", "evidence"].forEach(k => need(o[k], `opportunities[${i}].${k}`)));
  (content.recommendations || []).forEach((r, i) => {
    need(r.action, `recommendations[${i}].action`); need(r.rationale, `recommendations[${i}].rationale`);
    need(r.theme_ids, `recommendations[${i}].theme_ids`, "array");
    if (!PRIORITY_COLORS[r.priority]) fail(`recommendations[${i}].priority must be HIGH, MEDIUM or EXPLORATORY.`);
  });
  (content.appendix || []).forEach((a, i) => {
    need(a.label, `appendix[${i}].label`); need(a.text, `appendix[${i}].text`);
    (a.quotes || []).forEach((q, j) => checkQuote(q, `appendix[${i}].quotes[${j}]`));
  });
  need(content.limitations, "limitations");
  return content;
}

function checkQuote(q, where) {
  ["text", "participant", "source_id", "locator"].forEach(k => need(q[k], `${where}.${k}`));
  if (/[“”"]/.test(q.text)) fail(`${where}.text must not include its own quotation marks.`);
}

function build(content, PptxGenJS) {
  const deck = new PptxGenJS();
  deck.layout = "LAYOUT_WIDE";
  deck.author = content.meta.author;
  deck.title = content.meta.title;
  deck.subject = content.meta.subtitle;
  deck.lang = content.meta.lang || "en-US";
  const footer = content.meta.footer || "";

  const text = (slide, value, x, y, w, h, options = {}) => slide.addText(value, {
    x, y, w, h, fontFace: FONT, fontSize: 14, margin: 0, valign: "top", color: C.black, wrap: true, ...options,
  });
  const line = (slide, x, y, w, h = 0, color = C.border, width = 1) =>
    slide.addShape(deck.ShapeType.line, { x, y, w, h, line: { color, width } });
  const rect = (slide, x, y, w, h, fill, outline = fill) =>
    slide.addShape(deck.ShapeType.rect, { x, y, w, h, fill: { color: fill }, line: { color: outline, width: 0.75 } });
  const label = (slide, value, x, y, w) => text(slide, value, x, y, w, 0.34, { color: C.blue, bold: true, fontSize: 16 });
  const callout = (slide, value, y = 6.48) => text(slide, value, LM, y, FULL, 0.4, { color: C.muted, italic: true, fontSize: 11 });

  function contentSlide(title, notes) {
    const slide = deck.addSlide();
    slide.background = { color: C.white };
    const h = title.length > 92 ? 0.74 : 0.4;
    text(slide, title, LM, 0.55, FULL, h, { color: C.navy, fontSize: 20, valign: "mid" });
    const underline = 0.55 + h + 0.05;
    line(slide, LM, underline, FULL, 0, C.blue, 1.5);
    if (footer) text(slide, footer, LM, 7.12, 6, 0.22, { fontSize: 10, color: C.muted });
    if (notes) slide.addNotes(notes);
    return { slide, underline };
  }

  function quote(slide, q, x, y, w) {
    // Size the box to the text (about 14 characters per inch at 11pt) so the attribution sits just below it.
    const value = "“" + q.text + "”";
    const h = Math.ceil(value.length / (w * 14)) * 0.2 + 0.08;
    text(slide, value, x, y, w, h, { italic: true, fontSize: 11 });
    const who = [q.participant, q.role].filter(Boolean).join(", ");
    text(slide, `${who}, ${q.source_id} ${q.locator}`, x, y + h + 0.02, w, 0.24, { color: C.muted, fontSize: 10 });
    return y + h + 0.32;
  }

  // Cover
  const cover = deck.addSlide();
  cover.background = { color: C.white };
  text(cover, content.meta.title, LM, 2.8, 11, 0.95, { fontSize: 36, bold: true, color: C.navy, valign: "mid" });
  text(cover, content.meta.subtitle, LM, 4.0, 10, 0.4, { fontSize: 16, color: C.blue });
  rect(cover, LM, 4.7, 0.04, 0.62, C.amber);
  text(cover, content.meta.author + "\n" + content.meta.date, LM + 0.17, 4.68, 8, 0.66, { fontSize: 12, color: C.muted });
  if (content.meta.distribution) {
    text(cover, content.meta.distribution, LM, 6.54, 10, 0.36, { fontSize: 12, bold: true, color: C.muted });
  }

  // Contents
  const sections = ["Objectives and methodology", "Participant overview", "Executive summary", "Findings"];
  if ((content.opportunities || []).length) sections.push("Opportunity areas");
  if ((content.recommendations || []).length) sections.push("Strategic recommendations");
  sections.push("Appendix and limitations");
  const contents = contentSlide("Contents").slide;
  contents.addTable(sections.map((section, i) => [
    { text: String(i + 1), options: { align: "center", fontSize: 24 } },
    { text: section, options: { fontSize: 18, color: C.navy, bold: i === 0, fill: i === 0 ? { color: C.midBlue } : { type: "none" } } },
  ]), { x: 0.39, y: 1.38, w: 12.54, colW: [1.09, 11.45], rowH: 0.68, fontFace: FONT, border: { type: "none" }, autoPage: false });

  // Objectives and methodology
  const method = contentSlide("Objectives and methodology", content.objectives_notes).slide;
  label(method, "Objectives", LM, CONTENT_Y, 5.8);
  text(method, content.objective, LM, CONTENT_Y + 0.44, 5.8, 0.95, { fontSize: 13 });
  label(method, "Research questions", LM, 3.2, 5.8);
  content.research_questions.slice(0, 6).forEach((rq, i) => {
    text(method, `${rq.id}  ${rq.question}`, LM, 3.64 + i * 0.48, 5.8, 0.44, { fontSize: 12 });
  });
  line(method, 6.65, CONTENT_Y, 0, 4.6);
  label(method, "Methodology", 7, CONTENT_Y, 5.78);
  content.methodology.slice(0, 8).forEach(([field, detail], i) => {
    const y = CONTENT_Y + 0.5 + i * 0.5;
    text(method, field, 7, y, 1.6, 0.4, { bold: true, color: C.blue, fontSize: 12 });
    text(method, detail, 8.7, y, 4.08, 0.4, { fontSize: 12 });
    line(method, 7, y + 0.42, 5.78);
  });
  if (content.methodology_note) callout(method, content.methodology_note);

  // Participants
  const people = contentSlide("Participant overview", content.participants.notes).slide;
  const header = value => ({ text: value, options: { bold: true, color: C.white, fill: { color: C.blue }, fontSize: 13 } });
  people.addTable([content.participants.columns.map(header), ...content.participants.rows.map(r => r.map(String))], {
    x: LM, y: CONTENT_Y, w: FULL, rowH: 0.5, fontSize: 11.5, fontFace: FONT, autoPage: false,
    border: { type: "solid", color: C.border, pt: 1 },
  });
  if (content.participants.note) callout(people, content.participants.note);

  // Executive summary
  const summary = contentSlide("Executive summary", content.summary_notes).slide;
  content.executive_summary.slice(0, 5).forEach((item, i) => {
    const y = CONTENT_Y + i * 0.9;
    summary.addShape(deck.ShapeType.ellipse, { x: LM, y: y + 0.12, w: 0.12, h: 0.12, fill: { color: C.blue }, line: { color: C.blue } });
    text(summary, [{ text: item.lead + " ", options: { bold: true, color: C.blue } }, { text: item.detail }],
      LM + 0.26, y, FULL - 0.26, 0.7, { fontSize: 14 });
  });
  if (content.summary_note) callout(summary, content.summary_note, 6.6);

  // Insight slides
  content.themes.forEach((theme, index) => {
    const { slide, underline } = contentSlide(theme.headline, theme.notes);
    text(slide, `${theme.id} · Theme ${index + 1} of ${content.themes.length}`, 9.5, underline - 0.26, 3.28, 0.2,
      { fontSize: 10, color: C.muted, align: "right" });
    const top = underline + 0.35;
    theme.blocks.slice(0, 4).forEach((block, i) => {
      const y = top + i * 1.12;
      label(slide, block.label, LM, y, 7.6);
      text(slide, block.text, LM + 0.1, y + 0.38, 7.5, 0.7, { fontSize: 13 });
    });
    let y = top;
    (theme.quotes || []).slice(0, 3).forEach(q => { y = quote(slide, q, 8.45, y, 4.33); });
    if (theme.recommendation) {
      line(slide, LM, 6.0, FULL, 0, C.blue, 1);
      text(slide, [{ text: "Design recommendation: ", options: { bold: true, color: C.blue } },
        { text: theme.recommendation, options: { italic: true } }], LM, 6.05, FULL, 0.4, { fontSize: 12 });
    }
    callout(slide, theme.callout, 6.55);
  });

  // Opportunity areas: 2x2 cards
  if ((content.opportunities || []).length) {
    const slide = contentSlide("Opportunity areas", content.opportunities_notes).slide;
    content.opportunities.slice(0, 4).forEach((o, i) => {
      const x = i % 2 === 0 ? LM : 7.0;
      const y = i < 2 ? CONTENT_Y : 4.45;
      const w = 5.85;
      rect(slide, x, y, w, 2.6, C.white, C.border);
      rect(slide, x, y, 0.06, 2.6, C.blue);
      text(slide, o.title, x + 0.18, y + 0.12, w - 0.3, 0.34, { fontSize: 13, bold: true, color: C.navy });
      text(slide, o.detail, x + 0.18, y + 0.5, w - 0.3, 0.95, { fontSize: 10.5 });
      text(slide, o.evidence, x + 0.18, y + 1.5, w - 0.3, 0.3, { fontSize: 9.5, italic: true, color: C.muted });
      (o.directions || []).slice(0, 2).forEach((d, j) => {
        text(slide, "→  " + d, x + 0.18, y + 1.85 + j * 0.34, w - 0.3, 0.3, { fontSize: 10, color: C.blue });
      });
    });
  }

  // Strategic recommendations
  if ((content.recommendations || []).length) {
    const slide = contentSlide("Strategic recommendations", content.recommendations_notes).slide;
    text(slide, content.recommendations_caveat || "Proposals for review; each names the findings it rests on.",
      LM, CONTENT_Y, FULL, 0.34, { italic: true, color: C.muted, fontSize: 11 });
    const order = { HIGH: 0, MEDIUM: 1, EXPLORATORY: 2 };
    [...content.recommendations].sort((a, b) => order[a.priority] - order[b.priority]).slice(0, 5).forEach((r, i) => {
      const y = CONTENT_Y + 0.5 + i * 0.86;
      rect(slide, LM, y + 0.05, 1.45, 0.36, PRIORITY_COLORS[r.priority]);
      text(slide, r.priority, LM, y + 0.05, 1.45, 0.36, { align: "center", valign: "mid", bold: true, fontSize: 9.5, color: C.white });
      text(slide, r.action, 2.2, y, 10.58, 0.36, { fontSize: 12, bold: true, color: C.navy });
      text(slide, `${r.theme_ids.join(", ")}. ${r.rationale}`, 2.2, y + 0.36, 10.58, 0.38, { fontSize: 10.5 });
      line(slide, LM, y + 0.8, FULL, 0, "E8E8E8");
    });
  }

  // Appendix and limitations
  const appendix = contentSlide("Appendix and limitations", content.appendix_notes).slide;
  let y = CONTENT_Y;
  (content.appendix || []).slice(0, 3).forEach(item => {
    rect(appendix, LM, y + 0.03, 1.45, 0.32, C.paleBlue);
    text(appendix, item.label, LM, y + 0.03, 1.45, 0.32, { align: "center", valign: "mid", bold: true, fontSize: 9.5, color: C.blue });
    text(appendix, item.text, 2.2, y, 10.58, 0.4, { fontSize: 12, bold: true, color: C.navy });
    y += 0.5;
    (item.quotes || []).slice(0, 1).forEach(q => { y = quote(appendix, q, 2.2, y, 10.58); });
    y += 0.1;
  });
  if (y > CONTENT_Y) y += 0.2;
  label(appendix, "Scope of the evidence", LM, y, FULL);
  text(appendix, content.limitations, LM, y + 0.42, FULL, 1.2, { fontSize: 12 });

  return deck;
}

function main(argv) {
  if (argv.length !== 2) {
    console.error("Usage: node generate-deck.js <deck-content.json> <output.pptx>");
    process.exit(2);
  }
  const [input, output] = argv.map(p => path.resolve(p));
  let content;
  try {
    content = JSON.parse(fs.readFileSync(input, "utf8").replace(/^﻿/, ""));  // tolerate a Windows BOM
  } catch (error) {
    fail(`cannot read ${input}: ${error.message}`);
  }
  const deck = build(validate(content), loadPptx());
  return deck.writeFile({ fileName: output })
    .then(file => console.log("Wrote " + file))
    .catch(error => { console.error(error); process.exitCode = 1; });
}

if (require.main === module) main(process.argv.slice(2));

module.exports = { build, validate };
