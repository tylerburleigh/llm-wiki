---
type: concept
sources: [[[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]]
created: "2026-04-16"
updated: "2026-04-16"
status: current
tags: [statistics, agreement, kappa, reliability, automated-scoring]
---

> [!tldr]
> Quadratic-weighted kappa (QWK) is a chance-corrected rater-agreement statistic that penalizes large disagreements more than small ones; ETS requires QWK of at least 0.70 between automated and human essay scores as one of several conjunctive acceptance thresholds.

## Definition

> [!source] QWK compares observed disagreement to chance disagreement with a squared-error weighting.
> The paper's Note 1 gives the formula as kappa = 1 - E[(X1 - Y1)^2] / E[(X1 - Y2)^2], where (X1, Y1) is the paired-rating distribution assumed to agree and (X1, Y2) is a pair of unrelated ratings. "When the variables have the same marginal distributions and an intraclass correlation of rho, rho = kappa (Fleiss & Cohen, 1973)." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## Why it matters

> [!source] QWK and Pearson correlation are the headline agreement statistics at ETS.
> "We typically evaluate the agreement of automated scores with their human counterparts on the basis of quadratic-weighted kappa and Pearson correlations (Fleiss & Cohen, 1973)." ETS does not use exact or exact-plus-adjacent agreement percentages as acceptance thresholds "because of scale dependence... and sensitivity to base distributions." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## Key Claims

> [!source] The acceptance threshold is 0.70 (corroboration threshold).
> "The quadratic-weighted kappa between automated and human scoring must be at least .70 (rounded normally) on data sets that show generally normal distributions." The same 0.70 floor applies to product-moment correlations. [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] The 0.70 threshold is justified conceptually, not empirically.
> "This value was selected on the conceptual basis that it represents the 'tipping point' at which signal outweighs noise in agreement." The same rationale is given for the correlation floor: roughly half the variance in human scores is accounted for. [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] QWK and correlation yield non-identical values for the same data.
> "The results from quadratic-weighted kappa and product-moment correlations are not identical, as kappa is computed on the basis of values of e-rater that are rounded normally to the nearest score point on the scale that the human graders use, whereas the correlation is computed on the basis of unrounded values." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] Near-threshold agreement can still be approved when human-human agreement is itself borderline.
> "We have observed cases in which the automated-human agreement for a particular task has been slightly less than the .70 performance threshold, but very close to a borderline performance for human scoring (e.g., an automated-human weighted kappa of .69 and a human-human kappa of .71), and we have approved such models for operational use." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] Automated-human agreement can legitimately exceed human-human agreement on linguistic-quality tasks.
> "It is relatively common to observe automated-human agreements that are higher than the human-human agreements for tasks that primarily target linguistic writing quality, such as GRE Issue and TOEFL Independent tasks." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!analysis] The 0.70 threshold is a conventional anchor, not a derived one.
> The paper labels the threshold the "tipping point" where signal outweighs noise. That is a rhetorical frame, not a statistical theorem. The threshold's authority derives from ETS using it consistently across high-stakes programs, not from an empirical mapping between kappa values and score-use outcomes. Other programs adopting this threshold should flag that they are inheriting a convention.

> [!analysis] QWK's penalty structure matches how graders and test-takers care about errors.
> Squared-error weighting means a 1-point disagreement contributes 1/9 the penalty of a 3-point disagreement on a 6-point scale. That matches the intuition that a 4-vs-5 mix is close to agreement while a 2-vs-5 mix is not. Exact-agreement percentages lack that gradient and conflate small and large disagreements.

## Connections

- Central flagging statistic within [[Human-Automated Score Agreement]].
- Paired with [[Standardized Mean Score Difference]] as the other conjunctive flagging rule.
- Feeds the [[Automated Scoring Evaluation Framework]]'s Evaluation area (mapped to [[Argument-Based Validity]]).
- Applied to [[e-rater]] in production at [[Educational Testing Service]].

## Open Questions

> [!gap] Sensitivity of the 0.70 threshold is not characterized.
> The paper offers no analysis of how test decisions would change if the threshold were 0.65 or 0.75. Threshold sensitivity is treated as background convention.

> [!gap] QWK on non-normal score distributions
> The threshold is anchored to "data sets that show generally normal distributions." The paper does not describe the treatment for strongly skewed distributions beyond case-by-case judgment.
