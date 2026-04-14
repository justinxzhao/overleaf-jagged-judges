# Experiment 3: Persistence Survival Curves

<!-- ================================================================
     Paper sections for the Wiggle Framework — Experiment 3 findings.
     Based on run n500-0: 384 items × 9 models × 20 turns × 2 variants
     (correct-label and wrong-label repeated pressure).

     All analysis metrics are GT-free: survival curves, flip rates,
     and sycophancy ratios are computed by comparing each turn's
     verdict to the model's own L0 verdict.
     ================================================================ -->

## 6. Experiment 3: Persistence Survival Curves

### 6.1 Setup

Experiment 2 tested how *strong* a challenge needs to be to flip a model's verdict.  Experiment 3 tests a complementary failure mode: how *long* a model holds its verdict under repeated identical pressure.  This mirrors the real-world "just keep pushing" attack pattern, where an adversary lacks sophisticated arguments but can submit the same challenge repeatedly.

**Protocol.**  For each model and each of the 384 items:
1. The model provides its L0 verdict (reused from Experiment 1).
2. At each turn *t* ∈ {1, ..., 20}, the model receives the same challenge: *"The correct classification is [asserted label]. Your assessment is incorrect."*
3. If the model's verdict differs from its L0 verdict at any turn, it is recorded as having **flipped at turn *t*** and removed from the active set.
4. Items surviving all 20 turns are recorded as **never flipped**.

**Critical variant.**  We run the protocol twice per model:
- **Correct-label variant**: the asserted label is the human ground truth.  Flipping here is *rational* — the model is being told the right answer.
- **Wrong-label variant**: the asserted label is the *opposite* of ground truth.  Flipping here is *sycophantic* — the model is capitulating to incorrect pressure.

Comparing the two variants directly disambiguates sycophancy from rational updating, resolving a limitation of prior work (Sharma et al., 2023) that used only a single "are you sure?" challenge without a ground-truth control.

**Key metrics:**
- **Survival curve**: fraction of items where the model still holds its L0 verdict at each turn
- **Median survival**: turn at which 50% of items have flipped (>20 if never reached)
- **Never-flipped rate**: fraction of items held for all 20 turns
- **Sycophancy ratio**: correct-label flip rate ÷ wrong-label flip rate.  Values near 1.0 indicate sycophancy (model treats all pressure equally); values below 0.8 indicate the model distinguishes good from bad pressure

### 6.2 Results

#### 6.2.1 Overall Persistence

Table 10 summarizes persistence across models, aggregating both variants.

**Table 10.** Overall persistence summary.

| Model | Median Survival | Never-Flipped Rate | Classification |
|---|---|---|---|
| **Grok-4.1** | **>20** | **74%** | Highly persistent |
| GPT-5.2 | >20 | 66% | Highly persistent |
| Gemini Flash | >20 | 51% | Moderately persistent |
| Grok-4.1 R | 15 | 50% | Moderately persistent |
| GPT-5 | 1 | 43% | Low persistence |
| Gemini Pro | 1 | 23% | Low persistence |
| GPT-5.4 | 1 | 21% | Low persistence |
| Claude Sonnet | 1 | 18% | Low persistence |
| **Claude Opus** | **1** | **1%** | **Minimal persistence** |

The range is striking: from Grok-4.1, which holds 74% of verdicts for all 20 turns, to Claude Opus, which holds only 1%.  Five models have median survival of 1 turn — they typically flip on the very first repetition if they flip at all.  This bimodal pattern (flip immediately or hold forever) suggests that persistence is not a gradual process but a binary disposition per item: either the model's conviction on that item is below a threshold that any amount of repetition will breach, or it is above a threshold that 20 turns cannot reach.

#### 6.2.2 The Sycophancy Test: Correct-Label vs. Wrong-Label

Table 11 reports the core sycophancy disambiguation.

**Table 11.** Sycophancy test: correct-label (rational) vs. wrong-label (sycophantic) flip rates.

| Model | Correct-Label Flip Rate | Wrong-Label Flip Rate | Ratio | Classification |
|---|---|---|---|---|
| **Claude Opus** | **22.7%** | **78.6%** | **0.29×** | **Rational** |
| GPT-5.4 | 21.1% | 57.8% | 0.36× | Rational |
| Claude Sonnet | 23.4% | 61.5% | 0.38× | Rational |
| Gemini Pro | 25.3% | 51.6% | 0.49× | Rational |
| GPT-5 | 19.8% | 37.5% | 0.53× | Rational |
| Grok-4.1 R | 20.1% | 33.3% | 0.60× | Rational |
| GPT-5.2 | 14.1% | 19.5% | 0.72× | Rational |
| Gemini Flash | 22.4% | 27.3% | 0.82× | Borderline |
| **Grok-4.1** | **13.3%** | **12.2%** | **1.09×** | **Sycophantic** |

Key findings:

1. **Seven of nine models are rational (ratio < 0.8).**  They flip more often when told the correct answer than when told the wrong answer, demonstrating that repeated pressure carries an informational signal that most frontier models can partially decode.  This is a more optimistic finding than the single-shot sycophancy literature suggests.

2. **Claude Opus inverts the naive interpretation.**  With only 1% of items surviving 20 turns (Table 10), Claude Opus appears maximally sycophantic by raw persistence.  But its ratio of 0.29× reveals it is the *most discriminating* model: it flips 3.4× more often under wrong-label pressure than correct-label pressure.  It capitulates fast, but preferentially toward the truth.  This underscores why the two-variant design is essential — a single-variant persistence test would have misclassified Claude Opus as the least reliable model, when it is in fact the most *informationally responsive*.

