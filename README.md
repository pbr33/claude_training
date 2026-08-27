# Claude Training — CCAR-F Hands-On Prep

Practical, code-first prep for the **Claude Certified Architect – Foundations (CCAR-F)** exam.

This repo is not another slide deck. Every module ships with runnable labs, a
step-by-step visualization you can watch in a browser, real-world capstone builds
(including Anthropic's own official recommended prep exercises), and original
practice questions — because CCAR-F questions are scenario-based ("given this
production constraint, what do you design?"), not recall-based.

> **Who this is for:** solution architects, AI/ML engineers, technical leads, and
> students who want to *build* their way to passing CCAR-F rather than memorize
> flashcards.

## Sourced from the official exam guide, not guesswork

The domain names, weights, and task-statement breakdown below come directly from
Anthropic's own **CCAR-F Exam Guide** (v1.0, effective July 2026) — downloaded
from the Anthropic Partner Academy and used to design this repo's structure.
Anthropic's guide itself is not redistributed here (it's their copyrighted
material); everything in this repo — labs, scenarios, practice questions — is
original content built to teach the same mechanisms.

## Exam snapshot

| | |
|---|---|
| Format | 60 items (multiple-choice / multiple-response), 4 scenarios drawn from a bank of 6 |
| Passing score | 720 / 1000 (scaled) |
| Time limit | 120 minutes |
| Validity | 12 months |

**Five domains**, official weights:

| # | Domain | Weight | Status |
|---|---|---|---|
| 1 | Agentic Architecture & Orchestration | 27% | ✅ [`01-agentic-orchestration/`](01-agentic-orchestration/) |
| 2 | Tool Design & MCP Integration | 18% | coming next |
| 3 | Claude Code Configuration & Workflows | 20% | coming next |
| 4 | Prompt Engineering & Structured Output | 20% | coming next |
| 5 | Context Management & Reliability | 15% | coming next |

Modules are built largest-weight-first.

---

## Module 1 — Agentic Architecture & Orchestration (done)

The exam's biggest domain, and the first one built out in full: the agentic
loop's `stop_reason` mechanics, coordinator/subagent orchestration with the
Claude Agent SDK, `PreToolUse`/`PostToolUse` enforcement hooks, task
decomposition strategy, and session resumption/forking — each with a runnable
lab, an animated visualization, and original practice questions.

**Two capstones** in this module are original walkthroughs of exercises
Anthropic's own exam guide tells candidates to build before sitting the exam: a
multi-tool support agent with real escalation logic, and a multi-agent research
pipeline with error propagation and provenance tracking.

Start here: [`01-agentic-orchestration/README.md`](01-agentic-orchestration/README.md)

---

## Repo structure

```
claude_training/
├── 01-agentic-orchestration/    # Domain 1 — done
│   ├── README.md                 # task-statement → lab map
│   ├── labs/                     # runnable Python labs, one per task statement
│   ├── visualize/                 # agentic_loop.html — animated, opens in any browser
│   ├── scenario.md                # two capstone builds (official prep exercises)
│   └── practice-questions.md      # original scenario-style MCQs, tagged by lab
├── 02-tool-design-mcp/           # coming next
├── 03-claude-code-config/        # coming next
├── 04-prompt-engineering/        # coming next
└── 05-context-management/        # coming next
```

Each module folder is self-contained: read its `README.md`, then run the labs.

## How to use this repo

1. Start with the highest-weight module you haven't done yet (Module 1 first).
2. Run the labs — most call a real Claude API and print a step-by-step trace of
   what's actually happening on the wire, not just a final answer.
3. Open the module's `visualize/*.html` file directly in a browser — no server,
   no build step, no login.
4. Build the capstone(s) in `scenario.md` yourself before checking the practice
   questions.
5. Work `practice-questions.md` cold, then check your reasoning against the
   explanations — each question names the lab that proves its answer.

## Contributing

Found a gap, a stale example, or want to add a scenario you got tripped up on in
practice? PRs welcome. Keep additions in the same style: runnable code or a
concrete scenario, plus the *why*, not just the *what* — and no reproduced exam
content, ever.

## Sources / further reading

- Anthropic, *Claude Certified Architect – Foundations Exam Guide*, v1.0
  (effective July 2026) — request it from the
  [official certification page](https://anthropic-partners.skilljar.com/claude-certified-architect-foundations-certification).
- [Claude Agent SDK documentation](https://code.claude.com/docs/en/agent-sdk/overview)
- [Claude API documentation](https://docs.claude.com)

> This repo is independent self-study material and is not affiliated with or
> endorsed by Anthropic. No Anthropic logos, brand artwork, or trade dress are
> used. Trademarks are used nominatively only. All labs, scenarios, and practice
> questions are original — no real exam content is reproduced.
