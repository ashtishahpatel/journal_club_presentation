# journal_club_presentation

A [Claude Code](https://claude.com/claude-code) skill that turns journal club article PDFs into a 10-minute presentation outline (.docx). The outline follows the residency "Tips for Journal Club Presentations" template, uses bullet points, and focuses on results, with cropped figures and red highlight boxes.

## Use

In Claude Code:

```
/journal_club_presentation ~/Desktop/article1.pdf ~/Desktop/article2.pdf
```

Claude starts one agent per paper in parallel. Each outline is saved next to its PDF as `<name> - JC Outline.docx`.

## Install on a new machine

```bash
git clone <this repo> ~/.claude/skills/journal_club_presentation
brew install poppler
pip3 install python-docx pillow
```

## Files

- `SKILL.md`: orchestration (one sub-agent per paper)
- `reference/paper_agent.md`: what each agent does with its paper (content and style rules)
- `reference/template.md`: the journal club template
- `scripts/figure_tool.py`: page grid previews; crop figures and draw labeled highlight boxes
- `scripts/build_docx.py`: build the Word outline from a JSON spec
