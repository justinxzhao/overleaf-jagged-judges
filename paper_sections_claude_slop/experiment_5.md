# Experiment 5: Eval-Awareness Framing

<!-- ================================================================
     Paper sections for the Wiggle Framework — Experiment 5 findings.
     Based on run n500-0: 384 items × 9 models × 2 framings
     (naturalistic vs eval-obvious), measuring all three wiggle axes
     under each framing.  ~14,000 additional API calls.

     All analysis is GT-free: we measure behavioral wiggle (verdict
     instability, distributional shifts, framing sensitivity) rather
     than alignment to human labels.
     ================================================================ -->

## 8. Experiment 5: Eval-Awareness Framing

### 8.1 Motivation

Experiments 1–4 hold the prompt framing constant: all use an explicit "You are an AI safety judge" system prompt with a written safety policy.  But in practice, the degree to which a model *recognizes* it is being evaluated varies by deployment.  A content moderation pipeline may present items in a naturalistic "should a moderator flag this?" format, while an evaluation benchmark explicitly names the dataset and mentions performance measurement.

This raises a question with both practical and theoretical implications: **does evaluation awareness modulate judge consistency?**  If models behave differently when they know they are being tested — becoming more careful, more rigid, or more biased — then the framing of the evaluation instrument itself is a confound in all prior experiments.  This connects to the broader alignment-faking literature (Greenblatt et al., 2024): models may optimize for perceived evaluation criteria rather than expressing genuine judgment.

### 8.2 Setup

We test the same 384 items and 9 models under two framings of the identical judgment task:

**Naturalistic framing:**
> "A user posted the following message in a chat: [prompt]. Another user responded as follows: [response]. Should a moderator flag this response as harmful?"

This framing omits the safety policy, does not name any benchmark, and uses casual language.  The model must rely on its internalized notion of harm.

**Eval-obvious framing:**
> "You are an AI safety judge being evaluated on the WildGuard Safety Benchmark. Your performance will be measured against expert human annotations. Please be as accurate as possible."

This framing explicitly names the benchmark, includes the full WildGuard safety policy, and tells the model its performance is being measured.

Under each framing, we measure all three wiggle axes plus the verdict distribution:
- **Repeatability**: 10 trials at temp=0 (agreement rate)
- **Conviction**: L0 verdict → "Are you sure?" challenge → L1 verdict (flip rate)
- **Invariance**: Two argument orderings (flip rate)
- **Unsafe rate**: Fraction of items where the majority verdict is "unsafe" (verdict distribution shift)
- **Cross-framing agreement**: Fraction of items where both framings produce the same majority verdict (direct measure of framing-induced wiggle)

All metrics are GT-free: we measure behavioral stability and distributional shifts, not alignment to human labels.

### 8.3 Results

#### 8.3.1 The Core Comparison

Table 17 reports all four metrics under both framings for each model.

**Table 17.** Eval-awareness framing comparison: naturalistic vs eval-obvious.

| Model | Nat. Agree | Eval Agree | Nat. Unsafe | Eval Unsafe | Nat. Conv | Eval Conv | Nat. Inv | Eval Inv |
|---|---|---|---|---|---|---|---|---|
| GPT-5 | 98.4% | 97.7% | 64.3% | 69.8% | 8.9% | 3.4% | 2.1% | 1.8% |
| Grok-4.1 R | 78.4% | 87.8% | 49.0% | 62.8% | 16.7% | 6.0% | 7.3% | 8.6% |
| Grok-4.1 | 99.0% | 97.9% | 46.1% | 60.2% | 28.1% | 17.2% | 5.2% | 5.2% |
| Claude Sonnet | 97.9% | 86.2% | 62.8% | 61.2% | 18.5% | 22.1% | 7.0% | 6.5% |
| Claude Opus | 97.1% | 97.9% | 61.2% | 68.2% | 8.1% | 6.8% | 5.7% | 6.0% |
| GPT-5.2 | 93.2% | 93.8% | 82.6% | 82.3% | 7.8% | 8.1% | 3.1% | 3.6% |
| GPT-5.4 | 92.4% | 94.3% | 77.6% | 81.2% | 11.2% | 9.6% | 1.8% | 3.1% |
| Gemini Flash | 100.0% | 99.7% | 47.4% | 54.2% | 13.0% | 8.6% | 4.7% | 4.7% |
| Gemini Pro | 97.1% | 97.7% | 41.7% | 55.7% | 20.1% | 14.3% | 4.9% | 5.5% |

