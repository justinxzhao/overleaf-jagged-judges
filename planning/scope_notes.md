# Wiggle Analysis Paper — Scope Notes & Shared Themes

_Working document synthesizing ideas across three sources to scope a potential paper on LLM non-determinism and judge consistency._

---

## Sources

1. **"A Comprehensive Survey of Computational Persuasion"** — Academic survey (likely Anthony Hunter et al., UCL). Covers formal argumentation frameworks, probabilistic models of persuasion, belief revision under argument presentation, and strategic dialogue systems.

2. **"Defeating Nondeterminism in LLM Inference"** — Blog post by Thinking Machines Lab ([link](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/)). Documents that temperature=0 does NOT guarantee determinism due to floating-point non-associativity and batch variance in inference engines like vLLM.

3. **Judge Consistency Taxonomy** — Internal work (`JUDGE_CONSISTENCY_TAXONOMY.md` + `debate_synthesis.py`). Defines three orthogonal axes of LLM judge consistency: Repeatability, Conviction, and Invariance. Implemented in a multi-round debate pipeline for safety eval validation.

---

## Key Ideas Per Source

### Source 1: Computational Persuasion Survey

| Concept | Description | Relevance to Wiggle |
|---|---|---|
| **Probabilistic argumentation** | Arguments have associated belief probabilities; agents update beliefs when presented with new arguments | Directly models what happens when an LLM judge is "challenged" — its verdict probability shifts |
| **Argument strength** | Not binary valid/invalid; arguments have degrees of believability that shift an agent's posterior | Maps to our observation that some counterarguments cause wiggles and others don't |
| **Belief revision** | AGM-style or Bayesian conditionalization when new information (arguments) are presented | Formal framework for conviction wiggle — why does a judge change its mind? |
| **Persuasion as dialogue game** | Asymmetric game between persuader (has goal) and persuadee (updates beliefs) | Our debate synthesis pipeline IS this: Round 2 is the persuader, the LLM judge is the persuadee |
| **Strategic argument selection** | Persuader picks arguments via decision-theoretic planning (POMDPs, decision trees) to maximize belief shift | Could formalize which counterarguments are most "effective" at causing wiggles |
| **Entropy-based persuasion measures** | Effectiveness measured by how much an argument reduces entropy in the persuadee's belief distribution | Potential metric: "persuasion entropy" of a judge — how much does debate reduce its uncertainty? |
| **Position bias / anchoring** | Formal models of how argument presentation order affects acceptance | Exactly what Invariance (Round 4) measures — framing sensitivity |

### Source 2: Thinking Machines Blog — Defeating Nondeterminism

| Concept | Description | Relevance to Wiggle |
|---|---|---|
| **temperature=0 ≠ deterministic** | Even with greedy decoding, outputs vary across runs | Foundational motivation for Repeatability (Round 0) — wiggle exists even at temp=0 |
| **Floating-point non-associativity** | `(a+b)+c ≠ a+(b+c)` in floating point; parallel reductions in attention kernels change accumulation order | Root cause of stochastic wiggle — NOT model uncertainty, but hardware-level jitter |
| **Batch variance** | Changing batch size changes outputs even with `do_sample=False` | Important confound: some "wiggle" is infrastructure noise, not model behavior |
| **Throughput vs. determinism tradeoff** | Inference engines (vLLM) sacrifice bitwise reproducibility for speed | Explains why the problem is practically unavoidable at scale |
| **Off-policy correction** | Proposed mitigation: treat inference as sampling from a distribution, apply corrections | Potential methodology for disentangling "real" model uncertainty from hardware noise |

### Source 3: Judge Consistency Taxonomy (Internal)

| Concept | Description | Paper Contribution |
|---|---|---|
| **Repeatability** | Same question N times → agreement rate. Measures stochastic variance + calibration | Novel axis: separates infrastructure noise from model uncertainty |
| **Conviction** | Challenge with counterargument → does verdict flip? Measures depth of reasoning vs sycophancy | Novel axis: models persuadability of LLM judges |
| **Invariance** | Swap argument presentation order → does verdict flip? Measures framing sensitivity | Novel axis: captures position bias and anchoring |
| **Compound signals** | Low conviction + low invariance = worst judges (no stable principles) | Diagnostic framework for judge quality |
| **Directional asymmetry** | Conviction wiggle measured separately safe→unsafe vs unsafe→safe | Reveals underlying bias in judge disposition |
| **Independence of axes** | 2×2×2 table showing all combinations are possible and meaningful | Argues these are genuinely orthogonal failure modes |

---

## Shared Themes & Crosscutting Ideas

### Theme 1: "Wiggle" as a Multi-Layer Phenomenon

A unified view of LLM non-determinism should distinguish at least **three layers**:

| Layer | Source of variation | Measurement | Example |
|---|---|---|---|
| **Infrastructure wiggle** | FP non-associativity, batch variance, GPU scheduling | Repeatability (Round 0) at temp=0 | Same prompt, same model, different outputs |
| **Stochastic wiggle** | Sampling temperature, top-k/p | Repeatability at temp>0 | Same prompt, model samples differently |
| **Semantic wiggle** | Model's actual uncertainty about the answer | Conviction + Invariance | Model changes mind when challenged or reframed |

