"""Shared helpers for the agentic-orchestration labs.

Every lab imports get_client() and call_claude() from here so the same
one-line, no-stack-trace error handling applies everywhere: missing
ANTHROPIC_API_KEY, invalid key, or an account with no credit balance
should never crash a student's first run.
"""

import os
import sys

import anthropic

# Claude's output can include characters outside the Windows console's
# default cp1252 encoding (emoji, some symbols). Reconfigure stdout to UTF-8
# so a lab doesn't crash on print() -- this is a Windows console quirk, not
# an agentic-loop concept, so it's tucked away here rather than in each lab.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Override with ANTHROPIC_MODEL if your deployment uses a different model id
# (e.g. an Azure AI Foundry Claude deployment named "claude-sonnet-4-6" rather
# than "claude-sonnet-5").
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")


def get_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit(
            "No ANTHROPIC_API_KEY in the environment.\n"
            "Set it first:  export ANTHROPIC_API_KEY=sk-ant-...   (never hardcode it in a file)\n"
            "Using an Anthropic-compatible endpoint (e.g. Azure AI Foundry)? Also set:\n"
            "  export ANTHROPIC_BASE_URL=https://<your-resource>.services.ai.azure.com/anthropic\n"
            "  export ANTHROPIC_MODEL=<your-deployment-name>"
        )
    # base_url defaults to api.anthropic.com; set ANTHROPIC_BASE_URL to point
    # at any Anthropic-wire-compatible endpoint instead (same request/response
    # shape, different host -- e.g. an Azure AI Foundry Claude deployment).
    base_url = os.environ.get("ANTHROPIC_BASE_URL")
    return anthropic.Anthropic(api_key=api_key, base_url=base_url)


def call_claude(client: anthropic.Anthropic, **kwargs):
    """messages.create with friendly errors instead of a raw traceback."""
    kwargs.setdefault("model", MODEL)
    kwargs.setdefault("max_tokens", 1024)
    try:
        return client.messages.create(**kwargs)
    except anthropic.AuthenticationError:
        sys.exit("Auth failed — the API key is invalid or revoked.")
    except anthropic.BadRequestError as e:
        if "credit balance" in str(e).lower():
            sys.exit(
                "This key has no credit balance, so the live call can't run.\n"
                "Add credits at console.anthropic.com/settings/billing, then re-run this lab.\n"
                f"(Raw error: {e})"
            )
        raise
