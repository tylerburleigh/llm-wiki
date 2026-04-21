---
name: wiki-query
description: Answer a question from the LLM wiki's accumulated knowledge. Use when the user asks a question that plausibly draws on the wiki ("what does the wiki say about X", "/wiki-query X", "compare Y and Z from the wiki", "summarize what we know about ..."), or asks to produce a standalone artifact (comparison, timeline, slide deck) grounded in existing pages. Reads the index and relevant pages, follows wikilinks, cites specific pages, distinguishes sourced facts from inferences, and — when the answer is reusable — files it as a new page with proper frontmatter and a log entry. Does not commit to git.
---

# wiki-query

You are answering a question using the wiki's accumulated knowledge. The vault root has a `CLAUDE.md` that describes the schema; this skill describes the *workflow* for the query operation.

The point of the skill is epistemic discipline: cite the pages, separate what the wiki sourced from what you inferred, and file durable answers so the compiled knowledge grows instead of being thrown away after each question.

## When to invoke

- User says "/wiki-query <question>" or "query the wiki for <question>"
- User asks a question the wiki plausibly knows about ("what does our wiki say about X", "how do we think about Y")
- User asks for a derived artifact grounded in the wiki: comparison table, timeline, slide deck, explainer page
- User asks "are there contradictions in the wiki about X", "what's missing on Y"

Do not invoke for:
- Questions about the *tool* (schema, skills, workflow) — answer directly from CLAUDE.md
- Questions about a source you haven't ingested yet — route to `/wiki-ingest` first

## Arguments

- Positional: the question (free text)
- `--format=<markdown|page|table|deck>` — output form (default: markdown reply; `page` files a new page; `table` and `deck` produce a comparison table or Marp deck)
- `--no-file` — answer but do not file, even if the answer looks reusable

If the user's question is ambiguous about format, ask once; don't guess between deck and page.

## Steps

### 1. Read context

- Read `CLAUDE.md` at the vault root (frontmatter rules, claim typing, page naming, index format, writing style).
- Read `wiki/conventions.md` (domain-specific conventions accumulated by this vault).
- Read `purpose.md`. If it is empty, note that — you have no research-direction steering and must rely on the question alone.
- Read `wiki/index.md` in full. This is your map.

### 2. Plan the read

From the question and the index, build a short plan before opening any page:

1. **Candidate pages** — which entries in the index look directly relevant. Prefer pages whose TLDR matches the question over pages named like the question.
2. **Search terms** — two to four specific phrases you will grep for in `wiki/` to catch pages the index entry names don't telegraph. Use `obsidian search query="..." path=wiki` when the Obsidian CLI is available; fall back to `grep -ri "..." wiki/`.
3. **Link-following budget** — the max number of wikilink hops you will follow from the candidate set before stopping. Two hops is usually enough; three is the cap for most questions. State the budget so you stop when you reach it rather than drifting.

Show this plan to the user only if the question is ambiguous or the plan would touch many pages (>10). Otherwise proceed silently.

### 3. Read and collect

Read the candidate pages. For each, record:

- Page path, `type`, TLDR.
- The specific `[!source]` callouts that bear on the question, with their cited sources.
- The specific `[!analysis]` callouts that bear on the question.
- Any `[!gap]` or `[!unverified]` callouts that bear on the question — these are as important as the sourced claims, because they tell you what the wiki explicitly doesn't know.
- Wikilinks to follow in hop 2 (and hop 3 if budgeted).

If you hit `[!gap]` callouts that directly answer "we don't know X," name them in the answer. Do not silently fill gaps with guesses.

### 4. Assemble the answer

Write the answer with claim typing preserved:

- **Sourced claims**: state them and link the page that sourced them. Example: `According to [[Page Name]], X is Y.`
- **Inferences you're making across pages**: label them as inference and show the reasoning. `Synthesizing across [[Page A]] and [[Page B]]: …`
- **Unknowns**: if the wiki has `[!gap]` or `[!unverified]` relevant to the answer, say so. Do not paper over them.
- **Contradictions**: if pages disagree, surface the disagreement with both citations. Do not silently pick a side.

