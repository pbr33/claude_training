"""
Task Statements 1.2 + 1.3 — Orchestrate multi-agent systems with a coordinator-
subagent (hub-and-spoke) pattern, and configure subagent invocation, context
passing, and spawning.

Unlike lab1 (which hand-rolls a loop against the raw Messages API), this lab
uses the Claude Agent SDK's query() -- the same engine that powers Claude
Code -- which runs the agentic loop AND subagent orchestration for you.

Naming note (a real, current gotcha, not a typo): the exam guide's blueprint
calls this the "Task tool" and says a coordinator's allowedTools must include
"Task". Claude Code v2.1.63 renamed the tool emitted in tool_use blocks from
"Task" to "Agent" -- but "Task" still appears in the system:init tools list
and in result.permission_denials[].tool_name. For the exam, know it as the
Task mechanism. For code that runs today, put "Agent" in allowed_tools and
check block.name against BOTH "Task" and "Agent" when detecting invocation --
exactly as this lab does below.

Requires:  pip install claude-agent-sdk   (plus the Claude Code CLI configured
           with credentials -- this SDK shells out to it, unlike lab1's
           direct HTTPS calls via the `anthropic` package)
Run:       python lab2_coordinator_subagents.py
"""

import asyncio

from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions, ToolUseBlock, query

# ---------------------------------------------------------------------------
# A tiny local "web" the subagents search over, so the lab is deterministic
# and needs no external search API key. Each subagent gets ONLY the prompt
# string we hand it -- Task 1.3's key point: subagents do not automatically
# inherit the coordinator's conversation or memory.
# ---------------------------------------------------------------------------
SOURCES = {
    "src-1": "A 2026 survey of 4,000 developers found AI code assistants cut "
             "time-to-first-PR by 35% for engineers with under 2 years of tenure.",
    "src-2": "Senior engineers (8+ years) reported only an 8% time reduction, "
             "and 20% reported net-negative productivity from review overhead.",
    "src-3": "Teams using AI assistants shipped 22% more PRs per sprint but "
             "saw a 14% rise in post-merge bug-fix commits in the same period.",
}


# ---------------------------------------------------------------------------
# Task 1.2 skill: partition research scope across subagents to minimize
# duplication, rather than pointing every subagent at the whole topic.
# ---------------------------------------------------------------------------
RESEARCH_SUBAGENT = AgentDefinition(
    description="Searches the internal source corpus for a specific research subtopic.",
    prompt=(
        "You are a research subagent. You will be given ONE narrow subtopic "
        "to investigate. Read the sources available to you and report only "
        "findings relevant to your assigned subtopic, each tagged with its "
        "source id (e.g. src-1) so attribution survives synthesis. Do not "
        "speculate beyond what the sources say."
    ),
    tools=["Read"],
    model="sonnet",
)

SYNTHESIS_SUBAGENT = AgentDefinition(
    description="Combines findings from research subagents into a coherent, cited summary.",
    prompt=(
        "You are a synthesis subagent. You will be given findings collected "
        "by other subagents, each already tagged with a source id. Combine "
        "them into a short report. If two findings conflict, keep both and "
        "annotate the conflict with both source ids rather than picking one."
    ),
    tools=[],
    model="sonnet",
)


async def run_research_coordinator(topic: str) -> None:
    options = ClaudeAgentOptions(
        # "Agent" is what current SDK versions check for tool_use invocation.
        # Some teams also allow "Task" for compatibility with the exam's
        # documented name and with permission_denials[].tool_name.
        allowed_tools=["Read", "Agent"],
        agents={
            "research-subagent": RESEARCH_SUBAGENT,
            "synthesis-subagent": SYNTHESIS_SUBAGENT,
        },
    )

    prompt = (
        f"Research this topic using the research-subagent and synthesis-subagent: {topic}\n\n"
        "Available sources (pass the relevant ones' content directly into each "
        "subagent's prompt -- they cannot see this message):\n"
        + "\n".join(f"- {sid}: {text}" for sid, text in SOURCES.items())
        + "\n\nPartition the sources across at least two research-subagent calls "
          "by distinct angle (e.g. junior vs. senior developer impact, velocity vs. "
          "quality) so no single subagent has to cover everything. Emit those "
          "research-subagent calls in parallel, then pass their findings to "
          "synthesis-subagent to produce the final cited report."
    )

    print(f"--- Coordinator prompt sent. Watching for subagent invocations... ---\n")

    async for message in query(prompt=prompt, options=options):
        for block in getattr(message, "content", None) or []:
            if isinstance(block, ToolUseBlock) and block.name in ("Task", "Agent"):
                subagent_type = block.input.get("subagent_type", "?")
                print(f"  -> coordinator spawned subagent: {subagent_type!r}")

        if getattr(message, "parent_tool_use_id", None):
            print("     (message generated inside a subagent's own context)")

        if hasattr(message, "result"):
            print("\n--- Final synthesized report ---\n")
            print(message.result)


if __name__ == "__main__":
    asyncio.run(run_research_coordinator(
        "How do AI code assistants affect developer productivity?"
    ))
