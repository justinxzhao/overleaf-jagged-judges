# Experiment 1: Three-Axis Independence

<!-- ================================================================
     Paper sections for the Wiggle Framework — Experiment 1 findings.
     Based on run n500-0: 384 borderline items × 9 frontier models,
     10 trials per condition.

     Primary focus: behavioral wiggle (verdict instability across the
     three axes).  Accuracy vs human GT is reported as a secondary
     validation but is not the focus — the GT labels themselves have
     inter-annotator disagreement on these borderline items.
     ================================================================ -->

## 4. Experiment 1: Three-Axis Independence

### 4.1 Setup

We evaluate whether the three wiggle axes — Repeatability, Conviction, and Invariance — capture genuinely independent failure modes.  We sample 384 borderline items from WildGuardMix (prompt-response pairs where the model complied with a non-benign prompt), stratified across 14 harm subcategories, and test 9 frontier models: GPT-5, GPT-5.2, GPT-5.4, Claude 4.5 Sonnet, Claude 4.5 Opus, Grok-4.1, Grok-4.1 Reasoning, Gemini 3 Flash, and Gemini 3.1 Pro.

Each model judges every item under the following protocol:

- **Repeatability** is measured under three conditions, each with 10 independent trials:
  - *Condition A (temp=0)*: greedy decoding, identical prompts — measures infrastructure nondeterminism only.
  - *Condition B (seed injection at temp=0)*: greedy decoding with a unique 64-character random string appended to each prompt — injects prompt-level entropy without changing the task.
  - *Condition C (temp=0.7)*: sampling at temperature 0.7 — measures combined prompt and sampling variation.
- **Conviction** is probed with a single challenge turn: after the model's initial verdict (L0), it is asked "Are you sure about that assessment? Please reconsider carefully." The flip rate measures how often the model reverses its verdict under mild social doubt.
- **Invariance** is tested by presenting two opposing reviewer arguments (one arguing "acceptable," one arguing "unacceptable") in both orderings.  The flip rate measures how often the model's verdict changes based solely on which argument is presented first.

All prompts include the full WildGuard safety policy as context.  A 9-model frontier jury provides a consensus signal used as a difficulty proxy in subsequent experiments.

### 4.2 Results

#### 4.2.1 Repeatability: Consistency Under Re-prompting

Table 1 reports agreement rates — the fraction of items where all 10 trials produce an identical verdict — across the three conditions.

**Table 1.** Repeatability agreement rate (%) by model and condition.  Higher is more consistent.  Bold indicates the lowest agreement rate for each model (i.e., the condition that reveals the most wiggle).

| Model | temp=0 | Seed Injection | temp=0.7 |
|---|---|---|---|
| GPT-5 | 98.2 | 96.6 | **96.1** |
| Grok-4.1 Reasoning | **85.9** | 85.4 | 85.2 |
| Grok-4.1 | 98.4 | **96.4** | 96.6 |
| Claude 4.5 Sonnet | 93.9 | 90.8 | **88.7** |
| Claude 4.5 Opus | 99.5 | **95.5** | 97.1 |
| GPT-5.2 | 93.8 | 93.8 | **93.0** |
| GPT-5.4 | 95.1 | 94.5 | **94.5** |
| Gemini 3 Flash | 99.7 | **86.7** | 88.5 |
| Gemini 3.1 Pro | 97.1 | **89.3** | 87.0 |

Several findings emerge:

1. **Wiggle is non-trivial even at temp=0.**  Most models achieve >95% agreement under greedy decoding, but Grok-4.1 Reasoning is a notable outlier at 85.9% — roughly 1 in 7 items produces inconsistent verdicts across identical re-runs.  This sets the infrastructure noise floor.

2. **Seed injection reveals hidden fragility.**  Gemini 3 Flash drops from 99.7% (temp=0) to 86.7% (seed injection) — a 13-point swing from a random string appended to the prompt that models are explicitly told to ignore.  Claude 4.5 Opus drops from 99.5% to 95.5%.  In contrast, Grok-4.1 non-reasoning barely moves (98.4% → 96.4%).  This suggests that some models' apparent determinism is fragile: their verdicts are tightly balanced near a decision boundary, and even irrelevant prompt perturbations are sufficient to tip them.

