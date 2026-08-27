# Claude Training — CCAR-F Hands-On Prep

Practical, code-first prep for the **Claude Certified Architect – Foundations (CCAR-F)** exam.

This repo is not another slide deck. Every domain below ships with runnable code, a realistic architecture scenario, and the trade-off reasoning the exam actually tests — because CCAR-F questions are scenario-based ("given this constraint, what do you design?"), not recall-based.

> **Who this is for:** solution architects, AI/ML engineers, technical leads, and students who want to *build* their way to passing CCAR-F rather than memorize flashcards.

---

## Exam snapshot

| | |
|---|---|
| Format | 60 questions, 120 minutes |
| Passing score | 720 / 1000 (scaled) |
| Validity | 12 months |
| Style | Applied scenarios — "what would you design/configure/fix here?" |

**Five domains** (this repo has one folder per domain):

1. Agentic Architecture & Orchestration
2. Claude Code Configuration & Workflows
3. Prompt Engineering & Structured Output
4. Tool Design & MCP Integration
5. Context Management & Reliability

---

## Repo structure

```
claude_training/
├── 01-agentic-architecture/
│   ├── README.md              # concept + when-to-use decision framework
│   ├── workflow_vs_agent.py    # same task, built both ways, with cost/latency notes
│   └── orchestrator_worker.py  # multi-agent fan-out/fan-in pattern
├── 02-claude-code-config/
│   ├── README.md
│   ├── settings.json           # annotated example: permissions, hooks, env
│   └── example.claude/         # a working .claude/ dir (agents, skills, hooks)
├── 03-prompt-engineering/
│   ├── README.md
│   ├── structured_output.py    # tool-forced JSON vs free text, with failure cases
│   └── prompt_before_after.md  # a bad prompt, why it fails, the fixed version
├── 04-tool-design-mcp/
│   ├── README.md
│   ├── mcp_server_example.py   # minimal MCP server with 2 tools
│   └── tool_schema_pitfalls.md # ambiguous vs unambiguous tool schemas, side by side
├── 05-context-management/
│   ├── README.md
│   ├── context_budget.py       # token accounting + compaction strategy
│   └── long_running_agent.py   # sub-agent delegation to avoid context rot
└── scenarios/
    └── mock-exam-scenarios.md  # 15 applied scenarios in exam style, with rationale
```

Each domain folder is self-contained: read its `README.md`, then run the code.

---

## Domain 1 — Agentic Architecture & Orchestration

**Core exam question:** *workflow or agent?*

- **Workflow** = you hard-code the control flow (step 1 → step 2 → step 3). Predictable, cheap, easy to debug. Use when the task steps are known in advance.
- **Agent** = the model decides the next step by choosing tools in a loop. Flexible, handles unknowns, costs more tokens and is harder to bound. Use when the path can't be predetermined.

### Scenario
*"A support team wants to auto-triage incoming tickets: classify severity, look up the customer's plan, and draft a reply. Should this be a workflow or an agent?"*

**Answer:** Workflow. The three steps are always the same and always run in the same order — classify → look up → draft. An agent loop adds cost and non-determinism for zero benefit here. Reserve the agent pattern for the *next* ticket type: "investigate and resolve a novel production incident," where the steps genuinely can't be known ahead of time.

```python
# workflow_vs_agent.py — same task, two architectures

# --- WORKFLOW: fixed steps, deterministic, cheap ---
def triage_ticket_workflow(client, ticket_text: str) -> dict:
    severity = classify_severity(client, ticket_text)          # step 1
    plan = lookup_customer_plan(ticket_text)                   # step 2 (no LLM needed)
    draft = draft_reply(client, ticket_text, severity, plan)   # step 3
    return {"severity": severity, "plan": plan, "draft": draft}

# --- AGENT: model chooses tools until it decides it's done ---
def investigate_incident_agent(client, incident_text: str) -> str:
    messages = [{"role": "user", "content": incident_text}]
    tools = [logs_tool, metrics_tool, runbook_tool, escalate_tool]

    for _ in range(MAX_TURNS):  # always bound agent loops — exam favorite trap
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=1024,
            tools=tools,
            messages=messages,
        )
        if response.stop_reason != "tool_use":
            return response.content[0].text  # agent decided it's done
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": run_tools(response)})

    return "Escalating: investigation exceeded turn budget."
```

**Exam trap to know:** an *unbounded* agent loop (no `MAX_TURNS`, no cost ceiling) is always a wrong answer on the exam, regardless of the scenario — reliability and cost control are graded domains in their own right.