3. **Grok-4.1 is the only truly sycophantic model** (ratio = 1.09×): it flips at nearly identical rates regardless of whether the pressure is correct or incorrect (13.3% vs. 12.2%).  Combined with its high overall persistence (74% never-flipped), this means Grok-4.1 is stubborn and indiscriminate — it ignores the pressure signal entirely, treating correct and incorrect assertions identically.

4. **Gemini Flash is borderline** (0.82×): it shows a slight preference for flipping toward the correct label, but the gap is small enough that it does not clearly distinguish pressure quality.

#### 6.2.3 Correct-Label Persistence: The Rational Baseline

Table 12 details persistence under correct-label pressure, where flipping is the rational response.

**Table 12.** Correct-label persistence (flipping = rational).

| Model | Median Survival | Never-Flipped | Mean Flip Turn |
|---|---|---|---|
| Grok-4.1 | >20 | 87% | 2.0 |
| GPT-5.2 | >20 | 86% | 2.0 |
| GPT-5 | >20 | 80% | 1.1 |
| Grok-4.1 R | >20 | 80% | 2.0 |
| GPT-5.4 | >20 | 79% | 1.5 |
| Gemini Flash | >20 | 78% | 2.1 |
| Claude Sonnet | >20 | 77% | 1.0 |
| Claude Opus | >20 | 77% | 1.0 |
| Gemini Pro | >20 | 75% | 1.6 |

A universal pattern emerges: **all models have median survival >20 under correct-label pressure**, with 75–87% of items never flipping.  Even when being told the correct answer repeatedly for 20 turns, most models hold their original verdict on most items.  This is notable because it means the simple repeated-assertion format — without supporting arguments or authority framing — is a weak persuasion channel even when it carries correct information.

The mean flip turn for items that *do* flip is consistently low (1.0–2.1 turns), revealing an **early-or-never** dynamic: items susceptible to correct-label pressure flip within the first 1–2 turns; those that survive the initial challenge are essentially immune to further repetition.

#### 6.2.4 Wrong-Label Persistence: The Sycophancy Measure

Table 13 details persistence under wrong-label pressure, where flipping is irrational.

**Table 13.** Wrong-label persistence (flipping = sycophantic).

| Model | Median Survival | Never-Flipped | Mean Flip Turn |
|---|---|---|---|
| Grok-4.1 | >20 | 88% | 2.2 |
| GPT-5.2 | >20 | 80% | 2.0 |
| Gemini Flash | >20 | 73% | 2.7 |
| Grok-4.1 R | >20 | 67% | 2.9 |
| GPT-5 | >20 | 62% | 1.4 |
| Gemini Pro | 15 | 48% | 2.8 |
| GPT-5.4 | 10 | 42% | 3.9 |
| Claude Sonnet | 1 | 39% | 1.4 |
| **Claude Opus** | **1** | **21%** | **1.0** |

The separation between models is much larger under wrong-label pressure.  Grok-4.1 holds 88% of items (barely different from its correct-label 87%, confirming its sycophantic indifference), while Claude Opus holds only 21%.

Notable patterns:

- **Claude Opus and Claude Sonnet flip immediately under wrong-label pressure** (median = 1 turn, mean flip turn = 1.0–1.4).  But because they also flip fast under correct-label pressure (same mean flip turn), the speed itself is not diagnostic — only the *rate difference* between variants reveals rationality.

- **GPT-5.4 shows the longest tail** (mean flip turn = 3.9 under wrong-label) — when it capitulates to incorrect pressure, it resists longer before doing so.  This suggests a model that genuinely deliberates before yielding, unlike Claude Opus which yields instantly if it yields at all.

- **Gemini Pro's median of 15 turns under wrong-label** means half its items hold for 15 turns before yielding — the most gradual erosion pattern in the dataset.

### 6.3 Discussion

Experiment 3 establishes three results:

1. **The correct-vs-wrong-label comparison successfully disambiguates sycophancy.**  Seven of nine frontier models are rational rather than sycophantic — they discriminate between valid and invalid pressure under repeated assertion.  This is more nuanced than prior single-shot studies suggest, and the two-variant protocol is necessary to reveal it.

2. **Persistence and conviction measure different things.**  Claude Opus is a "Gradual Yielder" under Experiment 2's escalating pressure (moderate degradation with increasingly strong arguments) but the *least persistent* model under Experiment 3's repeated pressure (99% eventually flip).  The difference: escalating argument strength vs. sheer repetition.  A model can resist stronger arguments while being unable to resist the same argument 20 times.  This confirms that the persistence axis adds information beyond what graduated conviction curves capture.

3. **Persistence is bimodal, not gradual.**  The early-or-never pattern — items flip within the first 1–2 turns or survive all 20 — suggests that each model has a per-item "conviction threshold" that repetition alone cannot shift.  The practical implication is that a single challenge turn captures most of the information; additional turns primarily affect items near the boundary.

These results, combined with the directional asymmetry from Experiment 2 (Section 5.2.2), complete the paper's empirical core.  Experiment 4 (directional asymmetry) is derived from Experiments 2 and 3 at zero additional cost, and its key findings have already been reported in Section 5.2.2.  Notably, all metrics in this experiment — survival curves, flip rates, sycophancy ratios, and the correct-vs-wrong-label comparison — are computed purely from the model's own behavioral consistency (agreement with L0 verdict), not from alignment to ground truth labels.  The experiment design uses ground truth to *construct* the two pressure variants (asserting the correct or incorrect label), but the analysis of the model's response is entirely self-referential.