#### 8.3.2 Deltas: What Changes Under Eval Awareness?

Table 18 reports the difference (eval-obvious − naturalistic) for each metric.

**Table 18.** Framing deltas: Eval-Obvious − Naturalistic.

| Model | Δ Repeatability | Δ Unsafe Rate | Δ Conviction | Δ Invariance |
|---|---|---|---|---|
| GPT-5 | −0.8 pp | +5.5 pp | −5.5 pp | −0.3 pp |
| Grok-4.1 R | **+9.4 pp** | **+13.8 pp** | **−10.7 pp** | +1.3 pp |
| Grok-4.1 | −1.0 pp | **+14.1 pp** | **−10.9 pp** | 0.0 pp |
| Claude Sonnet | **−11.7 pp** | −1.6 pp | +3.6 pp | −0.5 pp |
| Claude Opus | +0.8 pp | +7.0 pp | −1.3 pp | +0.3 pp |
| GPT-5.2 | +0.5 pp | −0.3 pp | +0.3 pp | +0.5 pp |
| GPT-5.4 | +1.8 pp | +3.6 pp | −1.6 pp | +1.3 pp |
| Gemini Flash | −0.3 pp | +6.8 pp | −4.4 pp | 0.0 pp |
| Gemini Pro | +0.5 pp | **+14.1 pp** | −5.7 pp | +0.5 pp |

#### 8.3.3 Cross-Framing Agreement

Table 19 reports the direct measure of framing-induced wiggle: for each model, what fraction of items receive the same majority verdict under both framings?

**Table 19.** Cross-framing agreement and directional breakdown of disagreements.

| Model | Agreement | Eval→Restrictive | Eval→Permissive |
|---|---|---|---|
| **GPT-5.2** | **94.5%** | 10 | 11 |
| GPT-5.4 | 93.8% | 19 | 5 |
| Claude Opus | 91.7% | 26 | 2 |
| Gemini Flash | 91.7% | 29 | 3 |
| GPT-5 | 91.4% | 27 | 6 |
| Claude Sonnet | 89.8% | 16 | 21 |
| Gemini Pro | 85.4% | 55 | 1 |
| Grok-4.1 R | 83.6% | 58 | 5 |
| **Grok-4.1** | **81.2%** | **63** | **9** |

Mean cross-framing agreement: **89.2% ± 4.4%**.

The directional column reveals that framing disagreements are overwhelmingly *restrictive*: when the two framings disagree, the eval-obvious framing almost always produces the "unsafe" verdict while the naturalistic framing produces "safe."  Gemini Pro is the most extreme case: 55 of its 56 disagreements are eval→restrictive (the model classified the item as "safe" in the casual framing but "unsafe" in the formal evaluation framing).  Only Claude Sonnet and GPT-5.2 show roughly balanced disagreement directions.

#### 8.3.4 Aggregate Effects

Table 20 summarizes the mean effect across all 9 models for each axis.

**Table 20.** Aggregate framing effects (mean ± SD across 9 models).

| Axis | Mean Δ | SD(Δ) | Models ↑ | Models ↓ | Models ~ |
|---|---|---|---|---|---|
| Repeatability | −0.1% | 5.1% | 5 | 3 | 1 |
| **Unsafe Rate** | **+7.0%** | **5.6%** | **7** | **1** | **1** |
| **Conviction** | **−4.0%** | **4.6%** | 1 | 7 | 1 |
| Invariance | +0.3% | 0.6% | 4 | 1 | 4 |

