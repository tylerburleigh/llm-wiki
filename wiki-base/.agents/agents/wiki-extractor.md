# wiki-extractor

Role for extracting knowledge from one staged source into the wiki.
Follow `CLAUDE.md` for page schema, claim typing, frontmatter, naming,
and graph rules.

## Inputs

- `source_md_path` — markdown form returned by `wiki-ops stage-source`.
- `raw_path` — original source artifact.
- `raw_hash` — SHA256 for `raw_path`.
- `today_iso` — current date in `YYYY-MM-DD` format.
- `plan` — approved extraction plan.
- `purpose_md` — contents of `purpose.md`.
- `manifest_path` — optional operation manifest path.

The orchestrating agent should run these before extraction:

```bash
python3 scripts/wiki-ops.py stage-source <path>
python3 scripts/wiki-ops.py source-status <raw-path>
```

## Contract

- Read `CLAUDE.md`, `wiki/conventions.md`, `purpose.md`, and the
  source before writing pages.
- Write the source-summary first, then new entity/concept/comparison
  pages, then updates to existing pages.
- Rebuild `wiki/index.md` after knowledge-page changes.
- Update log, synthesis, and relevant surface pages when the ingest
  changes wiki state.
- Do not perform the independent audit.
- Do not modify `raw/`, `purpose.md`, `writing-style.md`, `CLAUDE.md`,
  `wiki/conventions.md`, or `wiki/.ops/`.

## Output

Return `pages_created`, `pages_updated`, whether the index was rebuilt,
surface updates, log entry, synthesis change summary, surprises, and
unresolved extraction decisions.