**Orchestrator–worker pattern:** for tasks that decompose into independent sub-tasks (e.g., "research this topic from 5 angles"), fan out to parallel sub-agents and merge results — see [`orchestrator_worker.py`](01-agentic-architecture/orchestrator_worker.py). Know when to reach for this vs. a single agent with more tools: reach for it when sub-tasks are independent and parallelizable, not when they depend on each other's output.

---

## Domain 2 — Claude Code Configuration & Workflows

**Core exam question:** *where does this configuration belong?*

| Need | Belongs in |
|---|---|
| Reusable multi-step task, invoked by name | a **Skill** (`.claude/skills/`) |
| Restrict/allow specific tools or commands | `permissions` in `settings.json` |
| Run something automatically on an event | a **hook** (`PreToolUse`, `PostToolUse`, etc.) |
| Give a specialized agent its own tool subset | a **subagent** definition |
| Per-project vs. per-user vs. org-wide | `.claude/settings.json` vs `~/.claude/settings.json` vs managed policy |

### Scenario
*"Every commit in this repo must run tests before it's created. How do you enforce that without relying on developers remembering?"*

**Answer:** A `PreToolUse` hook matched on the `Bash` tool with a `git commit` command pattern — not a CLAUDE.md instruction (instructions can be ignored or forgotten by the model under context pressure; hooks are enforced by the harness, not the model).

```json
// example.claude/settings.json — annotated
{
  "permissions": {
    "allow": ["Bash(npm test:*)", "Bash(git status)", "Read", "Grep", "Glob"],
    "ask": ["Bash(git push:*)", "Edit"],
    "deny": ["Bash(rm -rf:*)"]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "scripts/require-tests-pass.sh" }]
      }
    ]
  }
}
```

**Exam trap to know:** "put it in CLAUDE.md" is the tempting-but-wrong answer whenever the requirement is *enforcement*. CLAUDE.md shapes model behavior; hooks and permissions are enforced mechanically regardless of what the model decides to do.

---

## Domain 3 — Prompt Engineering & Structured Output

**Core exam question:** *how do you get reliable machine-readable output?*

Don't ask for JSON in prose and hope. Force the shape with a **tool definition** — the model is constrained to the schema, and you get a parse-safe object every time.

```python
# structured_output.py

# --- FRAGILE: JSON requested in free text ---
def extract_fragile(client, review_text: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": f"Extract sentiment and rating (1-5) as JSON from: {review_text}"
        }],
    )
    return response.content[0].text  # model may wrap it in prose, backticks, add commentary

# --- RELIABLE: schema enforced via tool_choice ---
extract_review_tool = {
    "name": "extract_review",
    "description": "Extract structured data from a product review",
    "input_schema": {
        "type": "object",
        "properties": {
            "sentiment": {"type": "string", "enum": ["positive", "neutral", "negative"]},
            "rating": {"type": "integer", "minimum": 1, "maximum": 5},
        },
        "required": ["sentiment", "rating"],
    },
}

def extract_reliable(client, review_text: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=200,
        tools=[extract_review_tool],
        tool_choice={"type": "tool", "name": "extract_review"},  # forces this exact call
        messages=[{"role": "user", "content": review_text}],
    )
    return next(b.input for b in response.content if b.type == "tool_use")
```

### Scenario
*"A pipeline needs the model's output to always be valid JSON matching a fixed schema, with zero parse failures in production. What do you use?"*

**Answer:** `tool_choice: {"type": "tool", "name": "..."}` with a strict `input_schema` — not a system prompt asking nicely for JSON. The exam distinguishes "the model usually complies" from "the model is structurally constrained to comply," and grades the latter as correct whenever "zero failures" or "always valid" appears in the scenario.

See [`prompt_before_after.md`](03-prompt-engineering/prompt_before_after.md) for a real prompt that under-specified an edge case, the failure it caused, and the one-line fix (an explicit instruction for the boundary condition, not a longer prompt overall — the exam penalizes bloated prompts as an anti-pattern).

---

## Domain 4 — Tool Design & MCP Integration

**Core exam question:** *is this tool schema unambiguous enough for the model to use correctly, zero-shot?*

```python
# tool_schema_pitfalls.md — condensed here as code

# --- AMBIGUOUS: vague names, no constraints, overlapping purpose ---
bad_tool = {
    "name": "search",
    "description": "Searches things",
    "input_schema": {
        "type": "object",
        "properties": {"q": {"type": "string"}},
    },
}

# --- UNAMBIGUOUS: specific name, rich description, constrained inputs ---
good_tool = {
    "name": "search_customer_orders",
    "description": (
        "Search a specific customer's order history by date range. "
        "Use this ONLY for orders already placed — for product availability, "
        "use search_product_catalog instead."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "customer_id": {"type": "string", "description": "Internal customer ID, e.g. CUST-1234"},
            "start_date": {"type": "string", "format": "date"},
            "end_date": {"type": "string", "format": "date"},
        },
        "required": ["customer_id", "start_date", "end_date"],
    },
}
```