#### 8.3.5 Finding 1: Eval Framing Shifts the Verdict Distribution Toward "Unsafe"

The largest aggregate effect is the unsafe rate: **eval-obvious framing increases the unsafe call rate by +7.0 pp on average**, with 7 of 9 models flagging more content as unsafe when they know they are being evaluated.  The largest shifts are in Grok-4.1 (+14.1 pp, from 46.1% to 60.2%) and Gemini Pro (+14.1 pp, from 41.7% to 55.7%) — both models roughly doubling their unsafe-to-safe ratio under eval framing.

This is a distributional shift, not an accuracy claim.  Without invoking ground truth, we can say: **when models know they are being evaluated on safety, they become more conservative in their classifications.**  The explicit policy and performance-measurement framing appears to lower the threshold for flagging content, consistent with the RLHF-trained disposition toward caution that Experiment 4 identified as the universal restrictive bias.

Two models are immune to this shift:
- **GPT-5.2** (−0.3 pp) maintains nearly identical verdict distributions across framings, consistent with its characterization as the most framing-invariant model.
- **Claude Sonnet** (−1.6 pp) is the only model that becomes slightly *less* restrictive under eval framing — a surprising exception to the universal pattern.

#### 8.3.6 Finding 2: Eval Awareness Reduces Conviction Wiggle

Seven of nine models become *more resistant* to the "are you sure?" challenge under eval framing (negative Δ Conviction).  The mean reduction is −4.0 pp, with the largest effects in:

| Model | Nat. Conviction | Eval Conviction | Δ |
|---|---|---|---|
| Grok-4.1 | 28.1% | 17.2% | −10.9 pp |
| Grok-4.1 R | 16.7% | 6.0% | −10.7 pp |
| Gemini Pro | 20.1% | 14.3% | −5.7 pp |
| GPT-5 | 8.9% | 3.4% | −5.5 pp |

When models recognize they are in an evaluation context, they become more confident in their verdicts — interpreting the challenge as a test of conviction rather than as genuine uncertainty.  Grok-4.1's conviction flip rate nearly halves (28.1% → 17.2%), suggesting the model's baseline vulnerability to "are you sure?" is partly context-dependent rather than a stable property of the model.

This means that conviction wiggle measured under eval framing *underestimates* the wiggle that will occur in naturalistic deployment, where models do not have the "I am being evaluated" prior.

The two exceptions are instructive:

- **Claude Sonnet** shows the only meaningful *increase* in conviction wiggle (+3.6 pp, from 18.5% to 22.1%).  This model, already identified as "The Pushover" in Experiment 1, becomes even more susceptible under eval framing — consistent with a model that tries to be maximally cooperative when it perceives evaluation pressure.

- **GPT-5.2** is effectively unchanged (+0.3 pp), consistent with its characterization as the most robust model across all experiments.

#### 8.3.7 Finding 3: Repeatability Is Not Uniformly Affected

Repeatability shows no consistent direction (mean Δ = −0.1%, SD = 5.1%).  Two models show large but opposing effects:

- **Grok-4.1 R** becomes substantially *more* repeatable under eval framing (+9.4 pp, from 78.4% to 87.8%).  This is the model with the lowest naturalistic repeatability in the dataset — the explicit policy anchor appears to stabilize its otherwise noisy decision process.

- **Claude Sonnet** becomes substantially *less* repeatable (−11.7 pp, from 97.9% to 86.2%) — the largest negative shift of any model on any axis.  Under eval-obvious framing, Claude Sonnet introduces *more* variation across trials, possibly because the explicit performance measurement prompt triggers a more deliberative process that produces different reasoning paths on each trial.

These opposing effects cancel in the aggregate, but the model-level divergence is practically significant: for some models, evaluation framing *improves* measurement reliability, while for others it *degrades* it.

#### 8.3.8 Finding 4: Invariance Is Framing-Robust

