#!/usr/bin/env bash
#
# wiki-doctor.sh — Health-check a spawned LLM Wiki vault.
#
# Usage:
#   scripts/wiki-doctor.sh [vault-dir]
#
# Defaults to the current directory. Fails only on structural problems or
# lint findings; missing optional tooling is reported as a warning.

set -euo pipefail

usage() {
  sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-1}"
}

TARGET="${1:-.}"
case "$TARGET" in
  -h|--help) usage 0 ;;
esac

ROOT="$(cd "$TARGET" && pwd)"
FAILURES=0
WARNINGS=0

say_ok() {
  printf 'OK   %s: %s\n' "$1" "$2"
}

say_warn() {
  WARNINGS=$((WARNINGS + 1))
  printf 'WARN %s: %s\n' "$1" "$2"
}

say_fail() {
  FAILURES=$((FAILURES + 1))
  printf 'FAIL %s: %s\n' "$1" "$2"
}

if [[ ! -d "$ROOT/wiki" ]]; then
  say_fail "vault" "no wiki/ directory under $ROOT"
fi
if [[ ! -f "$ROOT/CLAUDE.md" ]]; then
  say_fail "vault" "missing CLAUDE.md under $ROOT"
fi
if [[ ! -f "$ROOT/purpose.md" ]]; then
  say_fail "vault" "missing purpose.md under $ROOT"
fi
if [[ ! -f "$ROOT/scripts/wiki-lint.py" ]]; then
  say_fail "vault" "missing scripts/wiki-lint.py under $ROOT"
fi

if [[ "$FAILURES" -gt 0 ]]; then
  printf '\nWiki doctor: FAIL (%s failure(s), %s warning(s))\n' \
    "$FAILURES" "$WARNINGS"
  exit 1
fi

if command -v python3 >/dev/null 2>&1; then
  say_ok "python3" "$(command -v python3)"
else
  say_fail "python3" "python3 not found on PATH"
fi

if command -v git >/dev/null 2>&1; then
  if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    say_ok "git" "vault is in a git worktree"
  else
    say_warn "git" "vault is not in a git worktree (--git is optional)"
  fi
else
  say_warn "git" "git not found on PATH"
fi

if command -v claude >/dev/null 2>&1; then
  say_ok "claude" "$(command -v claude)"
else
  say_warn "claude" "Claude Code CLI not found on PATH"
fi

if command -v obsidian >/dev/null 2>&1; then
  say_ok "obsidian" "$(command -v obsidian)"
else
  say_warn "obsidian" "Obsidian CLI not found on PATH (optional)"
fi

if command -v python3 >/dev/null 2>&1; then
  LINT_OUTPUT="$(mktemp)"
  if python3 "$ROOT/scripts/wiki-lint.py" --vault "$ROOT" >"$LINT_OUTPUT" 2>&1; then
    say_ok "lint" "$(tail -n 1 "$LINT_OUTPUT")"
  else
    say_fail "lint" "$(tr '\n' ' ' < "$LINT_OUTPUT" | sed 's/[[:space:]]\+/ /g' | sed 's/^ //; s/ $//')"
  fi
  rm -f "$LINT_OUTPUT"

  if python3 -c "import pymupdf4llm" >/dev/null 2>&1; then
    say_ok "pdf" "pymupdf4llm is installed"
  else
    say_warn "pdf" "PDF ingest unavailable; run \`python3 -m pip install -r requirements.txt\`"
  fi
fi

if [[ -f "$ROOT/purpose.md" ]]; then
  if grep -Eq '^> TBD$|^1\.$|^2\.$|^3\.$' "$ROOT/purpose.md"; then
    say_warn "purpose" "purpose.md still contains placeholder content"
  else
    say_ok "purpose" "purpose.md looks customized"
  fi
fi

printf '\n'
if [[ "$FAILURES" -gt 0 ]]; then
  printf 'Wiki doctor: FAIL (%s failure(s), %s warning(s))\n' \
    "$FAILURES" "$WARNINGS"
  exit 1
fi

printf 'Wiki doctor: OK (%s warning(s))\n' "$WARNINGS"
