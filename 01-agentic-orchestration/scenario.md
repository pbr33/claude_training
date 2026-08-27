# Capstone scenarios — Domain 1

These are original walkthroughs of the two **official preparation exercises** from
Anthropic's own CCAR-F Exam Guide that map onto Domain 1. The guide's exact wording
is Anthropic's copyrighted exam-guide text (not reproduced here) — what follows is
an original build-it-yourself walkthrough of the same two exercises, using the labs
in this module.

> Official framing, paraphrased: *Exercise 1 — build a multi-tool agent with
> escalation logic. Exercise 4 — design and debug a multi-agent research pipeline.*
> Both are explicitly called out in the guide's own "How to Prepare" section as
> what a candidate should build before sitting the exam.

---

## Capstone A — Multi-tool agent with escalation logic

**Maps to:** Task Statements 1.1, 1.4, 1.5 · reinforces Domain 2 (tool design) and
Domain 5 (context/escalation), which is exactly why the official exam guide frames
this exercise as reinforcing three domains at once — production systems don't
respect your domain boundaries.

**Build it:**

1. Start from `labs/lab1_agentic_loop.py`'s loop shape (`stop_reason`-driven, exact
   `tool_use_id` matching) and `labs/lab3_enforcement_hooks.py`'s tool set
   (`get_customer`, `process_refund`).
2. Add a third and fourth tool: `lookup_order` and `escalate_to_human`. Write each
   tool's description to clearly differentiate it from the others — this is
   Domain 2 territory, but tool selection reliability is exactly what breaks
   Domain 1 escalation flows in practice.
3. Reuse `lab3`'s `PreToolUse` prerequisite gate (block `process_refund` until
   `get_customer` has verified an ID) and threshold gate (deny refunds over a
   policy amount, redirecting to `escalate_to_human`).
4. Add a genuine multi-concern test: one user message that bundles two issues
   ("my order is late AND I was double-charged"). Verify the agent decomposes it
   into distinct items, investigates each with the right tool, and synthesizes one
   reply — rather than only handling the first thing it noticed.
5. Test your escalation triggers against the anti-patterns Task Statement 5.2 (and
   the exam guide's own sample Question 3) calls out explicitly:
   - **Right triggers:** an explicit "let me talk to a human" request, a policy gap
     (the customer's ask isn't covered by any rule you implemented), inability to
     make progress after a reasonable number of turns.
   - **Wrong triggers:** a self-reported confidence score, detected sentiment/
     frustration. Neither correlates with actual case complexity — build them in
     anyway and watch them escalate the wrong cases, so you've seen the failure
     mode once instead of just being told about it.

**What "done" looks like:** a transcript where a straightforward request resolves
without escalating, a policy-gap request escalates with a structured handoff
(customer ID, root cause, what was attempted) instead of a bare "I can't help with
that," and a refund-amount request over your threshold gets blocked by the hook
before the tool ever executes — not by the model choosing not to call it.

---

## Capstone B — Multi-agent research pipeline

**Maps to:** Task Statements 1.2, 1.3, 1.6 · reinforces Domain 2 (tool
distribution) and Domain 5 (error propagation, provenance).

**Build it:**

1. Start from `labs/lab2_coordinator_subagents.py`. It already has a coordinator,
   a research subagent role, and a synthesis subagent role.
2. Deliberately reproduce the exam guide's own sample-question failure mode first:
   write a coordinator prompt that decomposes a broad topic into subtasks that are
   all the *same narrow angle* (e.g., three subtopics that are all visual-arts
   flavored for a "creative industries" topic). Run it. Confirm the output has a
   real, visible coverage gap — this is the point: the subagents did their jobs
   correctly, the decomposition was the bug.
3. Fix the decomposition to partition by genuinely distinct angle instead, and
   confirm the coverage gap closes.
4. Add error propagation: make one subagent's tool intentionally fail (simulate a
   timeout). Verify the coordinator receives *structured* error context — failure
   type, what was attempted, partial results — not a generic "search unavailable,"
   and that it proceeds with partial results plus an annotated coverage gap rather
   than either suppressing the failure or aborting the whole run.
5. Feed the synthesis subagent two "sources" with a genuinely conflicting number
   (e.g. two stats that disagree). Confirm the final report preserves both values
   with attribution rather than silently picking one — and add a publication-date
   field to each source so a real temporal difference can't be misread as a
   contradiction.
6. Time a sequential version (one subagent call per turn) against the parallel
   version (multiple `Agent`/`Task` calls in one coordinator response). Confirm
   you can see and explain the latency difference, not just assert it exists.

**What "done" looks like:** a run where you can point at the exact coordinator
decision that caused a coverage gap, a fix that closes it, a simulated failure
that degrades gracefully with visible annotation instead of silently vanishing or
crashing the whole pipeline, and a synthesis output that keeps disagreeing sources
disagreeing rather than averaging them into a false consensus.

---

## Why these two, and not something invented from scratch

Anthropic's own guide tells candidates to build exactly these two things before
sitting the exam. Building the actual homework — not a proxy for it — is the
highest-signal prep available short of the real exam itself.
