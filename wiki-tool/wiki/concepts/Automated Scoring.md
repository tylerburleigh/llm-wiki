---
type: concept
sources: [[[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]]
created: "2026-04-16"
updated: "2026-04-16"
status: current
tags: [automated-scoring, assessment, essay-scoring, simulation]
---

> [!tldr]
> Automated scoring uses computer algorithms to score constructed-response assessment items; systems divide into simulation-based (narrow, task-bound) and response-type (generalizable across tasks and populations).

## Definition

> [!source] Automated scoring is defined by algorithmic assignment of scores to constructed-response tasks.
> "Automated scoring, in which computer algorithms are used to score constructed-response tasks." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## Why it matters

> [!source] Constructed-response items are expensive to grade by humans.
> Compared to multiple-choice items, constructed-response tasks "take longer to administer with smaller contributions to reliability per unit time and delay score reporting because of the additional effort and expense typically required to recruit, train, and monitor human graders." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] Automated scoring promises scale, consistency, speed, and new feedback modalities.
> Potential advantages include "fast scoring, constant availability of scoring, lower scoring cost, reduced coordination efforts for human graders, greater score consistency, a higher degree of tractability of score logic for a given response, and the potential for a degree of performance-specific feedback that is not feasible under operational human scoring." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] Automated scoring also has distinct risks relative to human scoring.
> Risks include "the cost and effort of developing such systems, the potential for vulnerability in scoring unusual or bad-faith responses inappropriately, and the need to validate the use of such systems and to critically review the construct that is represented in resultant scores." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## Two system families

> [!source] Simulation-based systems score tasks built around realistic scenarios and do not generalize easily.
> "Simulation-based assessments... are characterized by task types that present computerized simulations of realistic scenarios for the examinee to complete, and for which the automated scoring systems are often not readily generalizable to other assessments, and sometimes even to other simulation-based tasks within the same assessment." Examples: USMLE computer-based case simulations, Architect Registration Examination CAD scoring, Uniform CPA Examination, iSkills information technology literacy. [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] Response-type systems score a particular kind of response that recurs across assessments.
> "Designed to score a particular type of response that is in relatively widespread use across various assessments, purposes, and populations and therefore more readily generalizable than simulation-based scoring." Examples include essay scoring, automated scoring of mathematical equations, short written responses, and spoken responses. [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] Essay scoring is the most mature domain within response-type systems.
> More than 12 automated essay evaluation systems exist; the best-known are Intelligent Essay Assessor (IEA), [[e-rater]], Project Essay Grade, and IntelliMetric. [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

## Key Claims

> [!source] Modern automated essay scorers differ in features and statistical methods but share a two-layer design.
> Each well-known engine has "at the core of the capability a set of features that are designed to measure the elements of writing... and... uses one or more statistical methodologies to derive a summary essay score from the feature values computed by the computer. However, these statistical methodologies differ by system." [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!source] High-stakes deployment has moved the field from "can it?" to "how?"
> "The fundamental question of automated scoring for such applications is no longer 'Can it be done?' but 'How should it be done?'" [[Williamson Xi Breyer 2012 - Framework for Automated Scoring]]

> [!analysis] The simulation-vs-response-type split is a generalizability dichotomy, not a technical one.
> Both families can share techniques (regression, NLP, rule-based logic). What separates them is whether the scoring model transfers to new tasks. Response-type systems earn that transferability by fixing the response format (an essay, a spoken utterance, an equation) across assessments; simulation systems buy richer task fidelity by giving it up.

> [!analysis] The face-validity argument for constructed-response is independent of psychometric gain.
> The paper notes constructed-response items sometimes add no construct coverage beyond multiple choice but are retained because stakeholders view them as more authentic. Automated scoring amplifies the economics of keeping these items: even when the unique construct contribution is weak, scoring cost was the binding constraint, and automation relaxes it.

## Connections

- Master concept for [[Automated Scoring Evaluation Framework]], [[Human-Automated Score Agreement]], [[Construct Representation in Automated Scoring]], [[Automated Scoring Implementation Models]].
- Realized at ETS by [[e-rater]]; also realized by IEA, PEG, and IntelliMetric.
- Evaluated under [[Argument-Based Validity]].

## Open Questions

> [!gap] Simulation-based automated scoring is outside the paper's framework scope.
> The paper's framework is illustrated exclusively with [[e-rater]], an essay scorer, and does not specify how the five-area framework adapts when the task is a patient simulation or architectural layout.
