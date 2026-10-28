# Project Unified Codex (PUC)

PUC is the shared memory of the ENGT 480 pendulum team. It is a plain folder of Markdown files. Every teammate's AI reads it at the start of a work session and writes back to it at the end, so whoever works next starts fully up to date.

It is a memory, not an AI. Nothing here runs by itself; the AIs follow the rules in [AGENTS.md](AGENTS.md).

## Start here

| File | What it is |
| --- | --- |
| [BRIEF.md](BRIEF.md) | Where the project stands right now. Read first. |
| [INDEX.md](INDEX.md) | Map of every page. |
| [AGENTS.md](AGENTS.md) | The rules every AI follows to read and write PUC. |
| [members.md](members.md) | Who is on the team, what they own, their PUC preferences. |

## How each of us uses it

- **Claude (claude.ai projects, Claude Code):** install the skill in [tools/claude-skill/SKILL.md](tools/claude-skill/SKILL.md). It pulls PUC when you start and pushes a session log when you finish. Claude Code also reads [CLAUDE.md](CLAUDE.md) automatically when this repo is open.
- **Codex CLI, Cursor, Copilot, Gemini CLI, other coding agents:** open or clone this repo; they read [AGENTS.md](AGENTS.md) automatically.
- **ChatGPT, Gemini app, local models without git:** paste [prompts/start.md](prompts/start.md) at the start, and [prompts/end.md](prompts/end.md) at the end. The end prompt gives you one block to paste into GitHub (Add file > Create new file).
- **People:** read it on GitHub like any docs folder, or open the folder in Obsidian.

## The one hard rule

Only project information goes in. No other classes, no personal topics, no grades, no passwords or API keys. AIs must strip anything else before writing.
