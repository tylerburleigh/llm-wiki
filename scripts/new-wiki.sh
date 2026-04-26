#!/usr/bin/env bash
#
# new-wiki.sh — Spawn a new wiki from the wiki-base/ skeleton.
#
# Usage:
#   scripts/new-wiki.sh <target-dir> [--git] [--force | --into]
#
# Copies wiki-base/ (schema, templates, skills, empty index/log/synthesis)
# to <target-dir>, excluding smoke-test leftovers. Creates the wiki
# subdirectories (entities, concepts, sources, comparisons) and
# raw/assets/ so the vault is ready for /wiki-ingest.
#
# With --git, initializes a fresh git repo in <target-dir> and commits
# the skeleton (or stages + commits the additions if <target-dir> is
# already a git repo).
# With --force, overwrites an existing <target-dir> (destructive).
# With --into, merges the skeleton into an existing <target-dir> without
# overwriting any existing files. Target must already exist.
# --force and --into are mutually exclusive.

set -euo pipefail

usage() {
  sed -n '2,19p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-1}"
}

TARGET=""
INIT_GIT=0
FORCE=0
INTO=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --git) INIT_GIT=1; shift ;;
    --force) FORCE=1; shift ;;
    --into) INTO=1; shift ;;
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

if [[ "$FORCE" -eq 1 && "$INTO" -eq 1 ]]; then
  echo "--force and --into are mutually exclusive" >&2
  exit 2
fi

# Resolve this script's real location, following symlinks (e.g. when
# invoked via ~/.local/bin/llm-wiki-new -> scripts/new-wiki.sh).
SOURCE="${BASH_SOURCE[0]}"
while [[ -L "$SOURCE" ]]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ "$SOURCE" != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC="$REPO_ROOT/wiki-base"

[[ -d "$SRC" ]] || { echo "source skeleton not found: $SRC" >&2; exit 2; }

if [[ -e "$TARGET" ]]; then
  if [[ "$FORCE" -eq 1 ]]; then
    rm -rf "$TARGET"
  elif [[ "$INTO" -eq 1 ]]; then
    [[ -d "$TARGET" ]] || {
      echo "--into requires target to be a directory: $TARGET" >&2
      exit 2
    }
  else
    echo "target already exists: $TARGET (pass --into to merge, or --force to overwrite)" >&2
    exit 2
  fi
elif [[ "$INTO" -eq 1 ]]; then
  echo "--into requires an existing target dir: $TARGET" >&2
  exit 2
fi

mkdir -p "$TARGET"
TARGET_ABS="$(cd "$TARGET" && pwd)"

# Remember which singleton files were already present before rsync so we
# don't rewrite {{date}} placeholders in user-authored files.
DATE_FILES=(
  "wiki/synthesis.md"
  "wiki/handoff.md"
  "wiki/backlog.md"
  "wiki/decisions.md"
  "wiki/docs/graph-protocol.md"
)
declare -a PRE_EXISTED
for i in "${!DATE_FILES[@]}"; do
  PRE_EXISTED[$i]=0
  if [[ "$INTO" -eq 1 && -f "$TARGET_ABS/${DATE_FILES[$i]}" ]]; then
    PRE_EXISTED[$i]=1
  fi
done

# rsync copies everything under wiki-base/ except:
#   - .DS_Store (macOS noise)
#   - any source files in raw/ (keep raw/assets/ but not any .md/.pdf etc.)
#   - any populated wiki subdirs (entities/concepts/sources/comparisons)
#   - .claude/settings.local.json (user-local)
# With --into, --ignore-existing preserves any files already in target.
RSYNC_FLAGS=(
  -a
  --exclude='.DS_Store'
  --exclude='raw/*'
  --include='raw/assets/'
  --exclude='wiki/entities/***'
  --exclude='wiki/concepts/***'
  --exclude='wiki/sources/***'
  --exclude='wiki/comparisons/***'
  --exclude='.claude/settings.local.json'
)
if [[ "$INTO" -eq 1 ]]; then
  RSYNC_FLAGS+=(--ignore-existing)
fi
rsync "${RSYNC_FLAGS[@]}" "$SRC/" "$TARGET_ABS/"

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

# Substitute {{date}} placeholders in scaffolded singleton files so the
# spawned vault passes wiki-lint on day 1. Templates in templates/ keep
# {{date}} — those are instantiated by the Obsidian Templates plugin on
# create.
TODAY="$(date +%Y-%m-%d)"
for i in "${!DATE_FILES[@]}"; do
  rel="${DATE_FILES[$i]}"
  abs="$TARGET_ABS/$rel"
  if [[ -f "$abs" && "${PRE_EXISTED[$i]}" -eq 0 ]]; then
    # portable in-place sed (macOS + linux)
    sed -i.bak "s/{{date}}/$TODAY/g" "$abs"
    rm -f "$abs.bak"
  fi
done

if [[ "$INIT_GIT" -eq 1 ]]; then
  (
    cd "$TARGET_ABS"
    if [[ -d .git ]]; then
      # Already a git repo (typical --into case). Stage the new skeleton
      # files and commit only if anything was actually added.
      git add .
      if ! git diff --cached --quiet; then
        git -c user.email=wiki@local -c user.name=wiki \
          commit -q -m "Add llm-wiki skeleton from wiki-base/"
      fi
    else
      git init -q
      git add .
      git -c user.email=wiki@local -c user.name=wiki \
        commit -q -m "Initial wiki skeleton from wiki-base/"
    fi
  )
fi

if [[ "$INTO" -eq 1 ]]; then
  LEAD="Wiki skeleton merged into: $TARGET_ABS
(existing files preserved; only missing skeleton files were added)"
else
  LEAD="Wiki skeleton created at: $TARGET_ABS"
fi

cat <<EOF

$LEAD

Next:
  1. Run $TARGET_ABS/scripts/wiki-doctor.sh
  2. If you plan to ingest PDFs:
     python3 -m pip install -r $TARGET_ABS/requirements.txt
  3. Edit $TARGET_ABS/purpose.md — describe your research direction.
  4. Drop a source file in $TARGET_ABS/raw/ (PDF or markdown).
  5. Open the vault in Obsidian (optional, for browsing).
  6. From $TARGET_ABS, run Claude Code and invoke /wiki-ingest <raw/your-source>.

EOF