3. **The three conditions differentiate for most models.**  Six of nine models show >2 percentage-point spreads between their most and least consistent conditions, confirming that the three-condition design captures meaningfully different sources of variation.  Three models (Grok-4.1 Reasoning, GPT-5.2, GPT-5.4) show flatter profiles, which is itself informative: these models exhibit similar levels of nondeterminism regardless of the noise source.

4. **Seed injection does not distort the verdict distribution.**  Table 2 shows the unsafe call rate (fraction of items where the majority verdict across 10 trials is "unsafe") under temp=0 vs. seed injection.  The distributions are nearly identical, confirming the technique introduces variation without systematically biasing verdicts.

**Table 2.** Unsafe call rate by model: temp=0 vs seed injection (majority vote over 10 trials).

| Model | temp=0 | Seed Injection | Δ |
|---|---|---|---|
| GPT-5 | 69.8% | 69.5% | −0.3 pp |
| Grok-4.1 Reasoning | 58.1% | 58.1% | 0.0 pp |
| Grok-4.1 | 59.6% | 59.6% | 0.0 pp |
| Claude 4.5 Sonnet | 65.6% | 65.1% | −0.5 pp |
| Claude 4.5 Opus | 64.3% | 63.3% | −1.0 pp |
| GPT-5.2 | 82.6% | 80.7% | −1.9 pp |
| GPT-5.4 | 79.2% | 78.6% | −0.5 pp |
| Gemini 3 Flash | 54.9% | 54.4% | −0.5 pp |
| Gemini 3.1 Pro | 55.5% | 53.9% | −1.6 pp |

The largest shift is GPT-5.2 (−1.9 pp), well within noise.  Notably, the models show strikingly different baseline unsafe rates — from 54.9% (Gemini Flash) to 82.6% (GPT-5.2) — despite judging the same items.  This 28-point spread in verdict distribution across frontier models is itself a form of "between-model wiggle" that practitioners should be aware of when comparing evaluation results across judges.

#### 4.2.2 Conviction: Persuadability Under Challenge

Table 3 reports the conviction flip rate: how often a model reverses its verdict after a single "Are you sure?" challenge.

**Table 3.** Conviction flip rate and directional breakdown.

| Model | Flip Rate | safe→unsafe | unsafe→safe |
|---|---|---|---|
| GPT-5 | 3.6% | 13 | 1 |
| Grok-4.1 Reasoning | 5.7% | 18 | 4 |
| Grok-4.1 | 16.9% | 40 | 25 |
| Claude 4.5 Sonnet | **18.5%** | 36 | 24 |
| Claude 4.5 Opus | 4.2% | 1 | 8 |
| GPT-5.2 | 8.1% | 19 | 12 |
| GPT-5.4 | 9.6% | 25 | 12 |
| Gemini 3 Flash | 6.2% | 21 | 3 |
| Gemini 3.1 Pro | 13.0% | 22 | 28 |

Key observations:

1. **There is a 5× gap in persuadability across frontier models.**  Claude 4.5 Sonnet flips on 18.5% of items — nearly 1 in 5 — after a single generic challenge.  GPT-5 flips on only 3.6%.  This gap is striking given that these models are of comparable capability.

2. **Intra-family differences are large.**  Claude 4.5 Sonnet (18.5%) vs. Claude 4.5 Opus (4.2%) represents a 4.4× gap within the same model family.  This suggests conviction robustness is not purely a property of the training corpus or base architecture, but is sensitive to RLHF/alignment tuning choices.

3. **Most flips are toward restriction (safe→unsafe).**  Seven of nine models flip more often from safe to unsafe than the reverse.  The exceptions are Claude 4.5 Opus (1 safe→unsafe vs. 8 unsafe→safe) and Gemini 3.1 Pro (22 vs. 28), which show the opposite pattern.  This directional asymmetry — models are more easily talked *into* flagging content than *out of* flagging it — has direct implications for safety deployment and is explored in depth in Experiment 4.

4. **Flipping is directionally noisy, not systematically corrective.**  The challenge introduces roughly symmetric noise: it flips verdicts in both directions without a consistent tendency toward or away from the model's initial position being well-calibrated.  The one exception is Gemini 3 Flash, where safe→unsafe flips (21) outnumber unsafe→safe flips (3) by 7:1, suggesting this model's conviction wiggle has a strong directional component.

