"""
Task Statement 1.1 — Design and implement agentic loops for autonomous task execution.

The loop lifecycle: send a request -> inspect stop_reason -> if "tool_use", run the
requested tool(s) and append results (matched by tool_use_id) -> send again -> repeat
until stop_reason is "end_turn".

This lab shows the anti-pattern failing first (offline, free, no API key needed),
then the correct implementation (needs a live, funded ANTHROPIC_API_KEY).

Run:  python lab1_agentic_loop.py
"""

from types import SimpleNamespace

from common import MODEL, call_claude, get_client

# ---------------------------------------------------------------------------
# A tiny local tool the agent can call. In production this would hit a real
# backend; here it's canned data so the lab is deterministic.
# ---------------------------------------------------------------------------
ORDERS = {
    "ORD-4471": {"status": "shipped", "carrier": "UPS", "eta": "2026-08-30"},
}

LOOKUP_ORDER_TOOL = {
    "name": "lookup_order",
    "description": "Look up the shipping status of an order by its order ID (format: ORD-####).",
    "input_schema": {
        "type": "object",
        "properties": {"order_id": {"type": "string"}},
        "required": ["order_id"],
    },
}


def lookup_order(order_id: str) -> dict:
    return ORDERS.get(order_id, {"error": f"no order found for {order_id}"})


# ---------------------------------------------------------------------------
# ANTI-PATTERNS (Task 1.1 "Skills": avoiding them) — demonstrated offline with
# fake response objects that mimic the real SDK's shape, so this half of the
# lab costs nothing and needs no API key.
# ---------------------------------------------------------------------------

def fake_tool_use_response() -> SimpleNamespace:
    """Mimics what the SDK returns when Claude decides to call a tool."""
    block = SimpleNamespace(type="tool_use", id="toolu_01Abc", name="lookup_order",
                             input={"order_id": "ORD-4471"})
    return SimpleNamespace(stop_reason="tool_use", content=[block])


def fake_end_turn_response() -> SimpleNamespace:
    block = SimpleNamespace(type="text", text="Your order ORD-4471 shipped via UPS, ETA Aug 30.")
    return SimpleNamespace(stop_reason="end_turn", content=[block])


def anti_pattern_parse_text_for_done() -> None:
    """WRONG: check assistant text content as a completion signal."""
    print("\n--- Anti-pattern 1: parsing text for a 'done' signal ---")
    response = fake_tool_use_response()
    try:
        # There is no text yet -- Claude just asked to call a tool. This is
        # exactly the "checking for assistant text content as a completion
        # indicator" anti-pattern the exam guide calls out.
        text = response.content[0].text
        print(f"  Parsed text: {text!r}")
    except AttributeError as e:
        print(f"  BROKE as expected: {type(e).__name__}: {e}")
        print("  The first content block is a tool_use block -- it has no .text.")
        print("  A loop that assumes text-first content silently mishandles this turn.")


def anti_pattern_iteration_cap() -> None:
    """WRONG: treat a hardcoded turn cap as the primary stopping mechanism."""
    print("\n--- Anti-pattern 2: hardcoded iteration cap as the stop condition ---")
    MAX_TURNS = 1  # looks reasonable, is not derived from stop_reason at all
    responses = [fake_tool_use_response(), fake_end_turn_response()]
    for turn in range(MAX_TURNS):
        response = responses[turn]
        print(f"  Turn {turn}: stop_reason={response.stop_reason!r} -- loop exits here (cap hit)")
    print("  BROKE as expected: stop_reason was still 'tool_use' when the cap stopped the loop.")
    print("  The tool call was never executed and the task never actually finished.")


# ---------------------------------------------------------------------------
# CORRECT implementation — needs a live, funded ANTHROPIC_API_KEY.
# ---------------------------------------------------------------------------

def run_agentic_loop(user_message: str) -> str:
    client = get_client()
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = call_claude(
            client,
            model=MODEL,
            tools=[LOOKUP_ORDER_TOOL],
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        print(f"  stop_reason = {response.stop_reason!r}")

        if response.stop_reason == "end_turn":
            final_text = "".join(b.text for b in response.content if b.type == "text")
            return final_text

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                print(f"  -> calling tool {block.name}({block.input}) [tool_use_id={block.id}]")
                if block.name == "lookup_order":
                    result = lookup_order(**block.input)
                else:
                    result = {"error": f"unknown tool {block.name}"}
                # The exact tool_use_id must round-trip back -- the API
                # rejects a mismatched or missing id.
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                })
            messages.append({"role": "user", "content": tool_results})
            continue

        raise RuntimeError(f"Unhandled stop_reason: {response.stop_reason}")


if __name__ == "__main__":
    anti_pattern_parse_text_for_done()
    anti_pattern_iteration_cap()

    print("\n--- Correct implementation: live call, driven by stop_reason ---")
    answer = run_agentic_loop("What's the status of order ORD-4471?")
    print(f"\n  Final answer: {answer}")
