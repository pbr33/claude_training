# Domain 1 — Agentic Architecture & Orchestration
### Practice questions, mapped to Task Statements 1.1–1.7

> Original items written to mirror the official CCAR-F blueprint's task statements
> and the exam's applied-scenario register. Not real exam questions — no exam
> content is reproduced. Each is tagged with the lab in `labs/` that proves the
> answer, so if you get one wrong, go run that lab and watch it happen.

---

**Q1** *(Task 1.1 · proves out in `lab1_agentic_loop.py`)*
A junior engineer's agentic loop checks `if "I'm done" in response.text:` to decide
whether to stop calling tools. It works in testing, then breaks in production the
first time the model's final answer happens to phrase completion differently.
What's the correct fix?

- A. Add more phrases to check for ("finished", "complete", "all done")
- B. Check `response.stop_reason == "end_turn"` instead of parsing text content
- C. Lower the temperature so phrasing is more consistent
- D. Add a retry loop that re-asks until the exact phrase appears

**Answer: B.** `stop_reason` is a structural field the API sets deterministically —
`"tool_use"` means keep going, `"end_turn"` means stop. Parsing text for a
completion phrase is exactly the anti-pattern the exam guide calls out by name; A
just adds more brittle phrases to a fundamentally wrong mechanism, C doesn't
address the structural issue, D never terminates if the phrase is never said.

---

