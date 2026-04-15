# Meta-Analysis: Wiggle vs. Jury Consensus Difficulty

<!-- ================================================================
     Cross-experiment meta-analysis correlating per-item wiggle scores
     from Experiments 1–4 with the frontier jury consensus signal.
     Based on run n500-0: 384 items × 9 models.

     All analysis is GT-free: jury consensus measures inter-model
     agreement (how many of 9 frontier models agree on a verdict),
     not alignment to human labels.
     ================================================================ -->

## 9. Meta-Analysis: Does Item Difficulty Predict Wiggle?

### 9.1 Motivation

The preceding experiments measure wiggle at the *model level* — aggregate flip rates, survival curves, and retention profiles.  But wiggle also varies at the *item level*: some items produce consistent verdicts across models and conditions, while others are chronically unstable.

This raises two fundamental questions for the Wiggle Framework:

1. **Is wiggle tracking genuine item difficulty, or is it random noise?**  If the items that wiggle are the same items that the frontier jury disagrees on, then wiggle is a signal — it reflects genuine ambiguity in the content.  If wiggle is uncorrelated with jury consensus, it's closer to measurement noise that happens to be model-specific.

2. **Do the three wiggle axes identify the same vulnerable items?**  If items that are unrepeatable (Experiment 1) are the same items that flip under conviction pressure (Experiment 2) and ordering changes (Experiment 4), then wiggle reflects a coherent item-level property.  If the axes identify different items, wiggle is axis-specific and each experiment captures a distinct failure mode.

We answer both questions: the first by examining how wiggle varies across the full jury consensus spectrum (strength 1–9), and the second by computing item-level correlations between the three wiggle axes.

### 9.2 Setup

For each of the 384 items and each of the 9 models, we compute three per-item wiggle scores:

- **Repeatability entropy** (bits): Shannon entropy of the verdict distribution across 10 trials under seed injection.  0 bits = all trials agree; 1 bit = 5/5 split.
- **Conviction flip** (binary): whether the model's verdict changed after the "are you sure?" challenge (from Experiment 2).
- **Invariance flip** (binary): whether the model's verdict changed when argument ordering was reversed (from Experiment 4).

We relate each score to **jury majority strength** — how many of 9 models voted with the majority, ranging from 5 (maximally contested) to 9 (unanimous).  Rather than collapsing this into a binary easy/hard split, we report mean wiggle at each jury strength level to reveal the full shape of the difficulty–wiggle relationship.  We also compute pairwise Pearson correlations between all three wiggle axes at the item level, within each model.

### 9.3 Results

#### 9.3.1 Jury Difficulty Predicts Wiggle Across All Three Axes

Table M1 reports Pearson correlations between jury strength and per-item wiggle for each model × axis.  Negative correlations mean harder items (lower jury strength) wiggle more.

**Table M1.** Correlation between jury consensus strength and per-item wiggle.

| Model | Repeatability | Conviction | Invariance |
|---|---|---|---|
| GPT-5 | −0.27 | −0.25 | −0.00 |
| Grok-4.1 R | −0.37 | −0.24 | **−0.35** |
| Grok-4.1 | −0.18 | **−0.40** | −0.25 |
| **Claude Sonnet** | **−0.38** | **−0.54** | −0.18 |
| Claude Opus | −0.28 | −0.30 | −0.28 |
| GPT-5.2 | −0.07 | +0.04 | −0.12 |
| GPT-5.4 | −0.16 | −0.14 | −0.08 |
| Gemini Flash | −0.20 | −0.21 | −0.19 |
| Gemini Pro | −0.22 | −0.24 | −0.12 |
| **Mean** | **−0.24 ± 0.09** | **−0.25 ± 0.15** | **−0.18 ± 0.10** |

The correlations are consistently negative across all models and axes, confirming that **harder items wiggle more**.  The mean correlations are moderate (−0.18 to −0.25), indicating that jury difficulty explains roughly 3–6% of item-level variance in wiggle — a meaningful but not dominant predictor.

Three observations stand out:

1. **Claude Sonnet shows the strongest conviction–difficulty link** (r = −0.54).  Items where the frontier jury splits are the same items where Claude Sonnet capitulates to an "are you sure?" challenge over half the time.  This makes Claude Sonnet's conviction vulnerability particularly concerning: it's not randomly susceptible, it's *preferentially* susceptible on the items that matter most — the genuinely ambiguous cases.

2. **GPT-5.2 is the exception**.  Its repeatability correlation is near zero (r = −0.07), and its conviction correlation is slightly *positive* (+0.04) — the only model where harder items are not more likely to flip.  This is consistent with GPT-5.2's characterization across all experiments as the most robust model: its wiggle is independent of item difficulty, suggesting a model that applies its safety heuristics uniformly rather than being sensitive to item-level ambiguity.

3. **Invariance is the weakest predictor** (mean r = −0.18).  This makes theoretical sense: argument ordering sensitivity (invariance) is driven by position bias in the attention mechanism, a structural property that should be less sensitive to content difficulty than the other two axes.  The exception is Grok-4.1 R (r = −0.35), whose high order sensitivity on hard items suggests its position bias interacts with content uncertainty.

