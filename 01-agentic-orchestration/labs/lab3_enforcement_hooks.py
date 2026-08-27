"""
Task Statements 1.4 + 1.5 -- Implement multi-step workflows with enforcement
and handoff patterns; apply Agent SDK hooks for tool call interception and
data normalization.

This is the exact scenario the official CCAR-F exam guide uses as its first
sample question: a support agent that skips get_customer and calls
process_refund straight off a stated name, occasionally refunding the wrong
account. The guide's answer: a PROGRAMMATIC prerequisite gate, not a system
prompt instruction -- prompt-based compliance has a non-zero failure rate,
and refunds have financial consequences. This lab builds that gate for real,
plus a PostToolUse hook that normalizes a messy data format and a PreToolUse
hook that blocks refunds over a policy threshold.

Requires:  pip install claude-agent-sdk   (see lab2's docstring)
Run:       python lab3_enforcement_hooks.py
"""

import asyncio
from datetime import datetime, timezone

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    HookMatcher,
    ResultMessage,
    ToolUseBlock,
    create_sdk_mcp_server,
    query,
    tool,
)

REFUND_THRESHOLD_USD = 500

# Per-session state the hooks read/write. In a real deployment this would be
# a request-scoped object, not a module global -- kept simple here so the
# gate logic itself stays readable.
session_state = {"verified_customer_id": None}


# ---------------------------------------------------------------------------
# Two custom business tools (Task 1.4's get_customer / process_refund),
# wrapped in an in-process MCP server.
# ---------------------------------------------------------------------------

CUSTOMERS = {"Jordan Alvarez": {"customer_id": "CUST-9931", "joined_unix": 1706745600}}


@tool("get_customer", "Look up a customer by the name they provide and verify their identity.",
      {"customer_name": str})
async def get_customer(args):
    record = CUSTOMERS.get(args["customer_name"])
    if not record:
        return {"content": [{"type": "text", "text": "No matching customer found."}], "is_error": True}
    return {"content": [{"type": "text", "text": str(record)}]}


@tool("process_refund", "Refund an amount (USD) to a verified customer_id.",
      {"customer_id": str, "amount_usd": float})
async def process_refund(args):
    return {"content": [{"type": "text",
                          "text": f"Refunded ${args['amount_usd']:.2f} to {args['customer_id']}."}]}


support_server = create_sdk_mcp_server(name="support", version="1.0.0",
                                        tools=[get_customer, process_refund])


# ---------------------------------------------------------------------------
# Task 1.4 skill: programmatic prerequisite -- block process_refund until
# get_customer has returned a verified customer ID in THIS session.
# Task 1.5 skill: block refunds above a policy threshold, redirecting to
# escalation instead of just failing silently.
# ---------------------------------------------------------------------------

async def enforce_refund_prerequisites(input_data, tool_use_id, context):
    if input_data["tool_name"] != "mcp__support__process_refund":
        return {}

    tool_input = input_data["tool_input"]

    if session_state["verified_customer_id"] is None:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    "process_refund requires a verified customer_id from get_customer "
                    "first -- no verification has happened yet in this session."
                ),
            }
        }

    if tool_input.get("customer_id") != session_state["verified_customer_id"]:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"process_refund was called with customer_id={tool_input.get('customer_id')!r}, "
                    f"which doesn't match the verified customer_id "
                    f"{session_state['verified_customer_id']!r} from get_customer."
                ),
            }
        }

    if tool_input.get("amount_usd", 0) > REFUND_THRESHOLD_USD:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"Refunds over ${REFUND_THRESHOLD_USD} require human escalation "
                    f"per policy -- route this to escalate_to_human instead."
                ),
            }
        }

    return {}  # allow -- everything checked out


async def capture_verified_customer(input_data, tool_use_id, context):
    """PostToolUse: record the verified customer_id AND normalize the raw
    Unix-timestamp join date into ISO 8601 before Claude reasons about it
    (Task 1.5's data-normalization skill).

    Note: this re-derives the record from `tool_input` (the request we know
    we made) rather than parsing the tool's raw response text -- the exact
    dict key that carries a PostToolUse result varies by SDK version, so
    re-deriving from a value we already control is both simpler and more
    robust than parsing a string we don't have a pinned schema for. Check
    the current docs at /docs/en/hooks#posttooluse-input if you need the
    real response payload for a tool whose output you can't re-derive.
    """
    if input_data["tool_name"] != "mcp__support__get_customer":
        return {}

    customer_name = input_data["tool_input"].get("customer_name")
    record = CUSTOMERS.get(customer_name)
    if not record:
        return {}

    session_state["verified_customer_id"] = record["customer_id"]
    iso_joined = datetime.fromtimestamp(record["joined_unix"], tz=timezone.utc).isoformat()

    print(f"  [PostToolUse] normalized joined_unix={record['joined_unix']} -> {iso_joined}")
    print(f"  [PostToolUse] recorded verified customer_id={session_state['verified_customer_id']!r}")

    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": f"(normalized) customer joined_at: {iso_joined}",
        }
    }


async def run_support_agent(user_message: str) -> None:
    options = ClaudeAgentOptions(
        mcp_servers={"support": support_server},
        allowed_tools=["mcp__support__get_customer", "mcp__support__process_refund"],
        hooks={
            "PreToolUse": [HookMatcher(matcher="mcp__support__process_refund",
                                        hooks=[enforce_refund_prerequisites])],
            "PostToolUse": [HookMatcher(matcher="mcp__support__get_customer",
                                         hooks=[capture_verified_customer])],
        },
    )

    async for message in query(prompt=user_message, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"  -> {block.name}({block.input})")
        elif isinstance(message, ResultMessage) and message.subtype == "success":
            print(f"\nFinal answer: {message.result}")


if __name__ == "__main__":
    print("--- Scenario A: agent skips verification, tries a refund straight away ---")
    asyncio.run(run_support_agent(
        "Refund $75 to customer_id CUST-9931 for order ORD-4471 -- skip the lookup, I already know the ID."
    ))

    session_state["verified_customer_id"] = None  # reset between scenarios

    print("\n--- Scenario B: agent does it correctly (verify, then refund) ---")
    asyncio.run(run_support_agent(
        "Jordan Alvarez wants a $75 refund for order ORD-4471. Verify their identity first, then refund."
    ))

    session_state["verified_customer_id"] = None

    print("\n--- Scenario C: verified, but refund amount is over the $500 policy threshold ---")
    asyncio.run(run_support_agent(
        "Jordan Alvarez wants a $650 refund. Verify their identity first, then refund."
    ))
