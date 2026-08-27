# Module 1 — Agentic Architecture & Orchestration
### CCAR-F Domain 1 · 27% of the exam · 7 official task statements

This module is built directly against Anthropic's own **CCAR-F Exam Guide**
(v1.0, effective July 2026) — the domain names, task statement numbers, and
weightings below come from that guide's official blueprint, not a third-party
guess. Two of the guide's own "Preparation Exercises" map onto this domain; see
[`scenario.md`](scenario.md) for both, built out in full.

Nothing here reproduces exam questions. Everything is original: labs, scenarios,
and practice questions written to prove out the *mechanism* behind each task
statement, not to memorize an answer key.

## Start here: `app.html`

**[`app.html`](app.html)** is the front door — one page, open it directly in any
browser (no server, no build step). It has everything: the concept for each task
statement, a step-through visualization, **"Run live" buttons that call the real
Claude API from your own browser using a key you paste into the page** (never
written to a file, never sent anywhere but straight to Anthropic or your
Anthropic-compatible endpoint), the actual lab source, and an integrated
13-question practice quiz with scoring and progress tracking.

Paste your key into the "Live API" panel in the sidebar to unlock the live demos.
Nothing about that key is ever committed to this repo — it lives only in your
browser tab.

> If you're viewing this through a claude.ai Artifact preview link instead of the
> actual file, the "Run live" buttons will not work there — claude.ai's sandbox
> blocks outbound network calls by design. Open the real `app.html` file in a
> normal browser to use them.

The standalone pieces below still exist for anyone who wants to run the raw
Python or read one file at a time.

## How to use this module

1. Open `app.html`, skim the task-statement nav so you know what you're aiming at.
2. Click "Run live" on each task statement to watch the real mechanism happen,
   then read the code panel underneath to see the exact source.
3. Build both capstones in [`scenario.md`](scenario.md) — they're Anthropic's own
   recommended prep exercises, done for real.
4. Work the practice quiz cold, then check your reasoning against the
   explanations — each question names the lab that proves its answer.
5. (Optional) Run the labs from the terminal too — see Setup below.

## Setup

```bash
cd labs
pip install -r requirements.txt        # anthropic (lab1, lab4)
pip install claude-agent-sdk            # lab2, lab3 (needs Claude Code CLI configured too)

export ANTHROPIC_API_KEY=sk-ant-...
# Using an Anthropic-compatible endpoint instead (e.g. Azure AI Foundry)?
# export ANTHROPIC_BASE_URL=https://<your-resource>.services.ai.azure.com/anthropic
# export ANTHROPIC_MODEL=<your-deployment-name>
```

Never commit a real key anywhere in this repo. `.gitignore` at the repo root
already excludes `.env` for exactly this reason.

## Task statements → labs

| # | Task statement | Lab | Needs |
|---|---|---|---|
| 1.1 | Design and implement agentic loops for autonomous task execution | [`lab1_agentic_loop.py`](labs/lab1_agentic_loop.py) | `anthropic` |
| 1.2 | Orchestrate multi-agent systems with coordinator-subagent patterns | [`lab2_coordinator_subagents.py`](labs/lab2_coordinator_subagents.py) | `claude-agent-sdk` |
| 1.3 | Configure subagent invocation, context passing, and spawning | [`lab2_coordinator_subagents.py`](labs/lab2_coordinator_subagents.py) | `claude-agent-sdk` |
| 1.4 | Implement multi-step workflows with enforcement and handoff patterns | [`lab3_enforcement_hooks.py`](labs/lab3_enforcement_hooks.py) | `claude-agent-sdk` |
| 1.5 | Apply Agent SDK hooks for tool call interception and data normalization | [`lab3_enforcement_hooks.py`](labs/lab3_enforcement_hooks.py) | `claude-agent-sdk` |
| 1.6 | Design task decomposition strategies for complex workflows | [`lab4_decomposition.py`](labs/lab4_decomposition.py) | `anthropic` |
| 1.7 | Manage session state, resumption, and forking | [`lab5_sessions.md`](labs/lab5_sessions.md) | Claude Code CLI |

**Verified this session:** `lab1_agentic_loop.py` and `lab4_decomposition.py` ran
live end-to-end. `lab2` and `lab3` are written against the Claude Agent SDK's
confirmed real API (verified against current official docs) but need
`claude-agent-sdk` + the Claude Code CLI installed to run — not yet executed live
in this environment.

## A genuinely current gotcha, not a typo

The exam guide calls the subagent-spawning mechanism the **"Task tool"** and says
a coordinator's `allowedTools` must include `"Task"`. Claude Code v2.1.63 renamed
the tool emitted in `tool_use` blocks from `"Task"` to `"Agent"` — but `"Task"`
still appears in the `system:init` tools list and in
`result.permission_denials[].tool_name`. For the exam: know it as the Task
mechanism. For code you write today: put `"Agent"` in `allowed_tools`, and check
`block.name` against **both** names when detecting invocation, exactly as
`lab2_coordinator_subagents.py` does.

## Sources

- Anthropic, *Claude Certified Architect – Foundations Exam Guide*, v1.0
  (effective July 2026) — downloaded from the official Anthropic Partner Academy
  course page. Not redistributed in this repo (Anthropic's copyrighted material);
  request it yourself from [the certification page](https://anthropic-partners.skilljar.com/claude-certified-architect-foundations-certification)
  if you want the primary source.
- [Claude Agent SDK — Subagents](https://code.claude.com/docs/en/agent-sdk/subagents),
  [Hooks](https://code.claude.com/docs/en/agent-sdk/hooks),
  [Custom tools](https://code.claude.com/docs/en/agent-sdk/custom-tools),
  [Permissions](https://code.claude.com/docs/en/agent-sdk/permissions) — verified
  against current official docs while building these labs.
