# Claude Training — CCAR-F Hands-On Prep

Practical, code-first prep for the **Claude Certified Architect – Foundations (CCAR-F)** exam.

**One app, all 5 domains: [`app.html`](app.html).** Open it directly in a browser
(no build step, no login) — it has the concept for every task statement, a
step-through visualization, a "Run it for real" live demo you drive with your own
API key, the exact code behind each demo, and 44 original scenario-style practice
questions plus a scored full-exam quiz. CCAR-F questions are scenario-based
("given this production constraint, what do you design?"), not recall-based —
this is built to match that register, not to hand you flashcards.

> **Who this is for:** solution architects, AI/ML engineers, technical leads, and
> students who want to *build* their way to passing CCAR-F rather than memorize
> answers.

## Run it

```bash
# Recommended: serve it locally rather than opening the file directly --
# some browsers restrict outbound requests from file:// pages more than http://
python3 -m http.server 8000
# then open http://localhost:8000/app.html
```

Opening `app.html` directly (double-click, drag into a browser) also works in
most setups — try that first, and fall back to the local-server approach above
if the "Test connection" button in the Live API panel can't reach the API.

In the sidebar, open **Live API** and paste in your own Anthropic (or
Anthropic-compatible, e.g. Azure AI Foundry) key. It's sent straight from your
browser to the API and nowhere else — never written to a file, never committed,
never persisted unless you explicitly check "remember for this tab." Click
**Test connection** first to confirm it's wired up correctly before working
through the domains.

## Sourced from the official exam guide, not guesswork

The domain names, weights, and all 30 task statements come directly from
Anthropic's own **CCAR-F Exam Guide** (v1.0, effective July 2026) — downloaded
from the Anthropic Partner Academy and used to design this app's structure.
Anthropic's guide itself is not redistributed here (it's their copyrighted
material); everything in this repo — concepts, live demos, code, questions — is
original content built to teach the same mechanisms, not a copy of exam content.

## Exam snapshot

| | |
|---|---|
| Format | 60 items (multiple-choice / multiple-response), 4 scenarios drawn from a bank of 6 |
| Passing score | 720 / 1000 (scaled) |
| Time limit | 120 minutes |
| Validity | 12 months |

**Five domains**, official weights — the app is organized in this order:

| # | Domain | Weight |
|---|---|---|
| 1 | Agentic Architecture & Orchestration | 27% |
| 2 | Tool Design & MCP Integration | 18% |
| 3 | Claude Code Configuration & Workflows | 20% |
| 4 | Prompt Engineering & Structured Output | 20% |
| 5 | Context Management & Reliability | 15% |

## What's live vs. conceptual

Most task statements have a genuine **"Run it for real"** demo — an actual
`fetch()` call from your browser to the real Claude API, using the same logic
shown in the code panel underneath. Every one of these was independently
verified end-to-end before shipping (via a standalone Node script mirroring
the exact browser logic, since Node's `fetch` skips the browser-only CORS
enforcement that a real run needs to clear).

A few task statements are inherently **Claude Code CLI / config surface**, not
API calls — session resumption and forking (1.7), `.mcp.json` / `CLAUDE.md` /
path-scoped rules (2.4–3.3), CI/CD flags (3.6), and the Batches API's
async-by-design nature (4.5) don't have a meaningful "live in the browser"
version. Those get a `.claude/`-style config walkthrough instead, clearly
marked, with an honest note about why — not a fake live demo bolted on for the
sake of consistency.

## Repo structure

```
claude_training/
├── app.html                      # the whole exam — start here
├── 01-agentic-orchestration/     # Domain 1 supporting material
│   ├── README.md
│   ├── labs/                      # standalone Python labs (terminal-runnable)
│   ├── visualize/                  # the original single-domain visualizer
│   ├── scenario.md                 # two capstone builds (official prep exercises)
│   └── practice-questions.md       # Domain 1 questions in markdown form
└── .gitignore
```

Domains 2–5's content lives entirely inside `app.html` (concept, demo, code,
and questions together) rather than being split into per-domain folders — that
consolidation is deliberate, not a placeholder; see the "one UI" note below.

## Why one file instead of five folders

The very first version of this repo had one folder per domain, each with its
own scattered visualizer, lab files, and question set — and it was hard to use
for exactly that reason. Everything now lives in one self-contained page so
there's a single place to go, a single progress tracker, and a single Live API
connection that carries across every domain instead of being re-entered five
times.

## Contributing

Found a gap, a stale example, or want to add a scenario you got tripped up on in
practice? PRs welcome. Keep additions in the same style: a real, verified live
demo or a concrete scenario, plus the *why*, not just the *what* — and no
reproduced exam content, ever.

## Sources / further reading

- Anthropic, *Claude Certified Architect – Foundations Exam Guide*, v1.0
  (effective July 2026) — request it from the
  [official certification page](https://anthropic-partners.skilljar.com/claude-certified-architect-foundations-certification).
- [Claude Agent SDK documentation](https://code.claude.com/docs/en/agent-sdk/overview)
- [Claude API documentation](https://docs.claude.com)

> This repo is independent self-study material and is not affiliated with or
> endorsed by Anthropic. No Anthropic logos, brand artwork, or trade dress are
> used. Trademarks are used nominatively only. All content is original — no
> real exam content is reproduced.