Match the writing-style rules (funnel structure, plain language, one qualifier max, no hedging stacks). See `writing-style.md` at the vault root if wording is hard.

For `--format=table`: a comparison table with named rows and citation column. For `--format=deck`: a Marp deck, title slide + one slide per key claim + citations. For `--format=page`: a standalone wiki page (see step 5).

### 5. Decide whether to file

A query answer is worth filing as a new page when **all** of these hold:

- It consolidates material from two or more existing pages into something reusable.
- Someone asking a similar question in a month would be served by finding this page.
- The answer is not trivially derivable by reading one existing page.

File as:
- `wiki/comparisons/<Title>.md` — for comparisons, trade-off analyses, and cross-source syntheses.
- `wiki/concepts/<Title>.md` — for new conceptual framings that emerge from the query.
- `wiki/entities/<Title>.md` — only if the query surfaced a distinct entity not previously filed; usually not.

When filing, use the appropriate template from `templates/`, fill required frontmatter (including `sources:` listing every source-summary you cited, per the Wiki Conventions), write a one-sentence TLDR, and preserve claim typing inside the page.

Do **not** file when:
- The question was about the wiki itself ("which pages cover X?") — an index lookup.
- The answer is a one-off or tightly scoped to the user's current context.
- The user passed `--no-file`.

When in doubt, ask once: "File this as a comparison page?"

### 6. Update the index, log, and — if affected — synthesis

If you filed a page:

- Add an entry to `wiki/index.md` under the correct category. Format: `- [[Page Name]] (N) — One-line TLDR.` where N is `len(sources)`.
- Append to `wiki/log.md`: `### [YYYY-MM-DD] query | <one-line description including the question framing>`
- If the new page materially shifts the wiki's overall story, revise `wiki/synthesis.md` (targeted edit, not rewrite; keep it under ~1,000 words).

If you did not file a page, still append a log entry when the query consumed meaningful read effort (≥5 pages touched). This lets lint's staleness checks see which corners of the wiki are being actively used.

### 7. Surface stale or gap findings — but don't fix

If during reading you notice:

- A page with `updated` older than 30 days whose content no longer matches recent ingests.
- An unanswered `[!gap]` that the current session could plausibly fill from a source already in the wiki.
- A broken or unresolved wikilink.

Report these to the user as observations at the end of the answer. Do **not** edit pages in response — that is `/wiki-repair`'s, `/wiki-ingest`'s, or `/wiki-lint`'s job depending on whether the work is a scoped correction, source refresh, or broader health pass. Mixing query with repair stretches the skill's contract and muddies what was changed when something goes wrong.

### 8. Present to the user

- The answer itself (with citations), or the filed page path plus a link-form answer.
- If a page was filed: path, TLDR, index entry added, log entry added.
- Stale / gap observations (from step 7) as a short appended list.
- A reminder to commit when ready. Do **not** auto-commit.

## Error handling

- **Empty index**: the wiki has no content yet. Tell the user and suggest `/wiki-ingest <source>` first.
- **Question depends on an un-ingested source**: if the user cites a source by name that isn't in `wiki/sources/`, say so and suggest ingesting it.
- **All candidates are `[!gap]`**: the wiki explicitly doesn't know. Return the gap callouts verbatim as the answer; do not attempt to fill from general knowledge.
- **Conflicting `[!source]` callouts across pages**: surface both, cite both, and note the disagreement as a finding. Do not silently reconcile.

## What this skill does not do

- Does not commit to git. Human reviews.
- Does not ingest new sources. If the question requires a source not in the wiki, route to `/wiki-ingest`.
- Does not modify existing wiki pages in response to findings. Stale and gap observations go to the user; fixes happen in `/wiki-repair` (scoped correction), `/wiki-ingest` (refresh path), or `/wiki-lint` (broader cleanup).
- Does not modify `CLAUDE.md`, `purpose.md`, `writing-style.md`, `wiki/conventions.md`, or anything in `raw/`.
- Does not bypass claim typing. A new filed page must still use `[!source]`, `[!analysis]`, `[!unverified]`, `[!gap]` correctly — citing the query didn't bless synthesis claims as sourced.
