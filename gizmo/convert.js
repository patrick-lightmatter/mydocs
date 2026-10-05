// Convert the program's markdown-formatted spec text into a real .docx
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, AlignmentType, Header, Footer, PageNumber,
  LevelFormat, ShadingType, BorderStyle, ImageRun,
} = require('docx');
const path = require('path');

const [,, inPath, outPath] = process.argv;
let text = fs.readFileSync(inPath, 'utf8');

const PAGE_W = 12240, PAGE_H = 15840, MARGIN = 1080; // US Letter, 0.75" margins
const CONTENT_W = PAGE_W - 2 * MARGIN; // 10080 DXA

// ---------- pre-processing ----------
let lines = text.split('\n');

// Drop leading "Table of Contents" artifact line
while (lines.length && lines[0].trim() === '') lines.shift();
if (lines.length && lines[0].trim() === 'Table of Contents') {
  lines.shift();
  while (lines.length && lines[0].trim() === '') lines.shift();
}

// Detect a page-header line: first non-empty line, plain text containing " | ", not a heading/table
let headerText = null;
if (lines.length && /\s\|\s/.test(lines[0]) && !/^[#|*]/.test(lines[0].trim())) {
  headerText = lines.shift().trim();
}

// Strip trailing header/footer remnants: lines ending in "Page" or "Page of"
let footerText = null;
while (lines.length) {
  let last = lines[lines.length - 1].trim();
  if (last === '') { lines.pop(); continue; }
  const m = last.match(/^(.*\|\s*)Page(\s+of)?$/);
  if (m) {
    if (m[2] || footerText === null) footerText = m[1]; // prefer the "Page of" variant
    lines.pop();
    continue;
  }
  break;
}

// ---------- inline formatting ----------
function unescapeMd(s) {
  return s.replace(/\\([\\`*_{}\[\]()#+\-.!|])/g, '$1');
}
function inlineRuns(s, extra = {}) {
  const runs = [];
  const parts = s.split(/(\*\*.+?\*\*|\*[^*]+?\*)/g);
  for (const p of parts) {
    if (!p) continue;
    if (/^\*\*.+\*\*$/.test(p)) {
      runs.push(new TextRun({ text: unescapeMd(p.slice(2, -2)), bold: true, ...extra }));
    } else if (/^\*[^*]+\*$/.test(p)) {
      runs.push(new TextRun({ text: unescapeMd(p.slice(1, -1)), italics: true, ...extra }));
    } else {
      runs.push(new TextRun({ text: unescapeMd(p), ...extra }));
    }
  }
  return runs;
}

// ---------- block parsing ----------
const children = [];
const HEADING = { 1: HeadingLevel.HEADING_1, 2: HeadingLevel.HEADING_2, 3: HeadingLevel.HEADING_3, 4: HeadingLevel.HEADING_4 };

function parseTableRow(line) {
  let cells = line.split('|');
  if (cells.length && cells[0].trim() === '') cells.shift();
  if (cells.length && cells[cells.length - 1].trim() === '') cells.pop();
  return cells.map(c => c.trim());
}
function isSeparatorRow(cells) {
  return cells.length > 0 && cells.every(c => /^:?-{2,}:?$/.test(c) || c === '---');
}

function buildTable(rows) {
  const nCols = Math.max(...rows.map(r => r.length));
  let colWidths;
  if (nCols === 2) colWidths = [Math.round(CONTENT_W * 0.3), CONTENT_W - Math.round(CONTENT_W * 0.3)];
  else {
    const w = Math.floor(CONTENT_W / nCols);
    colWidths = Array(nCols).fill(w);
    colWidths[nCols - 1] = CONTENT_W - w * (nCols - 1);
  }
  const tableRows = rows.map((cells, ri) => {
    while (cells.length < nCols) cells.push('');
    return new TableRow({
      tableHeader: ri === 0,
      children: cells.map((c, ci) => new TableCell({
        width: { size: colWidths[ci], type: WidthType.DXA },
        shading: ri === 0 ? { type: ShadingType.CLEAR, fill: 'DCE6F1' } : undefined,
        margins: { top: 40, bottom: 40, left: 80, right: 80 },
        children: [new Paragraph({
          children: inlineRuns(c, { size: 18 }),
          spacing: { before: 0, after: 0 },
        })],
      })),
    });
  });
  return new Table({
    columnWidths: colWidths,
    width: { size: CONTENT_W, type: WidthType.DXA },
    rows: tableRows,
  });
}

let i = 0;
while (i < lines.length) {
  const raw = lines[i];
  const line = raw.trim();

  if (line === '') { i++; continue; }

  // Table block
  if (line.startsWith('|')) {
    const rows = [];
    while (i < lines.length && lines[i].trim().startsWith('|')) {
      const cells = parseTableRow(lines[i].trim());
      if (!isSeparatorRow(cells)) rows.push(cells);
      i++;
    }
    if (rows.length) children.push(buildTable(rows));
    children.push(new Paragraph({ children: [], spacing: { after: 80 } }));
    continue;
  }

  // Heading
  const h = line.match(/^(#{1,4})\s+(.*)$/);
  if (h) {
    const level = h[1].length;
    const headingText = h[2];
    children.push(new Paragraph({
      heading: HEADING[level],
      children: inlineRuns(headingText),
      spacing: { before: level === 1 ? 320 : 240, after: 120 },
    }));
    i++;
    continue;
  }

  // Bullet
  const b = line.match(/^[-•]\s+(.*)$/);
  if (b) {
    children.push(new Paragraph({
      children: inlineRuns(b[1]),
      numbering: { reference: 'bullets', level: 0 },
      spacing: { after: 60 },
    }));
    i++;
    continue;
  }

  // Image: ![alt text](file.png) — centred, scaled to the content width
  const im = line.match(/^!\[([^\]]*)\]\(([^)]+)\)$/);
  if (im) {
    const alt = im[1], ref = im[2];
    const candidates = [ref, path.join(path.dirname(inPath), ref), path.join('/mnt/user-data/outputs', ref)];
    const found = candidates.find(p => fs.existsSync(p));
    if (!found) throw new Error('image not found: ' + ref);
    const data = fs.readFileSync(found);
    const pxW = data.readUInt32BE(16), pxH = data.readUInt32BE(20);   // PNG IHDR
    const maxW = Math.round(CONTENT_W / 15);                            // DXA -> px at 96 dpi (7.0 in = 672 px)
    const scale = Math.min(1, maxW / pxW);
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 60, after: 120 },
      children: [new ImageRun({
        type: 'png', data,
        transformation: { width: Math.round(pxW * scale), height: Math.round(pxH * scale) },
        altText: { title: alt, description: alt, name: alt },
      })],
    }));
    i++;
    continue;
  }

  // Plain paragraph
  children.push(new Paragraph({
    children: inlineRuns(line),
    spacing: { after: 120 },
  }));
  i++;
}

// ---------- header / footer ----------
const headers = headerText ? {
  default: new Header({
    children: [new Paragraph({
      children: [new TextRun({ text: headerText, size: 16, color: '595959' })],
      alignment: AlignmentType.RIGHT,
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: 'BFBFBF' } },
    })],
  }),
} : undefined;

const footers = footerText ? {
  default: new Footer({
    children: [new Paragraph({
      children: [
        new TextRun({ text: footerText, size: 16, color: '595959' }),
        new TextRun({ text: 'Page ', size: 16, color: '595959' }),
        new TextRun({ children: [PageNumber.CURRENT], size: 16, color: '595959' }),
        new TextRun({ text: ' of ', size: 16, color: '595959' }),
        new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 16, color: '595959' }),
      ],
      alignment: AlignmentType.CENTER,
    })],
  }),
} : undefined;

const doc = new Document({
  features: { updateFields: true },
  styles: {
    default: {
      document: { run: { font: 'Calibri', size: 22 } },
      heading1: { run: { font: 'Calibri', size: 32, bold: true, color: '1F3864' } },
      heading2: { run: { font: 'Calibri', size: 26, bold: true, color: '2E5395' } },
      heading3: { run: { font: 'Calibri', size: 24, bold: true, color: '2E5395' } },
      heading4: { run: { font: 'Calibri', size: 22, bold: true, italics: true, color: '2E5395' } },
    },
  },
  numbering: {
    config: [{
      reference: 'bullets',
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: '\u2022', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 360, hanging: 180 } } },
      }],
    }],
  },
  sections: [{
    properties: { page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } } },
    headers,
    footers,
    children,
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(outPath, buf);
  console.log('wrote', outPath, buf.length, 'bytes');
});