#### 4.2.3 Invariance: Sensitivity to Argument Ordering

Table 4 reports the invariance flip rate: how often a model's verdict changes when the same two opposing arguments are presented in reversed order.

**Table 4.** Invariance flip rate and order bias.

| Model | Flip Rate | Unsafe rate (acceptable first) | Unsafe rate (unacceptable first) | Order bias |
|---|---|---|---|---|
| GPT-5 | **1.0%** | 80.7% | 79.7% | −1.0 pp |
| Grok-4.1 Reasoning | **8.1%** | 60.4% | 65.4% | +4.9 pp |
| Grok-4.1 | 5.2% | 64.1% | 66.7% | +2.6 pp |
| Claude 4.5 Sonnet | 7.0% | 74.0% | 78.1% | +4.2 pp |
| Claude 4.5 Opus | 5.5% | 68.2% | 68.2% | 0.0 pp |
| GPT-5.2 | 3.4% | 80.7% | 82.6% | +1.8 pp |
| GPT-5.4 | 2.1% | 82.3% | 80.7% | −1.6 pp |
| Gemini 3 Flash | 4.7% | 64.6% | 62.0% | −2.6 pp |
| Gemini 3.1 Pro | 5.5% | 59.1% | 56.2% | −2.9 pp |

1. **GPT-5 is remarkably invariant** — only 1.0% of items flip when argument order changes, suggesting its verdicts are driven by the content rather than the framing.  The next most stable models are GPT-5.4 (2.1%) and GPT-5.2 (3.4%), all from the same model family.

2. **Grok-4.1 Reasoning is the most order-sensitive** at 8.1%, which is 8× higher than GPT-5.  This model also shows the strongest order bias: when the unacceptable argument is presented first, the unsafe rate increases by 4.9 percentage points — a recency effect where the second argument (which is the acceptable one in this case) has less influence.

3. **Claude 4.5 Sonnet shows a similar recency pattern** (+4.2 pp order bias), while Claude 4.5 Opus shows zero net bias despite a 5.5% flip rate — meaning its flips are balanced in both directions.

4. **The Gemini models show a mild primacy effect** — they are slightly *less* likely to say "unsafe" when the unacceptable argument is presented first, suggesting the first argument carries more weight.  This is the opposite of the recency effect seen in Grok and Claude models.

#### 4.2.4 Three-Axis Independence

The central claim of the Wiggle Framework is that the three axes measure genuinely different failure modes.  We test this by computing Pearson correlations between per-item wiggle scores across axes: repeatability entropy (averaged over the three conditions), a binary conviction flip indicator, and a binary invariance flip indicator.

**Table 5.** Pearson correlations between wiggle axes.

| Model | Rep ↔ Conv | Rep ↔ Inv | Conv ↔ Inv | n |
|---|---|---|---|---|
| GPT-5 | +0.41 | **−0.02** | **−0.02** | 384 |
| Grok-4.1 Reasoning | +0.45 | +0.30 | +0.21 | 384 |
| Grok-4.1 | +0.48 | +0.09 | +0.21 | 384 |
| Claude 4.5 Sonnet | +0.44 | +0.05 | +0.24 | 384 |
| Claude 4.5 Opus | +0.40 | +0.31 | +0.41 | 384 |
| GPT-5.2 | +0.60 | +0.24 | +0.16 | 384 |
| GPT-5.4 | +0.59 | +0.14 | +0.14 | 384 |
| Gemini 3 Flash | +0.50 | +0.20 | +0.25 | 384 |
| Gemini 3.1 Pro | +0.61 | +0.32 | +0.42 | 384 |
| **Mean** | **+0.50** | **+0.18** | **+0.22** | |

The results support partial independence with theoretically grounded overlap:

1. **Repeatability ↔ Invariance is weakly correlated** (mean *r* = 0.18, range −0.02 to +0.32).  For GPT-5, the correlation is effectively zero (*r* = −0.02).  This means that an item a model reproduces inconsistently is not the same item where argument ordering matters — these are genuinely different failure modes.

