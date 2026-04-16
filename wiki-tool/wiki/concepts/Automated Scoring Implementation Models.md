---
type: concept
sources: [[[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]]
created: "2026-04-16"
updated: "2026-04-16"
status: current
tags: [automated-scoring, implementation, deployment, validity]
---

> [!tldr]
> Williamson, Xi, and Breyer order five implementation models for automated scoring from conservative to liberal — human-only, automated QC of human, combined human-plus-automated, composite, and automated-only — and tie the evidence burden to position on the ladder.

## Definition

> [!source] Five implementation models are presented in increasing liberalization.
> "A rough ordering (from more conservative to more liberal use) of implementations for use of automated scoring is as follows: Human scoring; Automated quality control of human scoring; Automated and human scoring; Composite scoring; Automated scoring alone." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## The five models

**Table 1.** Implementation models, definitions, and sample programs (from the paper).

| # | Model | How scores are combined | Sample program |
|---|---|---|---|
| 1 | Human scoring | Average of two human scores (or a single human for low stakes); automated may run as a silent "shadow" | Historical default |
| 2 | Automated QC of human | Single human plus automated; if their scores differ beyond a threshold, a second human is called in. Reported score is the human(s) only | GRE Issue and Argument |
| 3 | Automated and human | Single human and automated scores are averaged or summed into the reported score; discrepancies trigger additional human scoring with program-specific resolution rules | TOEFL Independent and Integrated (using [[e-rater]]); GMAT Argument and Issue (using IntelliMetric after GMAT's vendor transition from e-rater) |
| 4 | Composite scoring | Human scores are treated as one more weighted feature alongside automated features to compute a composite score | No operational example cited in this paper |
| 5 | Automated scoring alone | Reported score is the automated score only | IEA in Pearson Test of English (PTE) |

> [!source] Model 2 (automated QC) and Model 3 (combined) are the workhorse models at ETS.
> The paper explicitly attributes GRE Issue and Argument tasks to Model 2 (citing Bridgeman et al., 2009) and TOEFL Independent and Integrated essays plus GMAT Argument and Issue prompts to Model 3 (citing Attali 2009; Rudner et al., 2006). [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] Model 5 (automated-only) is in use at Pearson for PTE.
> "The IEA automated scoring engine is deployed in the Pearson Test of English used for high-stakes purposes. However, unlike e-rater, the IEA engine is used as the sole rater." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## Key Claims

> [!source] Higher stakes demand more evidence, regardless of model.
> "The use of automated scoring for high-stakes decisions is subject to a higher burden of both the amount and quality of evidence to support the intended use than for lower-stakes and practice applications." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] Model choice depends on multiple factors beyond stakes.
> "The choice of implementation policies for automated scoring would be influenced by the quantity and quality of evidence supporting the use of automated scoring, the particular task types, testing purpose, test-taker population to which it is applied, and the degree of receptivity of the population of score users to models of implementation." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] A versioned development path is recommended.
> "A versioned approach to capability development and application to operational programs should be encouraged. Under this versioning approach, the use of emerging automated capabilities will be restricted to low-stakes nonconsequential uses, although more mature and proven capabilities may be recommended for higher stakes applications." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] Automated-only deployment requires stricter evaluation criteria.
> "If automated scoring were to be used as the only rater to score a consequential assessment, more stringent criteria may be advisable." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] Construct fit requirements also rise with liberalization.
> "Using automated scoring as the sole rater demands a much greater degree of congruence between the automated scoring features and the construct of interest than using automated scoring in conjunction with human scoring." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!analysis] The ladder encodes a liability model, not a quality model.
> Each step up the ladder does not necessarily produce more accurate reported scores. It shifts more scoring weight to the automated engine, which raises the consequences of engine failure. Conservatism means keeping human scoring in the loop as a fallback. Shipping Model 5 (automated-only) where Model 2 would suffice is an appetite decision about who absorbs errors.

> [!analysis] Composite scoring (Model 4) is conspicuously without an operational example in this paper.
> The paper defines Model 4 but cites no deployment. That likely reflects how much harder it is to defend a weighted human-plus-features composite on construct-explanation grounds: the weighting turns the human score into a latent feature and blurs what the reported score means.

> [!analysis] Model choice is partly a stakeholder-psychology decision.
> "Receptivity of the population of score users" is listed as a selection factor alongside empirical evidence. Two programs using the same engine with similar empirical evidence can land on different models because their score users (admissions committees, licensing boards) trust automated scoring differently. See [[GRE vs TOEFL e-rater Implementation]].

## Connections

- Defines the deployment dimension of the [[Automated Scoring Evaluation Framework]].
- Interacts directly with [[Human-Automated Score Agreement]] (adjudication thresholds differ by model).
- Instantiated by [[e-rater]] in Models 2 and 3; by IEA in Model 5 at PTE.
- Program-level contrast captured in [[GRE vs TOEFL e-rater Implementation]].

## Open Questions

> [!gap] Stricter criteria for Model 5 are not specified.
> The paper says they "may be advisable" but does not quantify them.

> [!gap] Composite scoring (Model 4) is defined but not illustrated.
> No operational or even pilot example of Model 4 is given in this paper.