The paper could argue that **conflating these layers is a major source of confusion** in LLM evaluation. The Thinking Machines blog shows that Layer 1 exists and is unavoidable. Our taxonomy shows that Layers 2-3 are independently measurable and reveal different failure modes.

### Theme 2: Persuadability as a Window into Calibration

From computational persuasion: an agent's susceptibility to argument-based belief revision reveals its **prior confidence**. From our taxonomy: conviction wiggle rate could be a *proxy for calibration*.

**Key hypothesis for the paper:** A well-calibrated judge should be:
- **Low conviction wiggle on clear-cut cases** (confident, not persuadable)
- **High conviction wiggle on borderline cases** (uncertain, appropriately persuadable)
- The *correlation* between conviction wiggle rate and case difficulty is a calibration signal

This connects persuasion theory (argument strength → belief shift) with evaluation science (calibration = P(correct | confidence)).

### Theme 3: Adversarial Probing vs. Passive Observation

| Approach | What it measures | Limitation |
|---|---|---|
| **Passive** (Repeatability) | Noise floor — how much random variation exists | Can't distinguish confident-wrong from uncertain-right |
| **Adversarial** (Conviction/Invariance) | Decision boundary robustness | Requires designing good challenges |
| **Strategic** (Computational persuasion) | Optimal challenge selection | Theoretical; harder to implement at scale |

The paper could position our debate synthesis pipeline as a **practical middle ground**: structured adversarial probing (not optimal, but systematic) that reveals more than passive repeatability alone.

### Theme 4: Position Bias Has Formal Roots

The invariance axis directly tests what computational persuasion literature formalizes as **order effects in argumentation**. The survey likely covers models where the same two arguments produce different outcomes depending on which is presented first. Our empirical finding (invariance wiggle rates) is the LLM-era instantiation of this well-studied phenomenon.

### Theme 5: Sycophancy as Failed Persuasion Resistance

In the persuasion literature, a persuadee should update beliefs proportionally to argument strength. An LLM that flips its verdict *regardless of argument quality* (high conviction wiggle across all cases) is exhibiting **sycophancy** — it's not evaluating argument strength at all, just recency/authority bias. This gives sycophancy a formal grounding in argumentation theory.

---

## Potential Duplicated / Prior Work to Acknowledge

| Our contribution | Related prior work | Differentiation |
|---|---|---|
| Repeatability axis | SimpleQA (OpenAI, 2024); TML blog | We measure it specifically for safety judges, not QA |
| Conviction axis | Computational persuasion literature (Hunter et al.) | We operationalize it empirically with LLMs, not formal agents |
| Invariance axis | Position bias literature (Wang et al., 2023 "Large Language Models are not Fair Evaluators") | We embed it in a unified taxonomy with conviction + repeatability |
| Debate synthesis pipeline | LLM-as-judge debate frameworks (ChatEval, etc.) | Our pipeline is specifically designed to measure *consistency*, not *accuracy* |
| Wiggle as calibration signal | Calibration literature (Kadavath et al. "Language Models (Mostly) Know What They Know") | We propose *adversarial* calibration measurement through debate, not just self-reported confidence |

---

## Suggested Paper Scope

### Title ideas
- "Wiggle Analysis: A Taxonomy of Non-Determinism in LLM Safety Judges"
- "How Much Do Judges Wiggle? Measuring Consistency, Conviction, and Calibration in LLM-as-Judge Safety Evaluation"
- "From Hardware Jitter to Sycophantic Capitulation: A Multi-Layer View of LLM Non-Determinism"

### Core argument
LLM non-determinism is not one phenomenon but many, and conflating them leads to unreliable safety evaluations. We propose a three-axis taxonomy (Repeatability, Conviction, Invariance) grounded in computational argumentation theory, implement it as a practical multi-round debate pipeline, and show that different axes reveal different failure modes with different implications for trust in automated safety judgments.

### What's novel
1. **The taxonomy itself** — three orthogonal, independently measurable axes of judge consistency
2. **The connection to formal argumentation** — grounding conviction/invariance in computational persuasion theory
3. **The multi-layer decomposition** — separating infrastructure noise from semantic uncertainty from persuadability
4. **Empirical evidence** that these axes are independent (from the debate synthesis pipeline runs)
5. **Wiggle as calibration signal** — the hypothesis that conviction wiggle rate correlates with case difficulty

### What the paper should NOT try to be
- Not a full computational persuasion paper (we're borrowing the framework, not extending it)
- Not a deterministic inference paper (TML covers the infrastructure layer well)
- Not a general LLM evaluation benchmark paper

---

## Open Questions

1. **Can we actually show calibration?** Does conviction wiggle rate correlate with case difficulty or human disagreement rate? This would be the strongest empirical contribution.
2. **How much wiggle is infrastructure vs. semantic?** Comparing temp=0 repeatability variance against conviction variance would quantify this.
3. **Does the taxonomy generalize beyond safety?** Would the same axes apply to factuality judges, code review judges, etc.?
4. **What's the right baseline?** Human judges also have repeatability/conviction/invariance profiles — comparing LLM judges to human baselines on these axes would be powerful.
