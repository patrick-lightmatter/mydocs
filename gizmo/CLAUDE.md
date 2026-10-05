# OCI 106G SerDes — Companion Design Spec Set (working instructions for Claude)

This folder holds the markdown sources for the OCI 106G line-side SerDes chiplet
companion design specifications. In this environment you edit these `.md` files
**in place** — there is no import/export or reupload step. Edit the file, save it,
done.

## Files in this set

| File | Document | Rev |
|---|---|---|
| `OCI_106G_SerDes_Architecture_Spec_Rev0p7.md` | **Architecture and Requirements Specification (parent / hub)** | 0.7 |
| `DES-OCI-106G-RXF-001_RX_Front_End_Design_Spec_Rev0p2.md` | RX Analog Front End (TIA, CTLE, AGC, slicer interface) | 0.2 |
| `DES-OCI-106G-TXD-001_TX_Driver_Design_Spec_Rev0p2.md` | TX Pre-Driver and Driver | 0.2 |
| `DES-OCI-106G-ADP-001_Adaptation_Loops_Design_Spec_Rev0p2.md` | Receive Digital Adaptation Loops | 0.2 |
| `DES-OCI-106G-CLK-001_Clocking_Design_Spec_Rev0p2.md` | Clock Generation, Distribution, Phase Interpolation | 0.2 |
| `DES-OCI-106G-EYM-001_RX_Eye_Monitor_Design_Spec_Rev0p2.md` | RX Eye Monitor | 0.2 |
| `DES-OCI-106G-SQL-001_TX_Squelch_Design_Spec_Rev0p2.md` | TX Squelch and Loss-of-Modulation | 0.2 |
| `DES-OCI-106G-JIT-001_TP1_Jitter_Budget_Rev0p3.md` | TP1 Electrical Jitter Budget | 0.3 |

`figures/` holds figure images and the scripts that generate them. `convert.js`
renders any `.md` in this set to a real Word `.docx` when a Word deliverable is
needed (see "Producing Word output" below).

`OCI_106G_SerDes_Architecture_Spec_Rev0p7.md` is the **parent / hub** specification
(Rev 0.7). The companion design specs decompose its requirements; where a companion
and the architecture spec differ, the architecture spec governs. It carries the
FAMILY-NNN requirement IDs (SYS-, DRX-, ELE-, CDR-, …) that every companion cites.
It does **not** contain block diagrams by convention — its §3 holds a prose
signal-chain description — so do not add figures to it unless the user explicitly
asks. It is edited in place like the others.

The change list, the doc-structure template, the coverage review, and the superseded
SQL Rev 0.1 are **not** in this folder and are not edited here.

## Document conventions (follow these when editing)

1. **Format.** These are plain-markdown documents: `#`/`##`/`###` headings,
   GitHub-style pipe tables, `**bold**` and `*italic*` inline. The first line of
   each file is a running-header line (`DOC-ID Rev x | Companion to … | … Spec`)
   and the last line is a running-footer line (`DOC-ID Rev x | DRAFT | Page of`);
   leave both in place — the Word converter turns them into the real header/footer.

2. **Numbering.** Sections are `# N.`, subsections `## N.M`, and tables are
   captioned `**Table N-M. <title>**` with chapter-sequential numbering. When you
   **insert or remove a subsection**, renumber the subsequent `## N.M` headings in
   that section *and* fix every internal cross-reference to them (prose "Section
   N.M", the "Section" column of the Table 1-1 requirement map, and any
   "(Section N.M)" pointers). When you **insert or remove a table**, renumber the
   later tables in that chapter and every "Table N-M" reference to them, including
   references from *other* files in the set.

3. **Figures.** A figure is a `## N.M Block diagram` (or similar) subsection with a
   bold `**Figure N-M. <title>**` caption line. Two forms occur:
   - **Placeholder** (not yet drawn): an italic
     `*\[FIGURE PLACEHOLDER — insert … here. Suggested content: …\]*` paragraph
     describing the figure in enough detail to draw it — every block (by table-row
     number), every signal on every arrow, control/gate inputs, data-flow
     direction, and the defining table.
   - **Rendered**: a markdown image
     `![caption](figures/<name>.png)` followed by a short italic key line.
     `RXF-001 §2.2` is in this rendered form; the other nine figures across the set
     are still placeholders.
   To turn a placeholder into a real figure, generate the PNG into `figures/`
   (keep a generator script alongside it, as `figures/RXF-001_Figure_2-1_source.py`
   shows), then replace the placeholder paragraph with the image line + key.

4. **Revision discipline.** Do **not** bump the `Revision` field or add a
   revision-history row for routine edits like adding a figure or fixing a
   cross-reference. Only change the revision block when the user explicitly asks
   for a new revision.

5. **Cross-file consistency.** The specs cite each other ("DES-OCI-106G-CLK-001
   Section 8", "RXF Table 8-3", etc.), and the architecture spec cites the
   companions (e.g. "DES-OCI-106G-CLK-001 Section 2.3"). After any renumbering, grep
   the whole set — architecture spec included — for references to the thing you
   moved and update them everywhere, not just in the file you edited. (The
   architecture spec's references to CLK-001 §2.x were already corrected to the
   post-figure-insertion numbering: §2.3 Frequency plan, §2.5 Architecture decisions.)

## Producing Word output (only when asked)

The specs live as markdown. When the user wants a Word deliverable, render with the
bundled converter (requires Node and the `docx` package):

```
node convert.js <file>.md <output>.docx
```

The converter reads the running-header/footer lines, renders the pipe tables,
embeds any `![](figures/…png)` images scaled to the text width, and applies the
house styling (Calibri, navy headings, US-Letter 0.75" margins). It does **not**
modify the markdown. Regenerate only the files you changed.

## What NOT to do

- Don't add or remove a Contents section (the set has none by convention).
- Don't edit the change list, the template, the coverage review, or the superseded
  SQL Rev 0.1 — none are in this folder.
- Don't add block diagrams to the architecture spec (`OCI_106G_SerDes_Architecture_Spec_Rev0p7.md`)
  unless explicitly asked; figures belong in the companion specs.
- Don't reflow or re-wrap unrelated paragraphs when making a small edit; keep diffs
  minimal so review is easy.