**Q2** *(Task 1.1 · proves out in `lab1_agentic_loop.py`)*
An agent's tool-result-handling code does `messages.append({"role": "user",
"content": [{"type": "tool_result", "content": result}]})` — omitting the
`tool_use_id` field. What happens?

- A. The API infers which tool call the result belongs to from message order
- B. The request is rejected — the API requires each tool_result's tool_use_id to match an outstanding tool_use block
- C. Claude silently ignores the malformed result and answers from general knowledge
- D. The SDK auto-generates a tool_use_id to patch the gap

**Answer: B.** The exact `tool_use_id` round-trip is enforced, not optional or
inferred — that's the whole reason it exists when a turn can contain multiple
tool calls. A, C, and D all describe forgiving behavior the API doesn't have.

---

**Q3** *(Task 1.2 · proves out in `lab2_coordinator_subagents.py`)*
A coordinator decomposes "audit our onboarding funnel for drop-off causes" into
exactly one subagent task: "check the signup form for UX issues." The subagent
does excellent work and reports back. The final report misses payment failures,
email verification delays, and mobile-specific bugs entirely. Whose failure is
this?

- A. The subagent's — it should have looked beyond its assigned scope
- B. The coordinator's — its decomposition was too narrow and never assigned those angles to anyone
- C. No one's — the coordinator can only be blamed if a subagent errors out
- D. The synthesis step's — it should have noticed the report felt incomplete

**Answer: B.** A subagent doing exactly its assigned job well is not a subagent
failure — the coordinator never created a subtask covering payment, email, or
mobile at all, so no agent in the system was ever going to surface them. A asks a
context-isolated subagent to guess at scope it was never given. D blames a
downstream step for a decomposition gap it has no way to detect without doing the
coordinator's job over again.

---

**Q4** *(Task 1.3 · proves out in `lab2_coordinator_subagents.py`)*
A coordinator's `allowed_tools` list is `["Read", "Grep"]`. When Claude tries to
delegate a subtask to a defined subagent, the call is denied. What's missing?

- A. The subagent's own `tools` field needs `"Read"` added
- B. `Agent` (the tool that spawns subagents — the exam blueprint's "Task" mechanism) needs to be in the coordinator's `allowed_tools`
- C. The subagent needs to be registered in a separate `subagents.json` file
- D. `model` needs to be set to `"opus"` on the coordinator

**Answer: B.** Spawning a subagent is itself a tool call — if the tool that does
the spawning isn't approved, the call never happens regardless of what the
subagents themselves are configured with. A confuses the subagent's own tool
restrictions with the coordinator's ability to invoke it at all. C and D describe
mechanisms that don't exist.

---

**Q5** *(Task 1.3 · proves out in `lab2_coordinator_subagents.py`)*
A coordinator has been chatting with the user for 20 turns, building up detailed
context about a bug. It then delegates root-cause analysis to a subagent with the
prompt: `"Investigate the bug we discussed."` What goes wrong?

- A. Nothing — subagents automatically inherit the parent conversation
- B. The subagent starts with a blank context except that one sentence — it has no idea what bug was discussed
- C. The API throws an error because the prompt is too vague
- D. The subagent asks the coordinator a clarifying question automatically

**Answer: B.** Unless a subagent is a fork, its context starts fresh — the only
thing that crosses the boundary is the prompt string you hand it. Twenty turns of
shared context evaporate unless you explicitly restate what's needed. A is the
exact false assumption that causes this bug in real systems; C and D describe
graceful failure modes that don't actually happen — the subagent just proceeds
confidently with almost nothing to go on.

---

**Q6** *(Task 1.4 · proves out in `lab3_enforcement_hooks.py`)*
A fintech agent's system prompt says: "Always verify the customer's identity
before processing any refund." Production logs later show refunds processed
without verification in roughly 1 in 8 cases. What's the correct diagnosis and fix?

- A. The prompt needs stronger language, like "NEVER skip verification, this is CRITICAL"
- B. Prompt-based instructions have a non-zero failure rate; add a programmatic prerequisite gate that blocks the refund tool until verification has actually returned a verified ID
- C. Switch to a more capable model, which will follow instructions more reliably
- D. Add a few-shot example showing the correct order of operations

**Answer: B.** This is the exam guide's own headline example, and the fix is
architectural, not rhetorical: when a business rule must hold with financial
consequences, it belongs in code (a hook or prerequisite gate) that can actually
block the call, not in a prompt the model is merely likely to follow. A, C, and D
are all still prompt-layer fixes — they may reduce the failure rate somewhat, but
none of them can reduce it to zero, and zero is the requirement here.

---

**Q7** *(Task 1.4)*
An agent escalates a billing dispute to a human agent with the message: "Customer
has a billing issue, please help." The human agent has no access to the bot's
conversation transcript and has to start the investigation from scratch. What's
missing from the escalation?

- A. Nothing — human agents are expected to re-investigate every case
- B. A structured handoff summary: customer details, root cause analysis already done, and a recommended action
- C. A confidence score attached to the escalation
- D. An apology to the customer for the inconvenience

**Answer: B.** The whole value of an agent that's already done the investigation
is lost if the handoff throws that work away. A structured summary — who, what was
found, what's recommended — lets the human start from the agent's findings instead
of zero. A defeats the purpose of escalating from an agent that already has
context; C and D are not substitutes for the actual case information the human
needs to act.

---

**Q8** *(Task 1.5 · proves out in `lab3_enforcement_hooks.py`)*
Three different backend systems feed an agent order data: one returns timestamps
as Unix epoch integers, one as ISO 8601 strings, and one as `"3 days ago"`-style
relative text. The agent frequently reasons incorrectly about delivery deadlines.
What's the most targeted fix?

- A. Tell the model in the system prompt to "convert all timestamps to a consistent format before reasoning"
- B. A PostToolUse hook that normalizes each tool's raw output into one consistent format before the model ever sees it
- C. Switch all three backends to the same date format (a multi-team migration)
- D. Ask the model to double-check its date math with a calculator tool

**Answer: B.** A `PostToolUse` hook intercepts and transforms tool results
deterministically, before they reach the model's context — this is precisely the
data-normalization pattern the exam guide describes. A relies on the model
correctly performing three different parses every single time, which is exactly
the kind of probabilistic compliance that produces the errors described. C solves
it but at a cost and timeline wildly disproportionate to a normalization hook. D
doesn't address the root cause — bad input format — at all.

---

**Q9** *(Task 1.5)*
A team wants refunds over $500 to always require human approval, with zero
exceptions, regardless of how the model is prompted. Where does this rule belong?

- A. In the system prompt, worded as an absolute rule
- B. In a `PreToolUse` hook that inspects the tool call's arguments and denies/redirects when the amount exceeds the threshold
- C. In a few-shot example showing a refusal for a $600 refund
- D. In the tool's description field, noting the limit

**Answer: B.** "Zero exceptions regardless of prompting" is definitionally an
enforcement requirement, and only code the model cannot talk its way around
satisfies that — a hook that inspects the actual argument value and denies the
call. A, C, and D are all still forms of asking nicely; the model reads them as
guidance, not a wall.

---

**Q10** *(Task 1.6 · proves out in `lab4_decomposition.py`)*
A team is building a review pipeline for pull requests with a fixed, well-
understood shape: lint check, then test coverage check, then a security scan,
always in that order, always the same three steps. What decomposition strategy
fits?

- A. Dynamic decomposition — let the model decide what to check and in what order
- B. Prompt chaining — a fixed, ordered sequence of calls matching the known steps
- C. A single call asking for all three at once, to save tokens
- D. Multi-agent orchestration with a coordinator

**Answer: B.** When the steps are fully known in advance and always the same,
prompt chaining is the simpler, more predictable, and cheaper choice — dynamic
decomposition (A) adds flexibility you don't need and non-determinism you don't
want here. C sacrifices the attention-quality benefit of separating distinct
concerns into separate focused passes. D is architecture overkill for a fixed
three-step pipeline with no need for isolated context or parallelism.

---

**Q11** *(Task 1.6)*
A team is building an agent for "investigate why our checkout conversion dropped
last week" — the right places to look aren't knowable in advance; it could be a
UI bug, a payment provider outage, a pricing change, or something else entirely.
What decomposition strategy fits, and why would prompt chaining be the wrong
choice here?

- A. Prompt chaining — check UI, then payments, then pricing, in that fixed order, every time
- B. Dynamic decomposition — let the model investigate, form hypotheses from what it finds, and decide what to check next
- C. Prompt chaining, because it's cheaper and open-ended tasks should still be bounded by cost
- D. Neither — this should be a single unstructured prompt with no tools

**Answer: B.** The task is open-ended and the useful next step depends entirely on
what's found at each point — exactly the case for dynamic, tool-driven
decomposition. A and C force a predetermined order onto a genuinely unpredictable
investigation, which either misses the real cause or wastes turns on irrelevant
fixed steps. D throws away the ability to actually look at anything.

---

**Q12** *(Task 1.7 · walkthrough in `lab5_sessions.md`)*
A developer resumes a named Claude Code session from yesterday to continue a
codebase investigation. Overnight, a teammate refactored two of the files the
session had already analyzed. The developer just runs `claude --resume
"investigation"` with a new question and says nothing about the refactor. What's
the risk?

- A. None — Claude Code automatically detects file changes on resume
- B. The session may reason from its stale prior findings about those two files, unaware they've changed
- C. The resume command will fail outright since the files changed
- D. Claude Code discards the entire session history rather than risk staleness

**Answer: B.** Resumption does not automatically re-verify previously read files
against disk — it's on the developer to inform the resumed session about what
changed so it does a targeted re-read, rather than silently reasoning from stale
tool results. A and D describe safety nets that don't exist; C is simply false.

---

**Q13** *(Task 1.7 · walkthrough in `lab5_sessions.md`)*
A developer has a shared baseline analysis of a slow database query and wants to
compare two different fix strategies (adding an index vs. rewriting the query)
without either exploration influencing the other, and without redoing the shared
analysis twice. What's the right mechanism?

- A. Two completely separate sessions, each redoing the baseline analysis from scratch
- B. `fork_session` twice from the same baseline session, one per strategy
- C. One session, asking about both strategies in the same conversation
- D. `--resume` twice in sequence, evaluating one strategy then the other in the same session

**Answer: B.** Forking gives each branch the shared baseline for free while
keeping the two explorations independent so neither's reasoning leaks into the
other — exactly the divergent-approaches-from-a-shared-baseline use case
`fork_session` exists for. A duplicates real work. C and D let the two strategies'
reasoning contaminate each other in a single shared context.

---

## Quick-recall cheat sheet — Domain 1

- **`stop_reason`, not text parsing, not iteration caps.** `tool_use` = continue, `end_turn` = stop.
- **Exact `tool_use_id` match** on every tool_result, always.
- **Coordinator owns decomposition and routing.** A subagent doing its assigned job perfectly is not proof the assignment was right — check whether anyone was assigned the missing angle.
- **Subagents don't auto-inherit context.** Only the prompt string you hand them crosses the boundary (forks are the one exception).
- **`Agent`/`Task` must be in `allowed_tools`** for a coordinator to spawn anyone at all.
- **Non-zero prompt failure rate + real-world consequence = enforce in code.** Hooks/prerequisite gates, not stronger wording.
- **PostToolUse hooks normalize; PreToolUse hooks gate/block.** Both run in code, before the model reasons over the result.
- **Chaining for predictable fixed steps; dynamic decomposition for open-ended investigation.**
- **Resume + brief it on what changed** when prior context is still mostly valid; **fresh + injected summary** when it's stale.
- **`fork_session`** = divergent branches from one shared baseline, not duplicated groundwork.
