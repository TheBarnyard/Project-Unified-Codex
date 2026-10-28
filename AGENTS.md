# PUC rules for every AI

You are working with the Project Unified Codex (PUC): the shared memory of the ENGT 480 inverted pendulum team. Treat it like your own long-term memory, shared with the whole team's AIs. Follow these rules exactly.

## 1. At the start of a session

1. Get the latest version (`git pull --rebase`, or re-read the files if you have no git).
2. Read [BRIEF.md](BRIEF.md) and [INDEX.md](INDEX.md).
3. List `sessions/` and read the titles and status of the last 7 days of sessions. Mention any WIP session that touches what the user is about to do.
4. Check the user's context preference in [members.md](members.md):
   - `brief`: stop here.
   - `topic`: also read the subsystem, debug and decision pages for the topic of this session.
   - `full`: also read every page linked from INDEX.md.
   - `ask` or not listed: ask the user once which they want, and offer to save it as their default.
5. Before trusting a page for a decision, check its `updated:` date and any `[?]` or `[HYP]` tags.
6. If you can push: find session files with `pages_applied: no` (written from ChatGPT and other AIs without git). Apply their "Proposed page updates" to the shared pages, set `pages_applied: yes`, and commit as `puc: apply updates from <session file>`.

## 2. During the session

- Re-pull before reading a page again if more than a few minutes have passed; teammates write constantly.
- When something durable is learned (a cause found, a value measured, a decision made, hardware changed), update the matching page right away, not only the session log.

## 3. At the end of a session

1. Ask the user once: "Anything to add to PUC before I save?" Include what they say.
2. Write one session file: `sessions/YYYY/MM/YYYY-MM-DD_HHMM_<member>_<short-slug>.md` from [templates/session.md](templates/session.md). One file per session; if you continue the same session later, append to it.
3. Update the shared pages the session touched: [BRIEF.md](BRIEF.md) if the project state changed, [hardware-state.md](hardware-state.md), [params.md](params.md), [open-questions.md](open-questions.md), [gotchas.md](gotchas.md), `subsystems/`, `debug/`, `decisions/`. Add new pages to [INDEX.md](INDEX.md).
4. Full transcript: only if the member has `transcripts: yes` in members.md. Save it to `transcripts/YYYY/MM/<same name as the session>.md` after applying rule 4 below.
5. Commit with the message `puc: <member> - <session title>`, then `git pull --rebase` and push. On a conflict, keep both sides' text and push again.

## 4. What may go in (hard rule)

- Only information about this project: the rig, code, firmware, wiring, runs, modelling, reports, schedule, team decisions.
- Never: other classes, personal topics, grades, health, opinions about people, passwords, API keys, tokens, or private contact details.
- If a session mixed topics, write only the project part. If unsure whether something is project-related, leave it out.

## 5. How to write

- Short and specific: numbers with units, file paths with repo and branch, commit hashes, run log names, absolute dates (YYYY-MM-DD).
- Say who found or decided it and in which session.
- Tag claims: `[HW]` verified on hardware, `[SIM]` simulation or digital twin only, `[HYP]` hypothesis, `[?]` unconfirmed.
- Record dead ends with why they failed. They are as valuable as fixes.
- Never delete someone else's content. If it is wrong or old, mark it `~~struck~~` with `Superseded YYYY-MM-DD by <session link>: <reason>`.
- Conflicting information: show both, each with its source and date, and add the conflict to [open-questions.md](open-questions.md). Do not pick a winner unless a team member decided it.
- When the code and PUC disagree, report both to the user and record the disagreement; do not silently change either.
- Use relative Markdown links between pages so they work on GitHub.

## 6. Folder layout

| Path | Holds |
| --- | --- |
| `BRIEF.md` | Current state of the project, at most about 150 lines |
| `INDEX.md` | Every page with a one-line description |
| `members.md` | Team, ownership, AI tools, PUC preferences |
| `direction.md` | Goals, deadlines, priorities |
| `hardware-state.md` | What is physically on the rig now (firmware, wiring, arms) |
| `params.md` | Key constants and settings, with sources and conflicts |
| `gotchas.md` | Traps that cost someone time |
| `open-questions.md` | Unresolved questions and conflicts |
| `subsystems/` | One living page per part of the system |
| `debug/` | One page per investigation: symptoms, tests, dead ends, cause, fix |
| `decisions/` | One page per decision: what, why, alternatives, who |
| `sessions/YYYY/MM/` | One file per AI work session |
| `transcripts/` | Opt-in full transcripts |
| `templates/` | Templates for the files above |
| `prompts/` | Copy-paste prompts for AIs that cannot use git |
| `tools/` | The Claude skill and other helpers |
