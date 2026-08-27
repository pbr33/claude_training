# Task Statements 3.1–3.3 — CLAUDE.md hierarchy, commands, skills & path-scoped rules

A hands-on walkthrough using a real (if fictional) small project, `orderflow`, an
internal order-processing API. You build the actual files below, then use the
real Claude Code CLI to confirm each mechanism behaves the way the exam guide
says it does. No API key needed for any of this — it's all Claude Code
configuration, not API calls.

> Original lab content. `orderflow` is a fictional project created for this
> exercise — nothing here reproduces any exam content.

## 1. Set up the project

```bash
mkdir orderflow && cd orderflow
git init
mkdir -p src/payments src/utils .claude/rules .claude/commands .claude/skills
```

## 2. The three CLAUDE.md scopes

### Project scope (shared — this is what your whole team gets)

```bash
cat > CLAUDE.md <<'EOF'
# orderflow

- Use TypeScript strict mode everywhere.
- Run `npm test` before considering any change done.
- Prefer editing existing files over creating new ones.
EOF
```

### Directory scope (shared, but scoped to one sensitive area)

```bash
cat > src/payments/CLAUDE.md <<'EOF'
# src/payments/ — extra caution required

- Never log a full card number, even in debug output.
- Any change here needs an explicit "why is this safe" comment in the diff.
EOF
```

### User scope (personal — never commit this)

```bash
mkdir -p ~/.claude
cat >> ~/.claude/CLAUDE.md <<'EOF'

# Personal preferences (orderflow)
- I prefer functional components over class components.
EOF
```

**Try it:** run `claude` from the `orderflow` root and ask `What does CLAUDE.md say about testing?` Then `cd src/payments` and ask `claude` (fresh session) `What does CLAUDE.md say about card numbers?` — it should mention it now, but wouldn't have from the project root, since the directory-level file only loads once Claude actually reads/edits something in that subtree.

**Confirm what actually loaded** with `/context` inside a session — look for the "Memory files" section. This is the fast way to debug "why isn't Claude following X" without guessing.

## 3. The "new teammate" bug, reproduced on purpose

Your personal preference about functional components lives in `~/.claude/CLAUDE.md` — it will **never** reach a teammate, because that file isn't in the repo at all (check `git status`; it won't show up as untracked either, since it's outside the project directory entirely).

**Try it:** move that bullet from `~/.claude/CLAUDE.md` into the project's `CLAUDE.md` instead. Now it's committed, and `git log` on a teammate's clone would show it arriving. That's the fix for "a new teammate isn't getting an instruction everyone else follows" — it's almost always this exact scope mistake.

## 4. `@import` — organizing, not reducing context

```bash
cat > STYLE_GUIDE.md <<'EOF'
# Style guide
- 2-space indentation.
- No default exports.
- Prefer named function declarations over arrow-function consts for top-level functions.
EOF

cat > CLAUDE.md <<'EOF'
# orderflow

@STYLE_GUIDE.md

- Run `npm test` before considering any change done.
EOF
```

**Try it:** run `/context` again. `STYLE_GUIDE.md`'s content is now part of what's loaded, exactly as if you'd pasted it into `CLAUDE.md` directly — same context cost, just organized into a separate, easier-to-review file. This is the trap: splitting into `@import`s feels like it should reduce context. It doesn't. Only rules below actually do that.

## 5. `.claude/rules/` — the one that actually loads conditionally

```bash
cat > .claude/rules/testing.md <<'EOF'
---
paths: ["**/*.test.ts"]
---

# Testing conventions
- Every test file starts with a comment naming the function under test.
- Use describe/it, never a bare test().
EOF

# a file that matches...
touch src/payments/refund.test.ts
# ...and one that doesn't
touch src/payments/refund.ts
```

**Try it:** start a fresh session and ask Claude to read `src/payments/refund.ts` (the non-test file). Check `/context` — the testing rule should **not** appear. Now ask it to read `refund.test.ts` instead, fresh session. Check `/context` again — now it does. That's the real context saving `@import` doesn't give you: a session that never touches a test file never pays for the testing conventions at all.

## 6. Commands: shared vs. personal

```bash
mkdir -p .claude/commands
cat > .claude/commands/review.md <<'EOF'
Review the current diff for bugs, security issues, and style-guide violations.
Report findings as a bulleted list, most severe first.
EOF

mkdir -p ~/.claude/commands
cat > ~/.claude/commands/todo.md <<'EOF'
Scan the current diff for any new TODO comments and list them with file:line.
EOF
```

**Try it:** `/review` works for anyone who clones this repo (it's in `.claude/commands/`, which you'll `git add`). `/todo` only works for you — it's outside the repo entirely, same as the user-scope CLAUDE.md above.

## 7. A skill with `context: fork`, `allowed-tools`, and `argument-hint`

```bash
mkdir -p .claude/skills/audit-dependencies
cat > .claude/skills/audit-dependencies/SKILL.md <<'EOF'
---
description: Audit dependencies for known vulnerabilities and outdated majors
context: fork
allowed-tools: Read, Bash
argument-hint: [package-name]
---

Run `npm audit` and `npm outdated`, cross-reference against package.json, and
report findings grouped by severity. If [package-name] is given, focus only
on that package and its transitive dependents.
EOF
```

**Try it:** run `/audit-dependencies` with no argument — Claude Code should prompt you for `[package-name]` rather than guessing one. Then run it for real (needs an actual `package.json` — `npm init -y` first if you don't have one). Notice that the (potentially long) `npm audit`/`npm outdated` output doesn't dump into your main conversation — you get a synthesized summary back, because `context: fork` ran the skill in its own isolated sub-conversation. Try removing `allowed-tools` entirely and re-running: the skill can now use whatever the main session can, including `Edit` — a materially different, less contained skill.

## Commit what belongs in version control

```bash
git add CLAUDE.md STYLE_GUIDE.md src/payments/CLAUDE.md \
  .claude/rules/testing.md .claude/commands/review.md \
  .claude/skills/audit-dependencies/SKILL.md
git status   # confirm ~/.claude/CLAUDE.md and ~/.claude/commands/todo.md never appear here
git commit -m "Configure orderflow's Claude Code setup"
```

## Exam traps this lab makes concrete

- **`@import` organizes; it does not reduce context.** Only `paths:`-scoped rules load conditionally.
- **Directory-level CLAUDE.md loads on demand** (when Claude touches a file in that subtree), not at session start — unlike the project-root file, which always loads.
- **User-scope files (CLAUDE.md and commands) are invisible to teammates by construction** — they're not even in the repo, so there's nothing to `git status` or forget to commit.
- **`context: fork` isolates a skill's own exploration/output**, not just its tools — the main conversation gets a summary, not the raw noise.
