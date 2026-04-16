---
type: concept
sources: [[[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]]
created: "2026-04-16"
updated: "2026-04-16"
status: current
tags: [automated-scoring, fairness, subgroups, validity]
---

> [!tldr]
> The Williamson-Xi-Breyer framework operationalizes fairness as applying the same framework criteria — mean score differences, associations, generalizability, prediction, and decision accuracy — to subgroups separately, with tighter thresholds for subgroup-level flags.

## Definition

> [!source] Fairness is "comparable validity for identifiable and relevant groups."
> The paper adopts Xi's (2010b, p. 154) definition and treats fairness as an aspect of the assessment's validity argument rather than a separate axis. Fairness analyses extend the framework's existing criteria to subgroups rather than introducing new metrics. [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] The question of fairness is scoped narrowly.
> "We have targeted the question of fairness to the direct question of whether it is fair to subgroups of interest to substitute a human grader with an automated score. This narrowing of the question of fairness makes the assumption that the task type is fair to all subgroups, to include in the assessment, and further, that the human scoring of responses is fair to all subgroups." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## The five subgroup checks

**Table 1.** Subgroup-level checks specified in the framework, each an extension of an existing criterion.

| # | Check | Source criterion | Subgroup rule |
|---|---|---|---|
| 1 | Standardized mean score difference (SMD) by subgroup | [[Standardized Mean Score Difference]] | Flag at SMD > 0.10 for any subgroup (stricter than the 0.15 overall threshold) |
| 2 | Associations between automated and human scores across subgroups | [[Human-Automated Score Agreement]] | Checked at task, task-type, and reported-score levels; major differences indicate a model problem for that subgroup |
| 3 | Generalizability of automated scores by subgroup | [[Generalizability of Automated Scores]] | Substantial subgroup differences suggest scores are differentially reliable |
| 4 | Predictive ability by subgroup | [[Association with Independent Measures]] | Two varieties: (a) predict a second human rater using an initial human vs. automated score, by subgroup; (b) predict an external criterion using human vs. automated score, by subgroup |
| 5 | Score-based decisions by subgroup | [[Automated Scoring Implementation Models]] impact analysis | "The most prominent manifestation of group differences" — whether admission, placement, or other score-based decisions differ by subgroup |

> [!source] SMD subgroup threshold is 0.10, not 0.15.
> "We have established a more stringent criterion of performance, setting the flagging criteria at .10, and applied this criterion to all subgroups of interest to identify patterns of systematic differences in the distribution of scores between human scoring and automated scoring for subgroups." Reference: Ramineni, Williamson, & Weng (2011). [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] Association differences by subgroup flag model problems.
> "Major differences by subgroups may indicate problems with the automated scoring model for these subgroups and should be evaluated for potentially undesirable performance with the subgroups in question." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] Generalizability by subgroup tests differential reliability.
> "Substantial differences across subgroups may suggest that the scores are differentially reliable for different groups." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] Predictive checks have two flavors.
> "This consists of two classes of prediction that are likewise related to the criteria and processes discussed above. First is to compare an initial human score and the automated score in their ability to predict the score of a second human rater by subgroup. The second type of prediction is comparing the automated and human score ability to predict an external variable of interest by subgroup." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] Decision-level differences are the final subgroup check.
> "Subgroup differences should also be investigated in relation to the decisions made based on the scores. This is the most prominent manifestation of group differences." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## Cited empirical examples

> [!source] Direct fairness explorations exist for GRE and TOEFL.
> "An example of a direct exploration of the question of fairness of automated scoring in the context of the GRE program can be found in Bridgeman et al. (2009) and a similar investigation for the TOEFL iBT test in Enright and Quinlan (2010)." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## Key Claims

> [!analysis] The narrow scoping is analytically clean but politically fragile.
> By assuming task design and human scoring are themselves fair, the framework isolates a specific question: does swapping one human for a computer harm any subgroup? This is defensible for a technical evaluation but elides upstream fairness concerns (prompt selection, rater pools, rubric choices). A critic could argue an automated system that inherits a biased human training signal passes the framework's fairness bar while still perpetuating disparate outcomes.

> [!analysis] The tightened 0.10 SMD threshold is the only quantitative fairness criterion in the framework.
> All four other subgroup checks are qualitative: "substantial differences," "major differences," the "most prominent manifestation." This makes fairness evaluation largely judgment-driven outside of the SMD flag, which has implications for audit reproducibility.

> [!analysis] The predictive-check asymmetry is worth noting.
> When comparing initial-human vs. automated-score predictive power on a second human rater by subgroup, the automated score is competing against a score trained on the same kind of rater. Systematic rater bias shared between first and second humans would not be caught by this check. That makes the external-criterion version of the check more robust for fairness, but also more vulnerable to impure criteria.

## Connections

- Cross-cuts every empirical area of the [[Automated Scoring Evaluation Framework]].
- Operationalized via [[Standardized Mean Score Difference]] (quantitative), [[Human-Automated Score Agreement]], [[Generalizability of Automated Scores]], [[Association with Independent Measures]] (qualitative).
- Decision-level differences connect to [[Automated Scoring Implementation Models]] impact analysis.

## Open Questions

> [!gap] Most subgroup thresholds are qualitative.
> The framework specifies a 0.10 SMD flag but leaves "major" and "substantial" undefined for the other four checks.

> [!gap] Upstream fairness is assumed, not tested.
> Task-design fairness and human-scoring fairness are treated as prerequisites. The framework does not specify how those assumptions are audited before subgroup analysis of the engine begins.

> [!gap] Intersectional subgroups are unaddressed.
> The paper discusses subgroups but does not address how to handle intersections (e.g., demographic crosses) or small subgroups where statistical power is limited.
