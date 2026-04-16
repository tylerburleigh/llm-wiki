# Writing Style Reference

The agent reads this for detail and examples when drafting or revising
wiki pages. The short rules in CLAUDE.md are the operational summary;
this file is the long form.

## Funnel structure

Each document, section, and paragraph flows from broad to narrow: result
first, then context, then detail. A reader who stops at any point should
have the most important information so far.

- **Page level:** The `[!tldr]` states the key takeaway. Body expands:
  context → claims → open questions.
- **Section level:** Open with the conclusion, then support it.
- **Paragraph level:** Lead with the point, then explain. Don't make the
  reader hold details in memory while waiting for the result.

## Plain language

Prefer concrete, everyday words over academic phrasing.

| Instead of | Write |
|---|---|
| "derive from" | "come from" |
| "sufficient" | "enough" |
| "may require" | "will likely need" |
| "binding constraint" | "bottleneck" |
| "utilize" | "use" |

## Short sentences

If a sentence has more than one clause doing real work, split it.

Before:
> The inference confidence is computed per claim from the model's raw
> logits, scaled by a temperature parameter, and compared against a
> tier-specific threshold.

After:
> Inference confidence is computed per claim from the model's scaled
> logits. Each value is compared against a tier-specific threshold.

## Avoid hedging stacks

One qualifier is fine. Stacking dilutes the point.

Before: "It should be noted that this might potentially suggest that the
threshold could possibly be too strict."

After: "This suggests the threshold is too strict."

Be direct about limitations: state them plainly rather than burying them
in hedged language.

## Avoid overusing emdashes

Emdashes are useful for parenthetical asides, but overuse makes prose
breathless. Limit to one emdash pair per paragraph. If you reach for a
second, use a comma, colon, period, or parentheses instead. For numeric
ranges, use a hyphen (9-10), not an emdash (9—10) or en-dash (9–10).

## Define acronyms on first use per page

Wiki pages are read standalone. Spell out on first mention — "inter-rater
reliability (IRR)" — then use the acronym within that page.

## Name recurring concepts

When a pattern is referenced across sections or pages, give it a compact
label on first introduction ("the three-judge panel," "write-once
semantics"). Later references can use the shorthand without re-explaining.

## Lead in to tables and figures

Don't drop a table or figure cold. Tell the reader what to look for.

> Table 1 shows source counts by entity, ordered by centrality. The
> rightmost column flags entities with only one cited source.

Caption format: `**Table N.** Description` and `**Figure N.** Description`.
Descriptions should be specific enough to interpret the table without
surrounding text.

## Anchor thresholds to their names

Pair a number with its concept on first mention. A bare number has no
meaning until the reader knows what it belongs to.

Before: "We include only entities with ≥ 3 sources."

After: "We include only entities meeting the corroboration threshold
(≥ 3 cited sources)."

## State assumptions explicitly

List assumptions up front — in a bullet list — rather than embedding them
in prose where they're easy to miss. This applies to `[!analysis]`
callouts and comparison pages especially.

Before:
> Because sources overlap substantially and use comparable methods, we
> can pool their estimates.

After:
> **Assumptions:**
> - Sources cover overlapping populations.
> - Methods are comparable enough that estimates can be pooled.
>
> Under these assumptions, we pool the estimates…

## Consistent numbers and formatting

- Pick a rounding convention per page. Don't mix "0.7" and "0.70" for
  the same quantity.
- Spell out numbers under 10 in prose ("three items") unless grouped
  with larger numbers ("items 3, 7, and 12").
- Use commas in thousands (18,000 not 18000).
- Use hyphens for numeric ranges (0.70-0.80, grades 3-5), not en-dashes
  or emdashes.

## For comparison and synthesis pages

- **Translate findings into practical implications.** Don't just restate
  results — say what they mean for the research direction. Each major
  finding should have a "so what" the reader can act on.
- **Qualify cross-source comparisons.** When comparing results across
  sources, note the boundary conditions — different methods, domains, or
  scope. Don't let a favorable comparison imply more generality than the
  sources support.
