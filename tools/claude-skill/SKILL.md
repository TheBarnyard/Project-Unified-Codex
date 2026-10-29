---
name: project-unified-codex
description: Use for any ENGT 480 pendulum project work, or when the user says PUC or codex. Loads the team's shared memory repo at the start and logs the session to it at the end.
---

# Project Unified Codex (PUC)

PUC is the pendulum team's shared AI memory: the GitHub repo `TheBarnyard/Project-Unified-Codex`, a folder of Markdown pages. Use it like your own long-term memory, shared with every teammate's AI. Its full rules are in the repo's `AGENTS.md`; read and follow them. This skill says how to reach the repo and when to read and write.

## 1. Get the repo (no approval needed; this is the user's own memory)

Use the first route that works:
1. **Cloud session with `add_repo`:** call `add_repo` with owner `TheBarnyard`, repo `Project-Unified-Codex`, `access: "push"`. Clone it into the scratchpad (or `git -C <dir> pull --rebase` if it is already cloned this session). If the tool returns a clone to register, call `register_repo_root`.
2. **Local Claude Code:** `git clone https://github.com/TheBarnyard/Project-Unified-Codex.git` (or pull if it exists) with the user's own git credentials.
3. **No shell but GitHub tools:** read files with the GitHub `get_file_contents` tool and write with `push_files` / `create_or_update_file` on branch `main`.
4. **None of these:** tell the user in one line that PUC is unreachable, and at the end give them the session file to paste (see `prompts/end.md` in the repo).

If access is denied, relay the tool's reason and remedy once, then continue the user's task without PUC.

## 2. At the start of the work
Follow `AGENTS.md` section 1: read `BRIEF.md`, `INDEX.md`, the last 7 days of `sessions/`, then more according to the member's `context` preference in `members.md` (ask once if it is `ask` or missing, and offer to save the answer). Apply any `pages_applied: no` sessions. Do this quietly; mention only what matters for the task (a teammate's WIP on the same part, a known dead end, a conflict).

## 3. During the work
Re-pull before re-reading after a few minutes. Update the matching page as soon as something durable is learned.

## 4. When the work is done
Follow `AGENTS.md` section 3:
1. Add one line to your final reply: "Anything to add to PUC before I save?" If the user answers later, append it to the same session file.
2. Write the session file from `templates/session.md` and update the shared pages it touched.
3. Commit `PUC: <member> - <title>`, `git pull --rebase`, push. On a conflict keep both sides and push again.
4. Tell the user in one short line that PUC was updated, naming the session file.

## Hard rules
- Only project information. Never other classes, personal topics, grades, credentials, or private contact details. When unsure, leave it out.
- Never delete teammates' content: strike it and note what superseded it.
- On conflicting information, show both with sources and dates and add it to `open-questions.md`.
- Never edit the team's original source code because of PUC; PUC holds notes, not code.
