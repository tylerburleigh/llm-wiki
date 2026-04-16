---
type: concept
sources: [[[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]]
created: "2026-04-16"
updated: "2026-04-16"
status: current
tags: [statistics, agreement, fairness, automated-scoring]
---

> [!tldr]
> The standardized mean score difference (SMD) compares the mean of automated and human scores in pooled standard deviation units; ETS flags SMD above 0.15 overall and above 0.10 for any subgroup as a substantive concern.

## Definition

> [!source] SMD is a standardized gap between automated and human score means.
> The paper's Note 4 defines SMD using X_AS (mean of the automated score), X_H (mean of the human score), SD_AS^2 (variance of the automated score), and SD_H^2 (variance of the human score). The actual formula in the footnote is a figure that did not survive PDF-to-markdown conversion ("picture [67 x 29] intentionally omitted"). [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!unverified] Denominator form.
> A common SMD denominator is pooled: sqrt((SD_AS^2 + SD_H^2) / 2). However, the paper's surrounding prose says standardization is "on the distribution of human scores," which would imply the denominator is SD_H alone. The omitted formula figure is the authoritative source; without access to it we cannot choose between these two interpretations. Treat the specific denominator as unverified until the original PDF or a secondary source is consulted.

> [!source] The criterion is standardized on the human-score distribution.
> "The standardized mean score difference (standardized on the distribution of human scores) between the human scores and the automated scores cannot exceed .15. This criterion ensures that the distribution of scores from automated scoring is centered on a point close to what is observed with human scoring to avoid problems with differential scaling." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## Thresholds

**Table 1.** SMD flagging thresholds used by ETS.

| Scope | Flagging threshold |
|---|---|
| Overall sample | SMD > 0.15 |
| Any subgroup of interest (fairness check) | SMD > 0.10 |

> [!source] The subgroup threshold is stricter than the overall threshold.
> "We have established a more stringent criterion of performance, setting the flagging criteria at .10, and applied this criterion to all subgroups of interest to identify patterns of systematic differences in the distribution of scores between human scoring and automated scoring for subgroups." Reference: Ramineni, Williamson, & Weng (2011). [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## Why it matters

> [!source] SMD catches differential scaling that QWK can miss.
> A high agreement kappa is consistent with a systematic mean shift; SMD guards against "differential scaling" across the human and automated distributions. [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] SMD requires out-of-sample evaluation for regression-based scorers.
> "For a regression-based procedure like e-rater, the standardized mean score difference criterion would seldom be flagged" if computed on the training data, because regression centers residuals by construction. ETS therefore requires evaluation on a different data set than the one used to build the model. [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] Variance differences are also examined but without a strict threshold.
> Note 3 states: "We also examine the variance of the e-rater scores in comparison to that of the human scores, although we do not have a strict rule of thumb for what constitutes a large difference. Judgments about the acceptability of variance differences are made case by case by a technical review committee at ETS." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## Key Claims

> [!analysis] The two-tier threshold operationalizes fairness as a tighter ceiling.
> Setting 0.10 for subgroups and 0.15 overall formalizes the idea that subgroup errors must be smaller than overall errors to count as fair. This is simple to audit but silent on how to rank-order subgroups when several exceed 0.10 by varying amounts.

> [!analysis] SMD pairs with QWK to cover complementary failure modes.
> QWK catches noise in individual scores. SMD catches bias in the distribution. A regression-based scorer can fail either check independently: noisy features hurt QWK, biased training data shifts the mean. Both need to pass.

## Connections

- Conjunctive with [[Quadratic-Weighted Kappa]] under [[Human-Automated Score Agreement]].
- Part of the Evaluation area of the [[Automated Scoring Evaluation Framework]].
- Extended to subgroups as the primary fairness flag (0.10 threshold).
- Applied to [[e-rater]] operationally.

## Open Questions

> [!gap] The 0.15 and 0.10 thresholds are not empirically derived in this paper.
> Like the 0.70 kappa threshold, the SMD thresholds are ETS working conventions. No sensitivity analysis or external benchmark is offered.

> [!gap] Variance-difference threshold is unspecified.
> The paper concedes no strict rule exists for acceptable variance differences; decisions are committee judgments.
