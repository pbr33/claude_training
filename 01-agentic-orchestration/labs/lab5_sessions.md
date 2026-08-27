# Task Statement 1.7 — Manage session state, resumption, and forking

This one isn't a Python lab — session resumption and forking are **Claude Code CLI**
features, not raw Messages API concepts. Run these commands yourself in a terminal,
inside any git repo, to see the mechanics for real.

## 1. Named session resumption

Start a named investigation, then walk away and come back to it later:

```bash
claude --session-name "auth-audit" -p "Read auth.py and list every security issue you find."
```

Close the terminal. Tomorrow, continue the *same* conversation — Claude still has
everything from the first pass:

```bash
claude --resume "auth-audit" -p "Now check whether session.py compounds any of those issues."
```

**The exam-relevant judgment call:** if `auth.py` hasn't changed since the first
pass, `--resume` is the right move — the prior analysis is still valid, and
re-reading it from scratch wastes tokens re-deriving facts you already have. If
`auth.py` *has* changed, tell the resumed session exactly what changed and why,
so it does a **targeted re-read** instead of quietly reasoning from stale
findings:

```bash
claude --resume "auth-audit" -p "auth.py changed since we last looked — the password check now uses bcrypt (see the diff below). Re-check just that function; the rest of your prior findings still stand.

<paste diff>"
```

## 2. When resuming is the WRONG call

If a lot has changed, or the prior session's tool results are simply stale (a
different branch, a refactor that moved files around), starting **fresh with an
injected summary** is more reliable than resuming and hoping Claude reconciles
stale context correctly on its own:

```bash
claude -p "Here's a summary of a prior audit of this codebase: <paste the key
findings, not the raw transcript>. The codebase has since been refactored —
treat this as background, not current fact, and re-verify anything load-bearing."
```

This is the same principle as Domain 5's "lost in the middle" / context-rot
material: a long stale history competing for attention is worse than a short,
curated summary of what's still true.

## 3. Forking — divergent branches from one shared baseline

`fork_session` lets you explore two different approaches from the *same*
starting point without re-doing the shared analysis twice. Do the shared
groundwork once:

```bash
claude --session-name "refactor-baseline" -p "Analyze session.py's token generation and summarize the weaknesses."
```

Then fork it two ways to compare strategies, each branch inheriting everything
above but diverging from there:

```bash
claude --resume "refactor-baseline" --fork-session --session-name "refactor-secrets-token" \
  -p "Propose a fix using Python's secrets module."

claude --resume "refactor-baseline" --fork-session --session-name "refactor-jwt" \
  -p "Propose a fix using signed JWTs instead."
```

Both forks share the same baseline analysis (no duplicated work) but can be
compared side by side without either polluting the other's reasoning.

## Try it yourself

1. Pick any small local repo (or use the `01-agentic-orchestration/labs/` files
   in this module).
2. Run a named session, close the terminal, resume it the next day, and confirm
   it remembers.
3. Deliberately edit a file the session already analyzed, resume, and check
   whether an *un-briefed* resume gives a subtly wrong answer versus a
   *briefed* one that names the change.
4. Fork a session two ways and compare how the branches diverge.

## Exam trap to know

"Just resume and let Claude figure out what changed" is the wrong answer
whenever a scenario says files changed since the last session — the guide is
explicit that you must inform the resumed session about the change so it does
a targeted re-read, not silent reasoning from stale tool results.