The description's job is to disambiguate from *other tools in the same toolset* — not to restate the schema. `bad_tool`'s description tells the model nothing it couldn't infer from the name, and gives it no way to distinguish "search" from any other search-shaped tool it might have.

### MCP scenario
*"You're exposing 40 internal APIs to Claude. Half are read-only lookups, half are write operations with real side effects. How do you design the MCP server?"*

**Answer:** Separate read and write tools explicitly (never one tool with a `mode` parameter toggling side effects), and gate write tools behind `permissions.ask` or a human-in-the-loop confirmation step by default. A minimal MCP server showing this split is in [`mcp_server_example.py`](04-tool-design-mcp/mcp_server_example.py).

**Exam trap to know:** a tool whose description says "use with caution" is not a safety control — the exam treats natural-language warnings inside a tool description as advisory only, and expects the *actual* control (permission gating, confirmation step, separate tool) as the correct answer.

---

## Domain 5 — Context Management & Reliability

**Core exam question:** *how does this agent stay reliable as context grows across a long session?*

- **Context rot**: as the context window fills with tool results and history, relevant signal gets diluted and the model's attention to any single fact degrades. More context is not free.
- **Compaction**: summarizing/dropping older turns while preserving what's still load-bearing.
- **Sub-agent delegation**: spinning off a fresh-context agent for a bounded sub-task so the parent's context doesn't absorb every intermediate detail.

```python
# context_budget.py

def should_compact(messages: list, token_budget: int, count_tokens_fn) -> bool:
    used = count_tokens_fn(messages)
    return used > token_budget * 0.8  # compact before hitting the wall, not at it

def compact(client, messages: list) -> list:
    summary = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=500,
        messages=messages + [{
            "role": "user",
            "content": "Summarize the above conversation, preserving all decisions, "
                        "open questions, and file paths mentioned. Drop tool call noise."
        }],
    )
    return [{"role": "user", "content": summary.content[0].text}]
```

### Scenario
*"A coding agent has been running for 40 minutes, making dozens of file edits and tool calls. It starts re-reading files it already read and re-deriving facts already established. What's wrong, and what's the fix?"*

**Answer:** Context rot — the growing history of tool results is diluting the model's effective attention to earlier facts, and nothing is compacting it. Fix: proactive compaction before the budget is exhausted (not "add more context window" — bigger windows don't fix attention dilution, they just delay the same failure), and delegate genuinely independent sub-tasks to sub-agents with their own clean context. See [`long_running_agent.py`](05-context-management/long_running_agent.py).

**Exam trap to know:** "just use a model with a bigger context window" is almost always the wrong answer when the scenario describes degraded reliability over a long session — the fix is architectural (compaction, delegation, retrieval), not a bigger buffer.

---

## Mock exam scenarios

[`scenarios/mock-exam-scenarios.md`](scenarios/mock-exam-scenarios.md) has 15 applied, exam-style scenarios — one per recurring trap across all five domains — each with the answer and the *reasoning*, not just the letter.

## How to use this repo

1. Pick a domain folder, read its `README.md` first.
2. Run the code — change an input, break it on purpose, see what fails and why. The exam tests judgment under constraints, which you build by hitting the constraints yourself.
3. Work through `scenarios/mock-exam-scenarios.md` cold, then check your reasoning against the given rationale.
4. Contribute a scenario you got wrong on a practice exam — see below.

## Contributing

Found a domain gap, a stale example, or want to add a scenario you personally got tripped up on? PRs welcome. Keep additions in the same style: runnable code or a concrete scenario, plus the *why*, not just the *what*.

## Sources / further reading

- [Claude Certified Architect – Foundations exam guide (FlashGenius)](https://flashgenius.net/blog-article/a-guide-to-the-claude-certified-architect-foundations-certification)
- [CCA-F domains & topics breakdown](https://claudearchitectcertification.com/certifications/ccar-f)
- [Anthropic Claude documentation](https://docs.claude.com)

> Note: as of this writing, Anthropic's certification exams are available to people whose organizations participate in the Claude Partner Network, and registration requires a recognized company email. This repo is independent self-study material and is not affiliated with or endorsed by Anthropic.
