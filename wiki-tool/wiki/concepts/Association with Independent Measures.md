---
type: concept
sources: [[[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]]
created: "2026-04-16"
updated: "2026-04-16"
status: current
tags: [automated-scoring, validity, convergent-validity, extrapolation]
---

> [!tldr]
> Association with independent measures is the framework's extrapolation check: whether automated scores relate to other variables (within-test sections, external criteria) in the same pattern as human scores, interpreted as evidence of convergent and divergent validity.

## Definition

> [!source] The check maps to Kane's extrapolation inference.
> "Association with independent measures" is paired with the extrapolation inference. It is meant to catch what agreement with humans cannot — specifically, whether automated scores behave like human scores (or better) when correlated with variables that stand outside the training signal. [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] The rationale is that human scores have known flaws.
> "The problems and concerns with human scoring are well documented and represent a range of potential pitfalls including halo effects, fatigue, tendency to overlook details, and problems with consistency of scoring across time. Therefore, it is not unreasonable to expect automated scores, if they are to provide any advantages that overcome these concerns with human scoring, to at least occasionally produce scores that differ from human scoring." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## Three sub-checks

**Table 1.** Sub-checks under the independent-measures area.

| Sub-check | Question |
|---|---|
| Within-test relationships | Are automated scores related to scores on other sections of the test in similar ways to how human scores are? |
| External relationships | Are automated scores related to external measures of interest (grades, self-assessments, etc.) in similar ways to how human scores are? |
| Relationship at the task-type and reported-score level | Do the within-test and external patterns hold not only at the task score level but also when aggregated to task-type and reported score? |

> [!source] Specific external criteria used for e-rater.
> "We have examined both within-test relationships through patterns of association with scores on other test sections, and external criteria, such as self-reported measures that may be of interest (e.g., self-assessments of writing ability, grades on essays in English class or on course papers, and grades on academic courses; Attali et al., 2010; Powers et al., 2002; Weigle, 2010)." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## Key empirical findings

> [!source] In mature essay scoring, divergence is rare.
> "Thus far in practice the fact that automated scoring models are calibrated to replicate human scores, and are typically quite successful at doing so, has resulted in there seldom being notable differences in association with external variables between automated and human scores that warrant such debate." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] Spoken-response scoring shows divergent correlations with external criteria.
> "For other domains of applications which are not as mature as automated essay evaluation, such as automated scoring of spontaneous speech, divergent patterns of correlations with external criteria have been found for automated scores versus human scores (Bridgeman, Powers, Stone, & Mollaun, 2012), which may be partially attributable to the limitations of current speech scoring technologies." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## Key Claims

> [!analysis] This check does double duty — validation and diagnostic.
> When automated and human scores show the same external-criterion pattern, that corroborates both. When they differ, the difference itself becomes a diagnostic: is the automated system missing something humans catch, or vice versa? The paper acknowledges this interpretation is hard because the external criteria are themselves "impure measures" (a classic construct-validity problem).

> [!analysis] The check is weak on mature essay systems because the training is tight.
> If the engine is regression-trained to predict human scores and does so well, the engine's correlations with third variables will track human correlations by construction. That the check rarely surfaces differences on e-rater is therefore evidence that e-rater is doing its training job, not that e-rater is construct-valid. The extrapolation inference is weaker than it looks when the model is tightly coupled to human scores.

> [!analysis] Divergent patterns on spoken-response scoring deserve more weight than the paper gives them.
> The one cited counterexample (Bridgeman et al., 2012) is folded into a single sentence, but it is exactly the scenario this check is designed to detect. Interpreting it as "the tech isn't mature enough" rather than "the check is doing its job" shades the evidence.

## Connections

- Third area of the [[Automated Scoring Evaluation Framework]].
- Complements [[Human-Automated Score Agreement]]: agreement tests how well the engine mimics humans on the same response; this area tests whether mimicking humans is the right target.
- One of the framework criteria applied to [[Fairness in Automated Scoring]] (relationship patterns checked by subgroup).
- Relevant to any liberalization decision captured in [[Automated Scoring Implementation Models]].

## Open Questions

> [!gap] No threshold for "similar" correlation patterns.
> The paper asks whether patterns are "similar" across automated and human but does not specify how much difference is too much. Judgments appear to be qualitative.

> [!gap] Pure external criteria are unavailable.
> The paper concedes that external measures used in practice (grades, self-assessments) are themselves impure indicators of writing ability. The check is constrained by the quality of the criterion space, not just by the engine.
