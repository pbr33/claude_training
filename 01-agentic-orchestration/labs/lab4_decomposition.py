"""
Task Statement 1.6 -- Design task decomposition strategies for complex
workflows: fixed sequential pipelines (prompt chaining) vs. dynamic adaptive
decomposition.

Same underlying task -- review three files for issues -- solved two ways:

1. PROMPT CHAINING: a fixed, predictable pipeline. Analyze each file with
   its own call, then a separate cross-file integration pass. Good when the
   steps are knowable in advance (Task 1.6's example: per-file review, then
   integration).

2. DYNAMIC DECOMPOSITION: the model itself decides what to look at next
   based on what it just found, via tool use. Good for open-ended
   investigation where the steps can't be predetermined.

This lab uses the raw Messages API (like lab1) since decomposition strategy
is a prompting/architecture decision, not an SDK-specific feature -- it runs
live with just `pip install anthropic`.

Run:  python lab4_decomposition.py
"""

from common import MODEL, call_claude, get_client

FILES = {
    "auth.py": (
        "def check_login(user, pw):\n"
        "    if user.password == pw:  # plaintext comparison, no hashing\n"
        "        return True\n"
        "    return False\n"
    ),
    "session.py": (
        "def new_session(user):\n"
        "    token = str(random.randint(0, 999999))  # low-entropy token\n"
        "    sessions[token] = user\n"
        "    return token\n"
    ),
    "logout.py": (
        "def logout(token):\n"
        "    pass  # sessions dict is never cleared -- tokens live forever\n"
    ),
}


# ---------------------------------------------------------------------------
# Strategy 1: prompt chaining -- fixed, ordered, predictable
# ---------------------------------------------------------------------------

def review_via_chaining() -> None:
    client = get_client()
    per_file_findings = {}

    print("--- Pass 1: per-file local analysis (one call per file) ---")
    for filename, code in FILES.items():
        response = call_claude(client, messages=[{
            "role": "user",
            "content": f"Review this file for security issues. Be terse.\n\n{filename}:\n{code}",
        }])
        finding = "".join(b.text for b in response.content if b.type == "text")
        per_file_findings[filename] = finding
        print(f"  {filename}: {finding.strip()[:120]}...")

    print("\n--- Pass 2: separate cross-file integration pass ---")
    combined = "\n\n".join(f"{f}:\n{c}" for f, c in FILES.items())
    response = call_claude(client, messages=[{
        "role": "user",
        "content": (
            "These files were already reviewed individually. Now look ACROSS "
            f"them for issues that only show up when you consider them together "
            f"(e.g. a session token format that's fine alone but weak given how "
            f"another file uses it):\n\n{combined}"
        ),
    }])
    cross_file = "".join(b.text for b in response.content if b.type == "text")
    print(f"  Cross-file finding: {cross_file.strip()[:300]}")


# ---------------------------------------------------------------------------
# Strategy 2: dynamic decomposition -- the model chooses what to open next
# ---------------------------------------------------------------------------

READ_FILE_TOOL = {
    "name": "read_file",
    "description": "Read the contents of one file from the small codebase being audited.",
    "input_schema": {
        "type": "object",
        "properties": {"filename": {"type": "string", "enum": list(FILES.keys())}},
        "required": ["filename"],
    },
}


def review_via_dynamic_decomposition() -> None:
    client = get_client()
    messages = [{
        "role": "user",
        "content": (
            "You're auditing a small codebase for security issues. Available files: "
            f"{list(FILES.keys())}. Read whichever files you need, in whatever order "
            "makes sense given what you find -- you don't know the dependencies "
            "between them ahead of time. When you're confident you've found the "
            "real issues, summarize them."
        ),
    }]

    while True:
        response = call_claude(client, tools=[READ_FILE_TOOL], messages=messages)
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            final = "".join(b.text for b in response.content if b.type == "text")
            print(f"  Final summary: {final.strip()[:400]}")
            return

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            filename = block.input["filename"]
            print(f"  -> model chose to read {filename!r} next")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": FILES[filename],
            })
        messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    review_via_chaining()
    print("\n" + "=" * 70)
    print("--- Dynamic decomposition: model picks its own investigation order ---")
    review_via_dynamic_decomposition()