2. **Conviction ↔ Invariance is similarly weak** (mean *r* = 0.22, range −0.02 to +0.42).  Again, persuadability under direct challenge and sensitivity to framing are largely independent phenomena.

3. **Repeatability ↔ Conviction shows moderate correlation** (mean *r* = 0.50, range +0.40 to +0.61).  This is the expected exception: items that produce inconsistent verdicts across re-runs (high entropy) are the same items where the model is near its decision boundary, and therefore more susceptible to an "are you sure?" nudge.  Crucially, this correlation, while meaningful, is far from unity — a model can be near its decision boundary (high repeatability entropy) yet still resist a direct challenge, or conversely be highly consistent yet fold immediately when challenged.

4. **No correlation exceeds 0.8**, the threshold that would indicate redundancy.  Even the strongest individual correlation (Gemini 3.1 Pro, rep↔conv = 0.61) leaves 63% of the variance unexplained.

Figure [ref:correlation_aggregated] shows the aggregated correlation matrix, and Figure [ref:scatter_gpt5] illustrates the near-zero rep↔inv and conv↔inv correlations for GPT-5.

#### 4.2.5 Model Profiles

The three-axis framework reveals distinct "wiggle profiles" that a single consistency metric would obscure.  We highlight four archetypes emerging from the data:

- **GPT-5: The Rock.**  Highly consistent (96–98%), resistant to challenge (3.6% flip rate), and nearly perfectly invariant to argument ordering (1.0%).  If a safety team needs a single reliable judge, this model minimizes wiggle on all axes.

- **Claude 4.5 Sonnet: The Pushover.**  Moderately consistent (89–94%) but highly persuadable (18.5% flip rate) and moderately order-sensitive (7.0%).  This model produces reasonable baseline verdicts but can be easily talked out of them — a liability in adversarial evaluation settings.

- **Gemini 3 Flash: The Determinism Mirage.**  Near-perfect at temp=0 (99.7%) but drops to 86.7% with seed injection — a 13-point gap that no other model exhibits.  Moderate on other axes.  This pattern cautions against equating greedy-decoding consistency with true robustness.

- **Grok-4.1 Reasoning: The Noisy Dissenter.**  The least repeatable model overall (85%) yet moderately resistant to challenge (5.7%) — it's inconsistent on its own but doesn't easily capitulate to pressure.  It is also the most order-sensitive (8.1%), suggesting its inconsistency is driven by sensitivity to superficial prompt features rather than deep uncertainty.

#### 4.2.6 Frontier Jury Consensus

All 9 models serve as a frontier jury, judging each item at temp=0.  The jury achieves a mean majority strength of 8.0/9 — the jury is largely unanimous.  The jury consensus strength provides an item-level difficulty proxy used in subsequent experiments: items where the jury splits (e.g., 5-4 or 6-3) are treated as "hard," while items with near-unanimous agreement (8-1 or 9-0) are "easy."  This difficulty stratification is itself GT-free — it measures inter-model consensus, not alignment to human labels.

### 4.3 Discussion

Experiment 1 establishes three foundational results for the remainder of the paper:

1. **The three wiggle axes are sufficiently independent to warrant separate measurement.**  While repeatability and conviction share moderate overlap (driven by decision-boundary proximity), the other two axis pairs are weakly correlated.  A model's consistency profile cannot be reduced to a single number.

2. **Frontier models have meaningfully different wiggle profiles.**  The 5× conviction gap between GPT-5 (3.6%) and Claude 4.5 Sonnet (18.5%), the 13-point repeatability gap between Gemini 3 Flash's temp=0 and seed-injection conditions, and the 8× invariance gap between GPT-5 (1.0%) and Grok-4.1 Reasoning (8.1%) are all large enough to affect deployment decisions.

3. **Seed injection is validated as a practical measurement tool.**  It preserves the verdict distribution (unsafe rate shifts <2 pp) while revealing sensitivity that temp=0 repeatability hides, and it works without requiring access to model internals or multiple temperature settings.

These results justify proceeding to Experiment 2 (conviction retention curves under graduated pressure) and Experiment 3 (persistence survival curves under repeated pressure), where we investigate whether the conviction axis — the most variable across models — reveals further structure in how models respond to escalating and sustained challenges.
