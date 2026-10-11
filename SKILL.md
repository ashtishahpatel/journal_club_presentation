---
name: journal_club_presentation
description: Turn one or more journal club article PDFs into a 10-minute presentation outline (.docx) that follows the residency "Tips for Journal Club Presentations" template, with bulleted facts, cropped figures with red highlight boxes, and a results-heavy focus. One sub-agent per paper, run in parallel.
argument-hint: <path-to-article.pdf> [more PDFs...]
---

# Journal Club Presentation

The user is a urology resident who presents journal club. They have **10 minutes** to walk the group through each paper, then ~10 minutes of discussion. They talk from bullets and do not read sentences aloud. For every PDF, produce a Word outline that follows the template in `reference/template.md`.

Scripts live in `~/.claude/skills/journal_club_presentation/scripts/`. Per-paper instructions for sub-agents are in `~/.claude/skills/journal_club_presentation/reference/paper_agent.md`.

## 1. Collect the PDFs

`$ARGUMENTS` holds one or more PDF paths. Paths may be quoted, contain spaces or colons, or come as `@`-mentions. If a folder is given, use every `.pdf` in it. If nothing is given, ask which articles to use.

## 2. Check dependencies (once)

```bash
which pdftoppm && python3 -c "import docx, PIL"
```

If `python-docx` is missing, run `pip3 install python-docx`. If `pdftoppm` is missing, tell the user to run `brew install poppler` and stop.

## 3. One sub-agent per paper, in parallel

In a **single message**, launch one `general-purpose` Agent per PDF. Give each agent:

- the absolute PDF path
- a scratch working directory unique to that paper (inside your scratchpad)
- the output path: same folder as the PDF, named `<PDF basename> - JC Outline.docx`
- this instruction: *"Read `~/.claude/skills/journal_club_presentation/reference/paper_agent.md` and follow it exactly for this paper."*
- any extra preferences the user stated in this conversation (they override the defaults)

Don't read or summarize the papers in the main agent. That's the sub-agents' job.

## 4. Review what comes back

For each finished agent:

- Confirm the .docx exists.
- Make a thumbnail of page 1 with `qlmanage -t -s 1100 -o <scratch> <docx>` and look at it to sanity-check the layout.
- Read the agent's list of numbers it was unsure about. Spot-check one or two key result numbers against the PDF yourself.

## 5. Report to the user

For each paper, give a clickable link to the .docx, the one-line conclusion, and any open questions (e.g., unclear numbers, figures that couldn't be highlighted cleanly). Keep it short.
