# Per-paper instructions (sub-agent)

You are preparing **one** journal club paper for a urology resident. They have **10 minutes** to present it and will speak from bullets. Your output is a .docx outline. **Accuracy matters above everything.** Every number in the outline must be traceable to the paper.

Scripts: `~/.claude/skills/journal_club_presentation/scripts/`
Template being filled in: `~/.claude/skills/journal_club_presentation/reference/template.md`

## Step 1: Read the whole paper carefully

- Read every page with the Read tool (`pages` param, ≤ 20 pages per call). That includes tables, figure legends, supplementary notes, and any **editorial comments** at the end, since editorials often hold the best critique and context.
- Note exact numbers: n, percentages with numerators/denominators, CIs, p-values, HRs, follow-up, dates, doses.
- Where the text and figures/tables can be cross-checked, do it (e.g., recount events on a swimmer plot, add up rows in a table). If the text seems garbled or ambiguous (OCR artifacts, typos), say so instead of guessing.

## Step 2: Write the content (JSON spec for `build_docx.py`)

Follow the template order and these rules:

**Style**
- **Bullets only.** No full paragraphs. Fragments are fine. **Bold** the number or phrase the presenter will say out loud.
- Short: one line per bullet when possible, rarely more than two. Use sub-bullets (`{"text": ..., "sub": [...]}`) to break up anything longer.
- Spell out an abbreviation only if a urology audience wouldn't know it.
- Put a time budget on the top-level sections (`"time"` field). Default: Background ~1 min, Methods ~2.5 min, Results ~5 min, Limitations + final comments ~1.5 min.

**Sections**
1. **Header:** title, lead author (+ senior author), institution, journal with year/volume/pages.
2. **Background** (3-5 bullets): why the authors did this study. Standard of care, the gap, key benchmark numbers from prior work.
3. **Objective** (1-2 bullets).
4. **Methods.** This is how the group judges validity, so be complete but terse. Sub-headings:
   - Study design & level of evidence: descriptive vs analytical, experimental vs observational, retrospective vs prospective, randomized or not. Give a level of evidence (Oxford CEBM) with a short justification.
   - Population: what, when, where, how; how the study and control groups were built (say plainly if there is **no control group**); the intervention/regimen.
   - Outcome definitions: exactly how each outcome was defined, **and what was excluded from the definition**.
   - Inclusion / exclusion.
   - Data collection & power: the actual power calculation, and **which endpoint it was powered for**.
5. **Results. This is the bulk of the talk.** Facts only, no speculation here.
   - Add one `h2` sub-section per key figure or table (usually 3-5). Put the **cropped figure first**, then 2-5 bullets on what it shows.
   - In the image, draw a **red box** around the part being discussed, labeled **A**, **B**, ... (see Step 3). Start bullets that refer to a box with **[A]** / **[B]** so the presenter can say "see Figure 2, box A".
   - The caption says what each box shows, e.g. `"Figure 1. Kaplan-Meier HG RFS. A = 24/36-mo landmarks; B = late drop"`.
   - Lead with the primary outcome, then secondary outcomes, then safety.
6. **Conclusion:** one sentence, as a `callout` block.
7. **Limitations**, two sub-headings:
   - "Acknowledged by the authors": the **1-2 most important** limitations the paper itself states.
   - "Not discussed in the paper": **1-2 sharp, original points** the authors did not raise. Make them specific and backed by the paper's own numbers (e.g., unpowered secondary endpoint with a wide CI, an outcome definition that flatters the result, attrition, control-group mismatch, a timing issue visible in a figure). No generic filler like "more studies needed".
   - Check against the template's shortcomings checklist (inclusion, exclusion, control group, data collection, bias, power) to find these, but **don't list every item**.
8. **Final comments / would I change practice?** 3-5 bullets: practical bottom line, ongoing trials that will answer the question, plus **2 discussion questions** for the group.

**JSON spec** (see the docstring in `scripts/build_docx.py`):
```json
{"output": "<given output path>",
 "header": {"title": "", "authors": "", "institution": "", "journal": ""},
 "blocks": [{"h1": "Results", "time": "~5 min"}, {"h2": "..."},
            {"figure": "<abs png>", "caption": "...", "width_in": 4.6},
            {"bullets": ["...", {"text": "...", "sub": ["..."]}]},
            {"callout": "..."}]}
```
Figure widths: ~4.5 in for plots, up to ~5.6 in for wide tables, ~3.6 in for narrow tables.

## Step 3: Crop figures and draw highlight boxes

All coordinates are **fractions of the full page** (0-1, origin top-left).

1. Make a grid preview of each page that has a figure/table you'll use, then view it with Read:
   ```bash
   python3 ~/.claude/skills/journal_club_presentation/scripts/figure_tool.py grid "<pdf>" <page> <workdir>/grid<page>.png
   ```
   PDF page numbers are physical pages (1 = first page of the file), not journal page numbers.
2. Crop and box:
   ```bash
   python3 ~/.claude/skills/journal_club_presentation/scripts/figure_tool.py crop "<pdf>" <page> <workdir>/fig1.png \
     --crop X0 Y0 X1 Y1 \
     --box X0 Y0 X1 Y1 --label A --pos right \
     --box X0 Y0 X1 Y1 --label B
   ```
   `--pos` is `above` (default), `below`, `left`, or `right`. Pick whichever keeps the label off the data.
3. **View every crop with Read** and fix it if: the crop cuts off axes, legends, or numbers-at-risk; a box misses or slices through the target; or a label covers data. Iterate until it's clean. Include the figure's legend inside the crop only when it's needed to read the figure.

## Step 4: Build and verify

```bash
python3 ~/.claude/skills/journal_club_presentation/scripts/build_docx.py <workdir>/outline.json
```

Then re-read your JSON against the paper one last time: every number, every patient ID, every "x of y". Fix and rebuild if anything is off.

## Step 5: Return (keep it brief)

Return: the .docx path; the one-sentence conclusion; your 1-2 "not discussed in the paper" limitations; and a list of anything you were **unsure about** (ambiguous text, numbers you couldn't reconcile).