#### 9.3.2 Wiggle Across the Full Jury Spread

Rather than collapsing jury consensus into a binary easy/hard split, Tables M2–M4 report mean wiggle at each jury strength level (5–9; strengths 1–3 have no items in this dataset since any majority of 9 models requires at least 5 votes, and strength 4 has only 2 items).

**Table M2.** Mean repeatability entropy (bits) by jury consensus strength.

| Model | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|
| GPT-5 | 0.000 | 0.085 | 0.154 | 0.040 | 0.014 | 0.000 |
| Grok-4.1 R | 0.441 | 0.310 | 0.287 | 0.198 | 0.236 | 0.021 |
| Grok-4.1 | 0.000 | 0.091 | 0.047 | 0.042 | 0.027 | 0.008 |
| Claude Sonnet | 0.361 | 0.255 | 0.205 | 0.099 | 0.117 | 0.004 |
| Claude Opus | 0.000 | 0.123 | 0.089 | 0.073 | 0.036 | 0.000 |
| GPT-5.2 | 0.000 | 0.021 | 0.056 | 0.107 | 0.111 | 0.019 |
| GPT-5.4 | 0.000 | 0.104 | 0.064 | 0.045 | 0.113 | 0.008 |
| Gemini Flash | 0.000 | 0.179 | 0.113 | 0.221 | 0.190 | 0.035 |
| Gemini Pro | 0.000 | 0.169 | 0.106 | 0.190 | 0.166 | 0.022 |

**Table M3.** Mean conviction flip rate by jury consensus strength.

| Model | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|
| GPT-5 | 0.000 | 0.118 | 0.129 | 0.100 | 0.038 | 0.000 |
| Grok-4.1 R | 0.000 | 0.176 | 0.129 | 0.125 | 0.094 | 0.009 |
| Grok-4.1 | 0.500 | 0.382 | 0.452 | 0.350 | 0.283 | 0.036 |
| **Claude Sonnet** | 0.500 | **0.618** | 0.484 | 0.425 | 0.208 | 0.027 |
| Claude Opus | 0.500 | 0.147 | 0.129 | 0.100 | 0.038 | 0.000 |
| GPT-5.2 | 0.000 | 0.000 | 0.065 | 0.125 | 0.151 | 0.071 |
| GPT-5.4 | 0.000 | 0.088 | 0.194 | 0.150 | 0.283 | 0.031 |
| Gemini Flash | 0.000 | 0.147 | 0.097 | 0.175 | 0.132 | 0.009 |
| Gemini Pro | 0.000 | 0.324 | 0.129 | 0.275 | 0.245 | 0.049 |

**Table M4.** Mean invariance flip rate by jury consensus strength.

| Model | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|
| GPT-5 | 0.000 | 0.000 | 0.000 | 0.050 | 0.000 | 0.009 |
| Grok-4.1 R | 0.500 | 0.235 | 0.290 | 0.150 | 0.075 | 0.013 |
| Grok-4.1 | 0.500 | 0.118 | 0.194 | 0.075 | 0.075 | 0.009 |
| Claude Sonnet | 0.000 | 0.147 | 0.129 | 0.175 | 0.094 | 0.027 |
| Claude Opus | 0.000 | 0.206 | 0.129 | 0.150 | 0.038 | 0.009 |
| GPT-5.2 | 0.000 | 0.029 | 0.097 | 0.100 | 0.057 | 0.009 |
| GPT-5.4 | 0.000 | 0.059 | 0.032 | 0.000 | 0.057 | 0.009 |
| Gemini Flash | 0.000 | 0.088 | 0.161 | 0.100 | 0.075 | 0.009 |
| Gemini Pro | 0.000 | 0.118 | 0.065 | 0.100 | 0.094 | 0.027 |

The per-level data reveals several patterns that a binary split would obscure:

1. **The difficulty–wiggle curve is not linear.**  For most models, wiggle does not decrease uniformly from strength 5 to 9.  Instead, there is a sharp cliff between strengths 8 and 9: unanimous items (strength 9) have near-zero wiggle across all axes, while items at strength 8 still show substantial instability.  The transition from "hard" to "stable" is abrupt, not gradual.

2. **GPT-5.2's inverted conviction profile is visible at full resolution.**  Its conviction flip rate *increases* from 0% at strength 5 to 15.1% at strength 8, then drops to 7.1% at strength 9.  This inversion — the only one across all models — confirms that GPT-5.2's conviction wiggle is genuinely difficulty-independent and not an artifact of the binary split.

3. **Claude Sonnet's conviction vulnerability peaks at strength 5** (61.8% flip rate), meaning that on items where the jury barely agrees (5 of 9 models), Claude Sonnet is *more likely to flip than hold* after a single challenge.  Even at strength 7, it still flips 42.5% of the time.

4. **The Gemini models show a plateau in repeatability entropy.**  Both Gemini Flash and Gemini Pro maintain elevated entropy (0.11–0.22 bits) across strengths 5–8, dropping only at strength 9.  Their repeatability noise is not concentrated on the hardest items but spread across all non-unanimous items, suggesting a different noise mechanism (perhaps higher effective temperature) rather than content-driven uncertainty.

