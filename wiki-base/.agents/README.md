# Codex Workflow Briefs

This directory contains Codex-facing workflow briefs for the generated
wiki. Start with `AGENTS.md`, then use the relevant file here for the
specific operation.

These files are deliberately generic:

- They do not rely on tool-specific frontmatter.
- They assume only ordinary file reads, file edits, and shell commands
  available in the current Codex environment.
- Workflow labels like `wiki-ingest` and `wiki-query` are names, not
  required slash commands.
- Role files under `.agents/agents/` can be used as separate roles when
  the environment supports delegation. Otherwise, perform the role
  yourself while preserving its contract.
- `CLAUDE.md` remains the canonical schema for page structure, claim
  typing, and graph rules.
