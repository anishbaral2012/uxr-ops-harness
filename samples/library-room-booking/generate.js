const fs = require("node:fs");
const path = require("node:path");
const PptxGenJS = require("pptxgenjs");

function readJson(file) {
  return JSON.parse(fs.readFileSync(path.join(__dirname, file), "utf8"));
}

const manifest = readJson("study-manifest.json");
const ledger = readJson("evidence-ledger.json");
const sources = new Map(manifest.sources.map(source => [source.id, source]));
const participantCount = new Set(manifest.sources.map(source => source.participant_id)).size;
const deck = new PptxGenJS();
deck.layout = "LAYOUT_WIDE";
deck.author = "Demo research team";
deck.subject = "Synthetic UX research study";
deck.title = "Library room booking";
deck.lang = "en-US";

const C = {
  navy: "002A86", blue: "0070F2", midBlue: "1B90FF", paleBlue: "D1EFFF",
  red: "C00000", amber: "F0AB00", white: "FFFFFF", black: "000000",
  muted: "595959", border: "D9D9D9",
};
const LM = 0.55;
const FULL = 12.23;
const FONT = "Calibri";

function text(slide, content, x, y, w, h, options = {}) {
  slide.addText(content, {
    x, y, w, h, fontFace: FONT, fontSize: 14, margin: 0, valign: "mid",
    color: C.black, wrap: true, ...options,
  });
}

function rule(slide, x, y, w, h = 0, color = C.border, width = 1) {
  slide.addShape(deck.ShapeType.line, { x, y, w, h, line: { color, width } });
}

function rect(slide, x, y, w, h, fill, outline = fill) {
  slide.addShape(deck.ShapeType.rect, {
    x, y, w, h, fill: { color: fill }, line: { color: outline, width: 0.75 },
  });
}

function sectionTitle(slide, title) {
  const h = title.length > 92 ? 0.74 : 0.4;
  text(slide, title, LM, 0.55, FULL, h, { color: C.navy, fontSize: 20 });
  return 0.55 + h + 0.05;
}

function contentSlide(title, notes) {
  const slide = deck.addSlide();
  slide.background = { color: C.white };
  titleUnderline(slide, sectionTitle(slide, title));
  text(slide, "Synthetic study", LM, 7.17, 4, 0.18, { fontSize: 10, color: C.muted });
  if (notes) slide.addNotes(notes);
  return slide;
}

function titleUnderline(slide, y) {
  rule(slide, LM, y, FULL, 0, C.blue, 1.5);
}

function label(slide, heading, x, y, w) {
  text(slide, heading, x, y, w, 0.34, { color: C.blue, bold: true, fontSize: 16 });
}

function callout(slide, message, y = 6.48) {
  text(slide, message, LM, y, FULL, 0.4, { color: C.muted, italic: true, fontSize: 11 });
}

function quote(slide, item, x, y, width) {
  const attribution = sources.get(item.source_id).participant_id;
  text(slide, '“' + item.quote + '”', x, y, width, 0.76, { italic: true, fontSize: 11, valign: "top" });
  text(slide, attribution + ", organizer, " + item.source_id + " " + item.locator, x, y + 0.78, width, 0.24,
    { color: C.muted, fontSize: 10 });
}

const cover = deck.addSlide();
cover.background = { color: C.white };
text(cover, "Library room booking", LM, 2.93, 9.5, 0.82, { fontSize: 36, bold: true, color: C.navy });
text(cover, "Discovery research exercise", LM, 4.1, 7.5, 0.4, { fontSize: 16, color: C.blue });
rect(cover, LM, 4.7, 0.04, 0.62, C.amber);
text(cover, "Demo research team\n20 November 2026", LM + 0.17, 4.68, 6, 0.66, { fontSize: 12, color: C.muted });
text(cover, "Synthetic participants and evidence", LM, 6.54, 7.5, 0.36, { fontSize: 12, bold: true, color: C.muted });

const contents = contentSlide("Contents");
const sections = [
  "Objectives and methodology", "Participant overview", "Executive summary",
  "Findings", "Opportunity areas", "Strategic recommendations", "Appendix",
];
contents.addTable(sections.map((section, i) => [
  { text: String(i + 1), options: { align: "center", fontSize: 24 } },
  { text: section, options: {
    fontSize: 18, color: C.navy, bold: i === 0, fill: i === 0 ? { color: C.midBlue } : { type: "none" },
  } },
]), {
  x: 0.39, y: 1.38, w: 12.54, colW: [1.09, 11.45], rowH: 0.68,
  fontFace: FONT, border: { type: "none" }, autoPage: false,
});

