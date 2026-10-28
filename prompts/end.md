# End prompt (ChatGPT, Gemini, local models)

Paste everything below the line at the end of your chat. Copy the AI's answer, then on GitHub open the repo, click **Add file > Create new file**, paste the path it gives as the file name, paste the content, and commit. That is the only step. The next Claude or coding-agent session will move the "Proposed page updates" into the shared pages.

---

Write a PUC session entry for this chat.

Rules:
- Only project information (the pendulum rig, code, firmware, wiring, runs, modelling, reports, team decisions). Leave out anything else, plus any passwords, keys or personal details.
- Short and specific: numbers with units, file paths, branches, commits, run log names, absolute dates.
- Tag each finding [HW] verified on hardware, [SIM] simulation only, [HYP] hypothesis, or [?] unconfirmed.
- Include dead ends and why they failed.
- Under "Proposed page updates", list each PUC page that should change and the exact text to add (for example hardware-state.md, params.md, a debug page, open-questions.md, BRIEF.md).
- Set `pages_applied: no`.

First ask me: "Anything to add before I write it?" Then output exactly two things:
1. One line: `PATH: sessions/YYYY/MM/YYYY-MM-DD_HHMM_<my name>_<short-slug>.md`
2. One Markdown code block with the full file, using this template:

```
---
type: session
date: YYYY-MM-DD
time: HH:MM (local)
member:
ai:
topics: []
status: done | wip | abandoned
pages_applied: no
transcript: none
---
# <title>

## Goal
## What happened
## Findings
## Dead ends
## Decisions
## Changed
## Open questions and next steps
## Proposed page updates
```