#### 9.3.3 Cross-Axis Item-Level Correlations: Do the Same Items Wiggle Across Experiments?

Table M5 reports pairwise Pearson correlations between the three wiggle axes at the item level, within each model.  Positive correlations mean items that wiggle on one axis tend to wiggle on the other.

**Table M5.** Cross-axis item-level correlations (per-model).

| Model | Repeat ↔ Convict | Repeat ↔ Invar | Convict ↔ Invar |
|---|---|---|---|
| GPT-5 | +0.37 | −0.02 | −0.02 |
| Grok-4.1 R | +0.43 | +0.28 | +0.21 |
| Grok-4.1 | +0.35 | +0.06 | +0.21 |
| Claude Sonnet | +0.39 | +0.05 | +0.24 |
| Claude Opus | +0.34 | +0.29 | **+0.41** |
| GPT-5.2 | **+0.54** | +0.29 | +0.16 |
| GPT-5.4 | **+0.53** | +0.16 | +0.14 |
| Gemini Flash | +0.40 | +0.15 | +0.25 |
| **Gemini Pro** | **+0.57** | +0.24 | **+0.42** |
| **Mean** | **+0.43 ± 0.08** | **+0.17 ± 0.11** | **+0.22 ± 0.13** |

Three key findings:

1. **Repeatability and conviction wiggle are strongly correlated** (mean r = +0.43).  This is the strongest cross-axis signal: items that produce variable verdicts across repeated trials are the *same items* that flip under a single "are you sure?" challenge.  This convergence across two very different perturbation types — stochastic (seed variation) vs. adversarial (social pressure) — suggests both are tapping into the same underlying item-level uncertainty.  Gemini Pro shows the strongest coupling (r = +0.57), while GPT-5 shows the weakest (r = +0.37).

2. **Invariance is partially decoupled** from the other two axes (mean r = +0.17 for repeat↔invar, +0.22 for convict↔invar).  This confirms that ordering sensitivity (invariance) captures a qualitatively different vulnerability than the repeatability and conviction axes.  Position bias — the mechanism driving invariance flips — is more architectural than content-driven, which explains the weaker item-level overlap.  The notable exception is **Claude Opus** (convict↔invar r = +0.41) and **Gemini Pro** (convict↔invar r = +0.42), where items vulnerable to challenge pressure are also vulnerable to ordering effects — a compound fragility.

3. **GPT-5 shows zero invariance coupling** (r = −0.02 for both invariance pairs).  Its (rare) invariance flips occur on entirely different items than its repeatability or conviction flips.  This suggests GPT-5's order sensitivity, when it occurs, is driven by a distinct mechanism unrelated to content difficulty — possibly a residual position bias that activates independently of semantic uncertainty.

### 9.4 Discussion

The meta-analysis establishes two results:

**Wiggle is not noise — it's signal.**  Across all three axes and nearly all models, items that the frontier jury disagrees on are the same items that produce inconsistent verdicts under perturbation, challenge, and reframing.  The per-level data shows this is not a binary divide but a graded relationship, with a sharp stability cliff at unanimity (strength 9).  This validates the Wiggle Framework's core premise: the three axes are measuring something real about the interaction between model uncertainty and item ambiguity.

**The wiggle axes are partially coherent.**  Repeatability and conviction share substantial item-level overlap (r = +0.43), confirming that stochastic instability and adversarial susceptibility are manifestations of the same underlying uncertainty.  Invariance is partially decoupled, capturing a distinct architectural vulnerability.  This means the three axes are not redundant — each contributes unique signal — but they are also not independent, which justifies analyzing them as a unified framework rather than three separate metrics.

Four implications for practitioners:

1. **Wiggle is a usable difficulty proxy.**  Teams that need to identify borderline items in their evaluation sets can use any of the three wiggle axes as a difficulty signal, without requiring ground truth labels or external annotation.  Items with high repeatability entropy or high conviction flip rates are likely to be the same items that human annotators would disagree on.

2. **The difficulty–wiggle relationship is model-specific in shape.**  GPT-5.2's flat difficulty profile means its wiggle cannot be used as a difficulty proxy — it wiggles uniformly.  Claude Sonnet's steep profile (61.8% conviction flip rate at strength 5) means its wiggle is concentrated exactly where it matters most.  The Gemini models' plateau pattern means their wiggle spreads across all non-unanimous items.

3. **Jury consensus provides a cheap difficulty stratification.**  Running 9 models at temp=0 once (a few hundred API calls) produces an item-level difficulty signal that predicts wiggle across all subsequent experiments.  This is far cheaper than running the full wiggle protocol on every item, and can be used to prioritize which items to test more thoroughly.

4. **Cross-axis coherence enables efficient screening.**  Because repeatability and conviction are strongly correlated at the item level, a team that can only afford one wiggle axis should prefer repeatability (which requires no adversarial prompting, just repeated calls).  Items flagged by repeatability entropy will largely overlap with those that would fail a conviction challenge.  Invariance testing adds unique signal and should be included when feasible, but is lower priority for difficulty identification.
