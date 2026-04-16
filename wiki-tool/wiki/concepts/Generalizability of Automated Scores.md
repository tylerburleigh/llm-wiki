---
type: concept
sources: [[[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]]
created: "2026-04-16"
updated: "2026-04-16"
status: current
tags: [automated-scoring, reliability, generalizability, validity]
---

> [!tldr]
> Generalizability is the fourth emphasis area of the Williamson-Xi-Breyer framework and asks whether automated scores (alone and combined with human scores) reproduce across tasks and alternate test forms as reliably as, or more reliably than, human scores.

## Definition

> [!source] Generalizability maps to Kane's generalization inference.
> The framework pairs "generalizability of the resultant scores" with the generalization inference in Kane's argument-based validity approach. It is separate from agreement with humans (evaluation) and from association with independent measures (extrapolation). [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] Automated scoring can improve score reliability, but the claim must be checked empirically.
> "Automated scoring has a great potential to improve the reliability of the reported scores. This is an empirical issue, though, and can be investigated in two ways." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## Two operational checks

**Table 1.** The two generalizability checks specified in the framework.

| Check | What it measures | How it is computed |
|---|---|---|
| Generalizability across tasks and test forms | Whether automated scores (and automated-plus-human combined scores) carry across tasks and forms as consistently as human scores | G or Phi coefficient in generalizability theory with task as a random facet, computed for human and automated scores separately. For combined reported scores, treat task and rating (human first, automated second) as random facets. |
| Prediction of human scores on an alternate form | Whether automated, human, or combined scores on one form predict human scores on an alternate form better | Regression / correlation of scores on form A against human scores on form B |

> [!source] G- and Phi-coefficient recipe.
> "A G or Phi coefficient in the G theory framework can be computed using task as a random facet for human and e-rater scores, respectively, and the coefficients can be compared to indicate the extent to which the use of e-rater impacts the score reliability. Additional analyses should also be conducted based on automated-human combined scores... treating task and rating (human rating as the first rating and e-rater score as the second rating) as random facets." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] Alternate-form prediction is the second check.
> "To what extent do automated, human, and automated-human combined scores on one test form predict human scores on an alternate form? This analysis will reveal whether the use of automated scoring may improve the alternate form reliability of the scores." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## Key empirical finding for e-rater

> [!source] e-rater beats a single human rater at predicting alternate-form human scores on TOEFL iBT Writing.
> "Such analyses have been conducted for e-rater for scoring a TOEFL iBT Writing task, where e-rater was found to predict scores averaged across two human raters on alternate forms better than a single human score (Bridgeman, Trapani, & Williamson, 2011)." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## Key Claims

> [!analysis] Generalizability is where automated scoring's best defense lives.
> Agreement with humans is bounded above by human-human reliability, so on that criterion the engine can at best match humans. Generalizability is different: because automated scoring applies the same scoring function invariantly across tasks and forms, it can exceed the consistency of human raters whose performance drifts. The Bridgeman et al. (2011) finding is the single sharpest empirical result in the paper supporting this.

> [!analysis] Task is the dominant random facet for essay scoring.
> Running generalizability with task as the random facet (rather than rater or occasion) reflects the assumption that essay prompts are the biggest source of construct-irrelevant variance in performance. This is a domain-specific modeling choice; a different assessment (say, clinical simulations) might foreground a different facet.

## Connections

- Fourth area of the [[Automated Scoring Evaluation Framework]].
- Complements [[Human-Automated Score Agreement]] (single-task agreement) by testing across-task consistency.
- Feeds into [[Automated Scoring Implementation Models]] decisions: a program with strong generalizability evidence can move up the liberalization ladder.
- One of the framework criteria also applied to [[Fairness in Automated Scoring]] (generalizability checked by subgroup).
- Demonstrated empirically for [[e-rater]] on TOEFL iBT Writing.

## Open Questions

> [!gap] Thresholds for generalizability coefficients are not specified.
> The paper describes how to compute G and Phi coefficients but does not give a flagging threshold analogous to the 0.70 kappa floor or the 0.15 SMD cap. The comparison is left as "indicate the extent to which the use of e-rater impacts the score reliability," without a pass-fail rule.

> [!gap] Alternate-form prediction is illustrated with one study.
> The Bridgeman, Trapani, & Williamson (2011) result applies to TOEFL iBT. The paper does not catalog analogous findings for GRE, GMAT, or other programs, so it is unclear how universal the "beats a single human" finding is.
