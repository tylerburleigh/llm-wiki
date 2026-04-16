---
type: concept
sources: [[[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]]
created: "2026-04-16"
updated: "2026-04-16"
status: current
tags: [automated-scoring, agreement, validity, reliability]
---

> [!tldr]
> At ETS, human-automated score agreement is treated as a bundle of conjunctive acceptance checks — agreement, degradation relative to human-human, mean-score difference, adjudication thresholds, and human intervention rules — rather than a single metric.

## Definition

> [!source] Agreement with human scores is the longest-standing criterion for automated scoring.
> "The emphasis of automated scoring evaluation has traditionally been on the agreement between the automated scores and human scores on the same response, which are typically considered the 'gold standard,' though we highlight problems with this perspective." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## The conjunctive acceptance bundle

**Table 1.** Checks ETS applies under the agreement area, with thresholds.

| Check | Threshold | Purpose |
|---|---|---|
| Agreement with human scores (QWK and Pearson correlation, same 0.70 floor on the same signal-vs-noise rationale) | >= 0.70 | Signal-over-noise in agreement |
| Degradation from human-human agreement | <= 0.10 lower in kappa or correlation | Prevents passing 0.70 while still notably worse than humans |
| Standardized mean score difference (SMD) overall | <= 0.15 | Catches differential scaling |
| SMD for any subgroup | <= 0.10 | Fairness |

The source treats QWK and Pearson as two expressions of a single agreement criterion, not as two independent conjunctive gates. Both are reported (kappa on rounded e-rater values, correlation on unrounded), but the underlying threshold and its rationale are the same.

See [[Quadratic-Weighted Kappa]] and [[Standardized Mean Score Difference]] for the statistics themselves.

> [!source] All checks are conjunctive.
> "At ETS these criteria are conjunctive, with any area of performance not meeting these criteria being flagged as a substantive concern." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] Human-human agreement is an upper bound for automated-human agreement when the model is trained on humans.
> "The expected performance of e-rater against this criterion is bounded by the performance of human scoring... if the interrater agreement of independent human raters is low, especially below the .70 threshold, then automated scoring is disadvantaged in demonstrating this level of performance not because of any particular failing of automated scoring, but because of the inherent unreliability of the human scoring upon which it is both modeled and evaluated." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## Adjudication thresholds

> [!source] Programs can pick different score-distance thresholds to trigger human adjudication.
> "In implementing automated scoring, alternative thresholds for the definition of discrepancy when evaluating the agreement between automated and human scores may be considered." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] GRE and TOEFL illustrate the range.
> "The GRE program is using an 'exact agreement' threshold for defining agreement between automated and human scores such that if the automated score is .5 or more different than the human score, the scores are considered to be discrepant and an additional human grader scores the submission. By contrast, the TOEFL program implemented a discrepancy threshold of 1.5 between the automated and human score as the minimum value that results in the scores being declared discrepant." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

See [[GRE vs TOEFL e-rater Implementation]] for the full contrast.

## Human intervention

> [!source] e-rater flags certain response types for human-only scoring.
> "An automated scoring model relies on analyzing typical patterns of response characteristics to predict human scores and may not work well for responses that exhibit certain 'abnormal' characteristics. Currently the e-rater technology will flag essays of excessive length or brevity, repetition, those with too many problems, or off-topic responses for scoring by human raters." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## Evaluation must be out of sample

> [!source] Agreement checks require data disjoint from training data.
> "All the performance expectations in this section are based on the assumption that these evaluation criteria are being applied to a different set of data than the data used to build the automated scoring models... if computed on the same data used for model calibration the measures of agreement for automated scoring would be inflated and, for a regression-based procedure like e-rater, the standardized mean score difference criterion would seldom be flagged." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] Evaluation conditions must match intended deployment.
> "The conditions under which the performance samples used for scoring model evaluation are produced should be consistent with the intended implementation method of automated scoring... Test takers are very likely to adapt their test-taking behavior to the grader... and may thus produce test responses that are much more challenging to grade by computers if they are aware of being scored by a computer only." (Citing Xi, in press.) [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## Key Claims

> [!source] Task-level, task-type-level, and reported-score-level evaluations are all required.
> "In typical practice at ETS, we first conduct the empirical associations with human score (agreement, degradation, and standardized mean score difference) at the task level. At the task type level (aggregated results across the individual tasks within the task type) and the reported section score level the entire contingent of measures discussed above are also employed in the evaluation of performance." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!analysis] The degradation rule closes the loophole created by the absolute threshold.
> Without it, an engine could just clear 0.70 on a task where humans themselves agree at 0.90, which would be a bad outcome. The 0.10-degradation rule says even when the engine clears the absolute floor, it cannot be more than 0.10 below the human-human ceiling. Combined with the absolute floor, this forces the engine to be both objectively reliable and comparable to humans on the same task.

> [!analysis] Human-human agreement is both ceiling and suspect benchmark.
> The framework treats human-human agreement as the practical upper bound the automated system can approach (via the degradation rule). But the paper also flags human scoring's known problems: "halo effects, fatigue, tendency to overlook details, and problems with consistency of scoring across time." That is why the framework includes a separate association-with-independent-measures area: if the engine diverges from humans in a way that agrees better with external criteria, that divergence is a feature, not a bug. On linguistic-quality tasks, automated-human agreement can legitimately exceed human-human agreement.

> [!analysis] Mismatched evaluation conditions is an under-discussed risk.
> The paper calls out that test-takers asked to perform for a known-automated grader may write differently than test-takers writing for a human or mixed grader. Any validation study using archive essays that were originally human-graded may overstate engine performance relative to a world in which the engine scores alone.

## Connections

- Central to the Evaluation area of [[Automated Scoring Evaluation Framework]].
- Built on [[Quadratic-Weighted Kappa]] and [[Standardized Mean Score Difference]].
- Cross-cuts [[Construct Representation in Automated Scoring]] (rubric-feature mismatch feeds directly into agreement failures).
- Program-level variation captured in [[GRE vs TOEFL e-rater Implementation]].

## Contradictions & Tensions

- Human-human agreement is simultaneously the ceiling for automated agreement (degradation rule) and a flawed benchmark (halo effects, fatigue, consistency drift). The paper resolves this by using humans as the training target and agreement floor, while adding a separate independent-measures check as a sanity check.

## Open Questions

> [!gap] The degradation rule's 0.10 is not empirically justified.
> As with the 0.70 kappa floor and the 0.15 SMD flag, the 0.10-degradation threshold is presented as a working convention.