const method = contentSlide("Objectives and methodology", "Source: Research Plan for Library Room Booking.");
label(method, "Objectives", LM, 1.69, 5.8);
text(method, "Decide what the first mobile prototype should show during search, room selection and confirmation.", LM, 2.15, 5.8, 0.74);
label(method, "Research questions", LM, 3.16, 5.8);
[
  "What do organizers settle first when searching?",
  "What room information matters before booking?",
  "How do organizers confirm and share the plan?",
].forEach((question, i) => {
  text(method, "RQ" + (i + 1) + "  " + question, LM, 3.63 + i * 0.49, 5.8, 0.38, { fontSize: 13 });
});
rule(method, 6.65, 1.69, 0, 4.35);
label(method, "Methodology", 7, 1.69, 5.78);
const attributes = [
  ["Research type", "Discovery interviews"], ["Format", "Remote, moderated"],
  ["Duration", "30 minutes planned"], ["Sessions", manifest.sources.length + " sources across " + participantCount + " organizers"],
  ["Dates", "17 and 18 November 2026"], ["Recruitment", "Fictional roles and booking attempts"],
  ["Scope", "Recent study room booking attempts"],
];
attributes.forEach(([field, detail], i) => {
  const y = 2.2 + i * 0.49;
  text(method, field, 7, y, 1.6, 0.38, { bold: true, color: C.navy, fontSize: 12 });
  text(method, detail, 8.7, y, 4.05, 0.38, { fontSize: 12 });
  rule(method, 7, y + 0.4, 5.78);
});
callout(method, "The accounts can illustrate research decisions. A prototype test would be needed to observe task completion.");

const people = contentSlide("Participant overview", "Source: study-manifest.json and transcript context lines.");
const header = heading => ({
  text: heading, options: { bold: true, color: C.white, fill: { color: C.blue }, fontSize: 14 },
});
const context = [
  ["First attempt", "Mobile web, then phone"], ["Repeat organizer", "Phone"],
  ["First attempt", "Service desk"], ["Repeat organizer", "Service desk"],
  ["Repeat organizer", "Mobile web"], ["First attempt", "Mobile web, then phone"],
];
const participantRows = manifest.participants.map((id, i) => [
  id, ...context[i], manifest.sources.filter(source => source.participant_id === id).map(source => source.id).join(", "),
]);
people.addTable([
  ["Participant", "Experience", "Booking channel", "Sources"].map(header), ...participantRows,
], {
  x: LM, y: 1.69, w: FULL, colW: [1.55, 3.18, 4.5, 3], rowH: 0.56,
  fontSize: 13, fontFace: FONT, autoPage: false, border: { type: "solid", color: C.border },
});
callout(people, "Six fictional organizers. The follow up with P6 adds one source and leaves the participant count at six.");

const summary = contentSlide("Executive summary", "Sources: analysis.md and evidence-ledger.json, T1 through T3.");
const summaryRows = [
  ["Two ways into search. ", "Three organizers fixed the time first. Three chose the branch and could shift the time."],
  ["Room details matter when there is a specific need. ", "Four checked capacity, equipment or access before booking."],
  ["Staff filled gaps in web information. ", "Two mobile web users called the branch to ask about capacity."],
  ["A booking detail can help the group meet. ", "Four reused a detail from staff or a confirmation."],
];
summaryRows.forEach(([lead, detail], i) => {
  const y = 1.69 + i * 0.94;
  summary.addShape(deck.ShapeType.ellipse, {
    x: LM, y: y + 0.23, w: 0.12, h: 0.12, fill: { color: C.blue }, line: { color: C.blue },
  });
  text(summary, [{ text: lead, options: { bold: true, color: C.blue } }, { text: detail }],
    LM + 0.26, y, FULL - 0.26, 0.58, { fontSize: 14 });
});
callout(summary, "Counts describe six synthetic accounts. All six discussed the three topics.");

const insightCopy = [
  {
    pattern: "P1, P3 and P5 had a fixed meeting window and considered where it could fit.",
    boundary: "P2, P4 and P6 chose a branch for travel reasons and could shift the time.",
    meaning: "Both constraints need a place at the start of a search.",
    quotes: ["S01", "S02"],
  },
  {
    pattern: "P1 and P6 called about capacity. P2 asked about a whiteboard. P4 checked for a route without stairs.",
    boundary: "P3 took a staff suggestion. P5 already knew the room and skipped the details.",
    meaning: "Room information can affect the choice before a booking is made.",
    quotes: ["S06", "S04"],
  },
  {
    pattern: "P1, P2, P3 and P6 reused booking details when they told others where to go.",
    boundary: "P4 told a group that was already present. P5 sent a short update because the group knew the room.",
    meaning: "The group may need different details from the person who made the booking.",
    quotes: ["S01", "S03"],
  },
];