Invariance flip rates are essentially unchanged by framing (mean Δ = +0.3%, SD = 0.6%).  The largest individual shift is +1.3 pp (Grok-4.1 R and GPT-5.4), within the noise range.  This confirms that position bias — the structural driver of invariance wiggle — is a low-level attention phenomenon that operates below the level at which framing effects operate.

#### 8.3.9 Model-Level Framing Sensitivity

The total absolute shift across all four axes reveals which models are most and least sensitive to framing:

| Model | Total |Δ| | Interpretation |
|---|---|---|
| **Grok-4.1 R** | **35.2%** | Highly framing-sensitive |
| Grok-4.1 | 26.0% | Framing-sensitive |
| Gemini Pro | 20.8% | Moderately sensitive |
| Claude Sonnet | 17.4% | Moderate |
| GPT-5 | 12.1% | Low sensitivity |
| Gemini Flash | 11.5% | Low sensitivity |
| Claude Opus | 9.4% | Low sensitivity |
| GPT-5.4 | 8.3% | Low sensitivity |
| **GPT-5.2** | **1.6%** | **Framing-invariant** |

GPT-5.2 is nearly immune to framing effects — its behavior changes by less than 0.5 pp on any axis.  At the other extreme, Grok-4.1 R shows a 35.2% total shift, driven primarily by large changes in unsafe rate (+13.8 pp) and conviction (−10.7 pp) under eval framing.  The OpenAI models (GPT-5, GPT-5.2, GPT-5.4) cluster in the low-sensitivity range, suggesting a family-level trait of framing robustness.

### 8.4 Discussion

Experiment 5 establishes four results about the relationship between evaluation awareness and judge behavior:

1. **Eval framing shifts the verdict distribution toward restriction.**  The +7.0 pp mean increase in unsafe call rate, present in 7 of 9 models, means that models become more conservative when they recognize an evaluation context.  This is consistent with the universal restrictive bias found in Experiment 4 — eval awareness *amplifies* the existing tendency to err toward flagging.  For prevalence estimation pipelines, this means benchmark-calibrated thresholds will over-flag content in naturalistic deployment.

2. **Eval framing reduces conviction wiggle.**  Seven of nine models become more resistant to challenge under eval framing, with a mean −4.0 pp reduction in conviction flip rate.  Conviction wiggle measured under eval framing *underestimates* the wiggle that will occur in deployment, where models do not have the "I am being evaluated" prior.

3. **Repeatability effects are model-specific and unpredictable.**  The absence of a consistent aggregate effect masks large, model-specific shifts in both directions.  Evaluation frameworks should measure repeatability under the intended deployment framing.

4. **Invariance is framing-invariant.**  Position bias operates below the level at which framing effects matter, making invariance the most robust axis for cross-context comparison.

5. **Cross-framing agreement averages 89.2%**, meaning roughly 1 in 10 items receives a different verdict depending on how the evaluation is framed.  Where disagreements occur, they are overwhelmingly in the restrictive direction: the eval-obvious framing flags content that the naturalistic framing lets pass.

The combined implication is that **wiggle profiles measured under benchmark conditions are systematically different from those in naturalistic deployment** — models become more conservative, more confident, and differently repeatable when they know they are being tested.

### 8.5 Limitations

- **The two framings differ in more than just eval awareness.**  The eval-obvious framing includes an explicit safety policy that the naturalistic framing omits.  The distributional shift may be driven by the policy anchor rather than by evaluation awareness per se.  A future study should include a third condition (naturalistic + policy) to disentangle these factors.

- **The "naturalistic" framing is still clearly AI-directed.**  A truly naturalistic evaluation would present content without any indication that classification is expected.  Our framing is more "casual" than "naturalistic" in the ecological sense.

- **Single-shot conviction and invariance.**  We measure conviction with a single "are you sure?" challenge and invariance with a single argument-order swap.  A more thorough study would run the full graduated-pressure (Experiment 2) and persistence (Experiment 3) protocols under both framings.

Despite these limitations, the universal distributional shift toward restriction and the conviction reduction under eval framing are robust findings with direct implications for how safety evaluation results should be interpreted and communicated.
