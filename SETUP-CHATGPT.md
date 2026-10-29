# PUC setup for ChatGPT users

PUC (Project Unified Codex) is our team's shared AI memory. It is this GitHub folder. Your ChatGPT reads it so it knows what everyone has done, and you add a short note to it after each work session so everyone else's AI knows what you did.

Setup takes about 10 minutes, once. After that it is two short messages per session.

---

## Part 1: One-time setup

### Step 1. Get into the repo
1. Accept the GitHub invite Barney sent you (check your email or [github.com/notifications](https://github.com/notifications)).
2. Open [github.com/TheBarnyard/Project-Unified-Codex](https://github.com/TheBarnyard/Project-Unified-Codex). If you can see the files, you're in.

### Step 2. Add yourself to the team list
1. Open [members.md](members.md) and click the pencil icon (Edit).
2. Fix your row: your name, what you work on, and `ChatGPT` under AI tools.
3. For `context`, pick how much your ChatGPT should read at the start of a chat: `brief` (just the summary, best for most people), `topic` (summary plus pages about what you're working on), or `full` (everything).
4. For `transcripts`, leave `no`.
5. Click **Commit changes**.

### Step 3. Make a ChatGPT project
1. In ChatGPT, in the left sidebar, click **New project**. Name it `ENGT 480 Pendulum`.
2. Open the project, then open its settings and find **Instructions**.
3. Paste everything in the box below and save.

```
You are helping me on the ENGT 480 inverted pendulum team project. The team shares a memory called PUC (Project Unified Codex): the GitHub repo TheBarnyard/Project-Unified-Codex.

START: When I start a chat, read BRIEF.md (from the GitHub repo if it is connected, otherwise from this project's files). Check dates, and treat [HYP] and [?] as unconfirmed. Tell me anything in PUC that matters for what I'm doing, and point it out if PUC and I disagree.

END: When I say "end session", ask me "Anything to add to PUC?", then output:
1. One line: PATH: sessions/YYYY/MM/YYYY-MM-DD_HHMM_<my name>_<short-slug>.md
2. One code block with the session file: a YAML header (type: session, date, time, member, ai: ChatGPT, topics, status: done|wip|abandoned, pages_applied: no, transcript: none), then the sections Goal, What happened, Findings (tag each [HW] hardware-verified, [SIM] simulation only, [HYP] hypothesis, or [?] unconfirmed), Dead ends (and why they failed), Decisions, Changed (code paths, branches, commits, firmware flashed, wiring, run log names), Open questions and next steps, and Proposed page updates (which PUC page should change and the exact text).

RULES: Only project information. Never other classes, personal topics, grades, passwords or keys. Be short and specific: numbers with units, file paths, dates as YYYY-MM-DD.
```

### Step 4. Let ChatGPT read PUC (pick one)

**Option A: GitHub connector (best, needs a paid ChatGPT plan).**
1. ChatGPT **Settings > Apps** (some accounts call it **Connectors**), find **GitHub**, and connect your GitHub account.
2. When GitHub asks which repositories to allow, include `TheBarnyard/Project-Unified-Codex`.
3. In a chat, turn GitHub on from the **+** menu if it isn't already on. ChatGPT can now read the newest PUC every time.

**Option B: Upload the summary (works on the free plan).**
1. Open [BRIEF.md](BRIEF.md) and click the download icon (Download raw file).
2. In your ChatGPT project, add it under **Files**.
3. Re-upload it about once a week so it stays current. If you're working on something specific, also upload that page (for example a file from `debug/` or `subsystems/`).

Setup is done.

---

## Part 2: Every work session

### At the start
Open a new chat inside the `ENGT 480 Pendulum` project and say what you're doing, for example:

> Start PUC session. Today I'm working on the TX2 battery wiring.

ChatGPT reads PUC and tells you anything relevant, such as what was tried before or someone else's unfinished work on the same part.

### At the end
1. Type `end session`. Answer its question ("Anything to add to PUC?") or say `no`.
2. It gives you a `PATH:` line and a code block. Copy both.
3. Go to the repo on GitHub and click **Add file > Create new file**.
4. In the file name box, paste the path after `PATH: ` (for example `sessions/2026/10/2026-10-29_1530_Ethan_tx2-battery.md`). The slashes create the folders automatically.
5. Paste the code block's contents into the big text box.
6. Click **Commit changes**. For the message, use `PUC: <your name> - <short title>`, then commit.

That's it. The next Claude session moves your "Proposed page updates" into the right pages, so you never have to edit those pages yourself.

---

## The rules
- **Project stuff only.** No other classes, personal topics, grades, passwords, or API keys. If a chat drifted off-topic, the log should only cover the project part.
- **Don't delete other people's notes.** If something is wrong, say so in your session log and it will be marked as outdated.
- **Write down what didn't work, too.** Dead ends save the next person hours.

## Quick fixes
| Problem | Fix |
| --- | --- |
| I can't see the repo | Accept the invite, or ask Barney to add your GitHub username. |
| ChatGPT says it can't find BRIEF.md | Option A: turn GitHub on in the chat's **+** menu. Option B: re-upload BRIEF.md to the project files. |
| ChatGPT's info seems old | Option B only: re-upload BRIEF.md. |
| I forgot to log a session | Open the old chat, type `end session`, and commit it the same way. |
| Commit button is greyed out | The file name box is empty; paste the path. |