ledger.themes.forEach((theme, index) => {
  const copy = insightCopy[index];
  const slide = contentSlide(theme.claim, theme.id + ". " + theme.counter_evidence + " See analysis.md and evidence-ledger.json.");
  text(slide, "Theme " + (index + 1) + " of " + ledger.themes.length, 10.15, 0.8, 2.63, 0.18,
    { fontSize: 10, color: C.muted, align: "right" });
  const blocks = [
    ["Pattern", copy.pattern],
    ["Other cases", copy.boundary],
    ["Implication", copy.meaning],
  ];
  blocks.forEach(([heading, detail], i) => {
    const y = 1.69 + i * 1.17;
    label(slide, heading, LM, y, 7.32);
    text(slide, detail, LM + 0.1, y + 0.38, 7.22, 0.58, { fontSize: 13, valign: "top" });
  });
  copy.quotes.forEach((id, i) => {
    quote(slide, theme.evidence.find(item => item.source_id === id), 8.45, 1.82 + i * 1.32, 4.3);
  });
  callout(slide, theme.id + "   " + theme.supporting_participants.length + " of " + participantCount +
    " accounts fit the pattern. All six discussed the topic.");
});

const opportunities = contentSlide("Opportunity areas", "Source: analysis.md opportunity areas, T1 and T2, and T2 and T3.");
[
  ["Search by either constraint",
    "Some organizers had a time locked in. Others needed to stay at a particular branch. Both groups still had to find a room that fit.",
    "Evidence from T1 and T2",
    "Explore entry points for time and branch."],
  ["Room details from choice to arrival",
    "Capacity, equipment and access can affect the booking. The branch, floor or entrance helps people find the room afterward.",
    "Evidence from T2 and T3 and the P6 follow up",
    "Explore which details belong at each step."],
].forEach(([heading, detail, signal, direction], i) => {
  const x = i === 0 ? LM : 7;
  const y = 1.69;
  const w = 5.78;
  rect(opportunities, x, y, w, 2.65, C.white, C.border);
  rect(opportunities, x, y, 0.06, 2.65, C.blue);
  text(opportunities, heading, x + 0.18, y + 0.15, w - 0.36, 0.36, { fontSize: 15, bold: true, color: C.navy });
  text(opportunities, detail, x + 0.18, y + 0.62, w - 0.36, 0.72, { fontSize: 13, valign: "top" });
  text(opportunities, signal, x + 0.18, y + 1.49, w - 0.36, 0.3, { fontSize: 11, italic: true, color: C.muted });
  text(opportunities, direction, x + 0.18, y + 1.94, w - 0.36, 0.38, { fontSize: 12, color: C.navy, bold: true });
});

const recommendations = contentSlide("Strategic recommendations", "Source: analysis.md, Strategic Recommendations.");
text(recommendations, "Prototype proposals for the fictional scenario", LM, 1.69, FULL, 0.36,
  { italic: true, color: C.muted, fontSize: 11 });
[
  ["HIGH", "Search can start with time or branch", "T1. Compare both search paths in a prototype test."],
  ["HIGH", "Room details appear before booking", "T2. Confirm what staff can maintain, then test whether people find capacity, equipment and access."],
  ["MEDIUM", "The confirmation includes a summary people can copy", "T3. Test what a recipient can tell from the branch, room, floor, date and time."],
].forEach(([priority, action, reason], i) => {
  const y = 2.2 + i * 0.96;
  const color = priority === "HIGH" ? C.red : C.blue;
  rect(recommendations, LM, y + 0.07, 1.32, 0.36, color);
  text(recommendations, priority, LM, y + 0.07, 1.32, 0.36, { align: "center", bold: true, fontSize: 10, color: C.white });
  text(recommendations, action, 2.08, y + 0.03, 10.7, 0.37, { fontSize: 14, color: C.navy, bold: true });
  text(recommendations, reason, 2.08, y + 0.4, 10.7, 0.38, { fontSize: 12 });
  rule(recommendations, LM, y + 0.85, FULL);
});

const appendix = contentSlide("Appendix", "Sources: analysis.md, Appendix Insights and Gaps and Limitations. Transcript S07 line 3.");
const followup = sources.get("S07");
const entranceQuote = fs.readFileSync(path.join(__dirname, followup.path), "utf8").split(/\r?\n/)[2].split(": ")[1];
label(appendix, "Entrance details", LM, 1.69, FULL);
text(appendix, "Only P6 was asked what happened after the organizer sent the room and time.", LM, 2.17, FULL, 0.47);
quote(appendix, { source_id: "S07", locator: "line 3", quote: entranceQuote }, LM, 2.82, 10.9);
label(appendix, "Scope of the evidence", LM, 4.19, FULL);
text(appendix, "Fictional accounts cover three booking channels. Staff workflows, prototype task completion and the accuracy of live availability remain unexplored.",
  LM, 4.66, 11.6, 0.85, { valign: "top" });

deck.writeFile({ fileName: path.join(__dirname, "research-report.pptx") })
  .then(file => console.log("Wrote " + file))
  .catch(error => { console.error(error); process.exitCode = 1; });
