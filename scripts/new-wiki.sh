#!/usr/bin/env bash
#
# new-wiki.sh — Spawn a new wiki from the wiki-base/ skeleton.
#
# Usage:
#   scripts/new-wiki.sh <target-dir> [--git] [--force]
#
# Copies wiki-base/ (schema, templates, skills, empty index/log/synthesis)
# to <target-dir>, excluding smoke-test leftovers. Creates the wiki
# subdirectories (entities, concepts, sources, comparisons) and
# raw/assets/ so the vault is ready for /wiki-ingest.
#
# With --git, initializes a fresh git repo in <target-dir> and commits
# the skeleton. With --force, overwrites an existing <target-dir>.

set -euo pipefail

usage() {
  sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-1}"
}

TARGET=""
INIT_GIT=0
FORCE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --git) INIT_GIT=1; shift ;;
    --force) FORCE=1; shift ;;
    -h|--help) usage 0 ;;
    -*) echo "unknown flag: $1" >&2; usage ;;
    *)
      if [[ -n "$TARGET" ]]; then
        echo "too many positional args" >&2; usage
      fi
      TARGET="$1"; shift ;;
  esac
done

[[ -n "$TARGET" ]] || usage

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC="$REPO_ROOT/wiki-base"

[[ -d "$SRC" ]] || { echo "source skeleton not found: $SRC" >&2; exit 2; }

if [[ -e "$TARGET" ]]; then
  if [[ "$FORCE" -eq 1 ]]; then
    rm -rf "$TARGET"
  else
    echo "target already exists: $TARGET (pass --force to overwrite)" >&2
    exit 2
  fi
fi

mkdir -p "$TARGET"
TARGET_ABS="$(cd "$TARGET" && pwd)"

# rsync copies everything under wiki-base/ except:
#   - .DS_Store (macOS noise)
#   - any source files in raw/ (keep raw/assets/ but not any .md/.pdf etc.)
#   - any populated wiki subdirs (entities/concepts/sources/comparisons)
#   - .claude/settings.local.json (user-local)
rsync -a \
  --exclude='.DS_Store' \
  --exclude='raw/*' \
  --include='raw/assets/' \
  --exclude='wiki/entities/***' \
  --exclude='wiki/concepts/***' \
  --exclude='wiki/sources/***' \
  --exclude='wiki/comparisons/***' \
  --exclude='.claude/settings.local.json' \
  "$SRC/" "$TARGET_ABS/"

# Create the empty subdirectories the ingest skill expects.
mkdir -p \
  "$TARGET_ABS/raw/assets" \
  "$TARGET_ABS/wiki/entities" \
  "$TARGET_ABS/wiki/concepts" \
  "$TARGET_ABS/wiki/sources" \
  "$TARGET_ABS/wiki/comparisons"

# Keep empty dirs in git by dropping .gitkeep.
for d in raw/assets wiki/entities wiki/concepts wiki/sources wiki/comparisons; do
  touch "$TARGET_ABS/$d/.gitkeep"
done

# Substitute {{date}} placeholders in wiki/synthesis.md so the spawned
# vault passes wiki-lint on day 1. Templates in templates/ keep {{date}}
# — those are instantiated by the Obsidian Templates plugin on create.
TODAY="$(date +%Y-%m-%d)"
if [[ -f "$TARGET_ABS/wiki/synthesis.md" ]]; then
  # portable in-place sed (macOS + linux)
  sed -i.bak "s/{{date}}/$TODAY/g" "$TARGET_ABS/wiki/synthesis.md"
  rm -f "$TARGET_ABS/wiki/synthesis.md.bak"
fi

if [[ "$INIT_GIT" -eq 1 ]]; then
  (
    cd "$TARGET_ABS"
    git init -q
    git add .
    git -c user.email=wiki@local -c user.name=wiki \
      commit -q -m "Initial wiki skeleton from wiki-base/"
  )
fi

cat <<EOF

Wiki skeleton created at: $TARGET_ABS

Next:
  1. Run $TARGET_ABS/scripts/wiki-doctor.sh
  2. If you plan to ingest PDFs:
     python3 -m pip install -r $TARGET_ABS/requirements.txt
  3. Edit $TARGET_ABS/purpose.md — describe your research direction.
  4. Drop a source file in $TARGET_ABS/raw/ (PDF or markdown).
  5. Open the vault in Obsidian (optional, for browsing).
  6. From $TARGET_ABS, run Claude Code and invoke /wiki-ingest <raw/your-source>.

EOF
