#!/usr/bin/env sh
# Install the LLM Wiki.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/foundry-works/llm-wiki/main/install.sh | sh
#
# Clones the repo to $LLM_WIKI_DIR (default: ~/.local/share/llm-wiki) and
# symlinks scripts/new-wiki.sh and scripts/wiki-doctor.sh to
# $LLM_WIKI_BIN/llm-wiki-new and $LLM_WIKI_BIN/llm-wiki-doctor (default:
# ~/.local/bin). Re-running updates the clone in place.

set -eu

REPO="${LLM_WIKI_REPO:-https://github.com/foundry-works/llm-wiki.git}"
CLONE_DIR="${LLM_WIKI_DIR:-$HOME/.local/share/llm-wiki}"
BIN_DIR="${LLM_WIKI_BIN:-$HOME/.local/bin}"

if [ -d "$CLONE_DIR/.git" ]; then
  echo "Updating $CLONE_DIR"
  git -C "$CLONE_DIR" pull --ff-only
else
  echo "Cloning $REPO -> $CLONE_DIR"
  mkdir -p "$(dirname "$CLONE_DIR")"
  git clone --depth 1 "$REPO" "$CLONE_DIR"
fi

mkdir -p "$BIN_DIR"
ln -sf "$CLONE_DIR/scripts/new-wiki.sh" "$BIN_DIR/llm-wiki-new"
ln -sf "$CLONE_DIR/scripts/wiki-doctor.sh" "$BIN_DIR/llm-wiki-doctor"

case ":$PATH:" in
  *":$BIN_DIR:"*) PATH_NOTE="" ;;
  *) PATH_NOTE="
Add this to your shell profile (~/.zshrc, ~/.bashrc) if it isn't already:
  export PATH=\"$BIN_DIR:\$PATH\"
" ;;
esac

cat <<EOF

Installed:
  repo:     $CLONE_DIR
  launchers:
    $BIN_DIR/llm-wiki-new -> scripts/new-wiki.sh
    $BIN_DIR/llm-wiki-doctor -> scripts/wiki-doctor.sh
$PATH_NOTE
Next steps:
  1. llm-wiki-new ~/wikis/my-wiki --git
  2. cd ~/wikis/my-wiki
  3. llm-wiki-doctor .
  4. If you want PDF ingest: python3 -m pip install -r requirements.txt
  5. Edit purpose.md with your research direction.
  6. Drop a source (PDF or markdown) into raw/.
  7. Launch Claude Code and run: /wiki-ingest raw/<your-source>
EOF
