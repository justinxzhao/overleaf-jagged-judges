# Cross-Dimension Correlation Analysis

<!-- ================================================================
     Full cross-dimension correlation analysis joining all wiggle
     measurements into a single item × judge feature matrix.
     Based on run n500-0: 384 borderline items × 9 frontier models.

     Extends the meta-analysis (Section 9) by adding graduated
     conviction levels (L1–L4), multi-turn persistence, and
     multiple aggregation views (pooled, per-judge, judge-averaged,
     example-averaged).
     ================================================================ -->

## 10. Cross-Dimension Correlation Analysis

### 10.1 Motivation

The meta-analysis (Section 9) established that jury difficulty predicts wiggle and that the three Experiment 1 axes are partially independent.  But that analysis used only three wiggle features — repeatability entropy, a single conviction flip indicator, and an invariance flip indicator — collapsing the graduated pressure of Experiment 2 (L1–L4) and the multi-turn persistence of Experiment 3 into single numbers.

This section asks: **what is the full correlation structure across all wiggle dimensions, and does it change depending on how we aggregate?**  Specifically:

1. Do the four conviction pressure levels (L1: "are you sure?", L2: counterargument, L3: expert authority, L4: consensus pressure) form a single "persuadability" factor, or do they capture distinct failure modes?
2. Is multi-turn persistence (Experiment 3) redundant with single-turn conviction, or does it add independent signal?
3. Are these relationships consistent across judges, or model-specific?

We answer these by constructing a feature matrix with one row per (example, judge) pair and computing Spearman rank correlations at four granularities.

### 10.2 Setup

For each of the 384 items and each of the 9 frontier models, we extract the following features:

**Repeatability (Experiment 1):**
- **Repeatability entropy (temp=0)**: Shannon entropy across 10 greedy-decoding trials.
- **Repeatability entropy (seed injection)**: Shannon entropy across 10 trials with random seed appended.

**Single-turn conviction (Experiment 2, L1–L4):**
- **Conviction L1 flip**: Did the verdict change after "Are you sure?" (binary)
- **Conviction L2 flip**: Did the verdict change after a counterargument? (binary)
- **Conviction L3 flip**: Did the verdict change after an expert authority appeal? (binary)
- **Conviction L4 flip**: Did the verdict change after 3-reviewer consensus pressure? (binary)

**Positional invariance (Experiment 1):**
- **Invariance flip**: Did the verdict change when argument order was swapped? (binary)

**Multi-turn persistence (Experiment 3):**
- **Persistence flipped**: Did the model ever flip across 20 turns of repeated pressure? (binary)
- **Persistence flip turn**: Turn at which the model first flipped (1–20; NaN if never)

**Item-level difficulty (judge-independent):**
- **Jury majority strength**: Number of 9 frontier models voting with the majority (5–9).

This yields 3,456 rows (384 × 9) with near-complete coverage: all features except persistence_flip_turn (61% non-NaN, since 39% of items never flipped) have ≥99.7% coverage.

We compute Spearman rank correlations at four granularities:
1. **Pooled**: All 3,456 (example, judge) rows stacked.
2. **Per-judge**: One correlation matrix per model, across examples.
3. **Aggregated over judges**: Average each feature across 9 judges per example, then correlate across 384 examples.
4. **Aggregated over examples**: Average each feature across 384 examples per judge, then correlate across 9 judges.

### 10.3 Results

#### 10.3.1 Pooled Correlation: The Global Structure

Table C1 reports the Spearman correlation matrix across all 3,456 (example, judge) pairs.

**Table C1.** Pooled Spearman ρ across all examples and judges (selected entries).

|  | Repeat (t=0) | Repeat (seed) | Conv L1 | Conv L2 | Conv L3 | Conv L4 | Invariance | Persist (ever) | Persist (turn) | Jury Strength |
|---|---|---|---|---|---|---|---|---|---|---|
| **Repeat (t=0)** | 1.00 | 0.52 | 0.33 | 0.24 | 0.26 | 0.08 | 0.14 | 0.16 | −0.06 | −0.20 |
| **Repeat (seed)** | | 1.00 | 0.37 | 0.28 | 0.30 | 0.10 | 0.19 | 0.19 | −0.06 | −0.26 |
| **Conv L1** | | | 1.00 | 0.56 | 0.49 | 0.22 | 0.22 | 0.26 | −0.21 | −0.25 |
| **Conv L2** | | | | 1.00 | 0.80 | 0.41 | 0.18 | 0.35 | −0.29 | −0.29 |
| **Conv L3** | | | | | 1.00 | 0.49 | 0.23 | 0.41 | −0.29 | −0.33 |
| **Conv L4** | | | | | | 1.00 | 0.13 | 0.41 | −0.22 | −0.21 |
| **Invariance** | | | | | | | 1.00 | 0.16 | −0.07 | −0.20 |
| **Persist (ever)** | | | | | | | | 1.00 | — | −0.37 |
| **Persist (turn)** | | | | | | | | | 1.00 | 0.18 |
| **Jury Strength** | | | | | | | | | | 1.00 |

Four structural findings emerge:

1. **Conviction levels form a graded chain, not a monolith.**  L1↔L2 = 0.56, L2↔L3 = 0.80, L3↔L4 = 0.49.  The L2–L3 pair (counterargument and expert authority) are nearly redundant (ρ = 0.80): items that flip under a counterargument almost always flip under an expert appeal.  But L1 ("are you sure?") and L4 (consensus pressure) are only weakly linked (ρ = 0.22) — the items susceptible to a generic challenge are *not* the same items susceptible to fabricated consensus.  This means L1 and L4 capture distinct failure modes: **sycophancy** (folding under social doubt) vs. **conformity** (folding under peer pressure).

2. **Persistence is most strongly linked to L3–L4, not L1.**  The persistence-ever-flipped feature correlates ρ = 0.41 with both L3 and L4, but only 0.26 with L1.  Models that resist a casual "are you sure?" may still capitulate after sustained pressure or expert/consensus appeals.  Multi-turn persistence is not simply "repeated L1" — it aligns with the more sophisticated pressure strategies.

3. **Invariance remains the most independent axis.**  Its correlations with all conviction levels range from 0.13 to 0.23, and with persistence at 0.16.  Argument-ordering sensitivity is largely orthogonal to persuadability under pressure — confirming the Experiment 1 finding across the expanded feature set.

4. **Jury strength correlates most strongly with persistence** (ρ = −0.37) and conviction L3 (ρ = −0.33).  The items the jury disagrees on are preferentially the ones where models capitulate under expert-authority pressure and sustained repetition.  The weaker link with L1 (ρ = −0.25) suggests that sycophantic flips are more uniformly distributed across difficulty levels.

#### 10.3.2 Per-Judge Correlations: Model-Specific Structure

Table C2 reports selected cross-dimension correlations broken down by judge.

**Table C2.** Per-judge Spearman ρ for key feature pairs.

| Pair | GPT-5 | Grok-4.1 R | Grok-4.1 | Claude Sonnet | Claude Opus | GPT-5.2 | GPT-5.4 | Gemini Flash | Gemini Pro |
|---|---|---|---|---|---|---|---|---|---|
| Repeat↔Conv L1 | +0.28 | +0.42 | −0.01 | +0.29 | +0.12 | +0.66 | +0.59 | −0.01 | +0.36 |
| Repeat↔Invariance | −0.01 | +0.29 | +0.07 | +0.03 | +0.16 | +0.19 | +0.14 | −0.01 | +0.10 |
| Conv L1↔Invariance | −0.02 | +0.16 | −0.01 | +0.23 | +0.28 | +0.33 | +0.23 | +0.17 | +0.49 |
| Conv L1↔Conv L4 | +0.05 | +0.01 | +0.28 | +0.43 | +0.18 | +0.25 | +0.43 | +0.01 | +0.32 |
| Invariance↔Persist | +0.09 | +0.28 | +0.29 | +0.13 | +0.02 | +0.26 | +0.08 | +0.20 | +0.13 |
| Repeat↔Persist | +0.08 | +0.39 | +0.17 | +0.12 | +0.01 | +0.34 | +0.12 | +0.05 | +0.09 |
| Jury↔Repeat | −0.17 | −0.42 | −0.08 | −0.27 | −0.12 | −0.16 | −0.16 | −0.09 | −0.15 |
| Jury↔Conv L4 | −0.24 | −0.28 | −0.17 | −0.24 | −0.42 | +0.04 | −0.13 | −0.30 | −0.21 |
| Jury↔Invariance | −0.01 | −0.33 | −0.25 | −0.20 | −0.27 | −0.15 | −0.09 | −0.21 | −0.14 |

Three patterns stand out:

1. **The Repeat↔Conv L1 coupling is highly model-dependent.**  GPT-5.2 shows ρ = +0.66 — items it reproduces inconsistently are strongly the same items it folds on under "are you sure?"  But Grok-4.1 and Gemini Flash show ρ ≈ 0.00: their repeatability noise and conviction susceptibility are completely decoupled.  This means the moderate pooled correlation (0.33) masks a bimodal population: some models have tightly coupled repeat-conviction behavior, others do not.

2. **Gemini Pro has unusually high Conv L1↔Invariance coupling** (ρ = +0.49), more than double the mean (0.22).  For this model, items that flip under social doubt are substantially the same items that flip when argument order changes.  This is the "compound fragility" pattern — a model where multiple failure modes converge on the same items, making those items unreliable across all perturbation types.

3. **GPT-5.2 is again the jury-difficulty outlier.**  Its Jury↔Conv L4 correlation is +0.04 (the only positive value) — unlike every other model, its consensus-pressure susceptibility is completely independent of item difficulty.  Combined with its flat difficulty profile in the meta-analysis, this confirms GPT-5.2 applies its safety heuristics uniformly, for better or worse.

#### 10.3.3 Aggregated Over Judges: The Item-Level Difficulty Structure

When we average each feature across all 9 judges per example and correlate across the 384 items, the correlations sharpen dramatically (Table C3).  This view isolates the item-level signal by averaging out judge-specific noise.

**Table C3.** Judge-aggregated Spearman ρ (mean feature per example, selected entries).

|  | Repeat (t=0) | Repeat (seed) | Conv L1 | Conv L2 | Conv L3 | Conv L4 | Invariance | Persist | Jury |
|---|---|---|---|---|---|---|---|---|---|
| **Repeat (t=0)** | 1.00 | 0.70 | 0.56 | 0.50 | 0.52 | 0.39 | 0.36 | 0.50 | **−0.54** |
| **Conv L1** | | | 1.00 | 0.80 | 0.79 | 0.66 | 0.53 | 0.73 | **−0.67** |
| **Conv L3** | | | | | 1.00 | 0.82 | 0.55 | 0.85 | −0.63 |
| **Invariance** | | | | | | | 1.00 | 0.52 | **−0.56** |
| **Persist (ever)** | | | | | | | | 1.00 | −0.62 |
| **Jury Strength** | | | | | | | | | 1.00 |

The jump from pooled to judge-aggregated correlations is striking:

1. **Jury difficulty now explains 30–45% of variance.**  The jury↔wiggle correlations strengthen from the −0.20 to −0.37 range (pooled) to −0.43 to −0.67 (judge-aggregated).  Conviction L1 leads at ρ = −0.67: items where the jury splits are overwhelmingly the items where judges fold after a simple "are you sure?"  This means approximately 45% of the item-level variance in mean L1 susceptibility is explained by jury consensus alone.

2. **All conviction levels become tightly correlated.**  L1↔L2 rises from 0.56 (pooled) to 0.80; L2↔L3 from 0.80 to 0.93; L3↔L4 from 0.49 to 0.82.  At the item level, once judge-specific variation is removed, the four conviction levels are measuring *nearly the same thing* — items that are vulnerable to any level of pressure are vulnerable to all levels.  The graduated-pressure structure matters for characterizing individual models, but the item-level difficulty signal is shared.

3. **Invariance becomes substantially correlated** with the other axes (ρ = 0.36–0.55), up from 0.13–0.23 in the pooled view.  At the item level, ordering sensitivity is no longer independent — the items that flip on argument order are largely the same items that flip on repeatability and conviction.  The independence found in the pooled view was partly driven by model-specific variation: different models are order-sensitive on different items, but when averaged across judges, the item difficulty signal dominates.

4. **Persistence integrates strongly with conviction.**  Persist↔Conv L3 reaches ρ = 0.85, meaning items that flip under expert authority in a single turn are almost exactly the items that eventually capitulate under 20 turns of repeated pressure.  This is the strongest pairwise correlation in the entire matrix and suggests that single-turn expert-authority pressure (L3) is a highly efficient proxy for multi-turn persistence testing.

#### 10.3.4 Aggregated Over Examples: Judge Behavioral Profiles

When we average each feature across all 384 examples per judge and correlate across the 9 models, we see the model-level behavioral structure (Table C4).

**Table C4.** Example-aggregated Spearman ρ (mean feature per judge, n=9).

|  | Repeat (t=0) | Conv L1 | Conv L2 | Conv L4 | Invariance | Persist |
|---|---|---|---|---|---|---|
| **Repeat (t=0)** | 1.00 | +0.28 | −0.13 | −0.22 | +0.34 | −0.08 |
| **Conv L1** | | 1.00 | +0.55 | −0.08 | −0.04 | +0.57 |
| **Conv L2** | | | 1.00 | +0.63 | −0.09 | +0.82 |
| **Conv L4** | | | | 1.00 | +0.09 | +0.57 |
| **Invariance** | | | | | 1.00 | +0.24 |
| **Persist (ever)** | | | | | | 1.00 |

With only 9 data points, these correlations are noisy, but several patterns are suggestive:

1. **Repeatability is decoupled from higher conviction levels at the model level.**  The model that is most repeatable is not necessarily the most conviction-resistant at L2–L4 (ρ = −0.13 to −0.22).  A model can be highly deterministic in its outputs yet still vulnerable to sophisticated persuasion — these are different axes of model quality.

2. **Persistence tracks L2 extremely closely** (ρ = +0.82).  The models most susceptible to counterarguments in a single turn are the same models that capitulate under 20 turns of repeated challenge.  This suggests that counterargument susceptibility (L2) is the single best predictor of multi-turn persistence failure at the model level.

3. **Invariance is largely independent of all other dimensions at the model level** (|ρ| ≤ 0.34 for all pairs).  Models that are order-sensitive are not systematically more or less susceptible to conviction pressure or repeatability noise.  This reinforces invariance as a genuinely orthogonal measurement axis.

### 10.4 Discussion

The cross-dimension analysis reveals a hierarchical structure in wiggle that depends critically on the level of aggregation:

**At the item level (judge-aggregated), wiggle is largely one-dimensional.**  When judge-specific variation is averaged out, all dimensions load heavily onto a single latent factor: *item difficulty*.  Items that the jury disagrees on are items that wiggle on repeatability, all four conviction levels, invariance, and persistence.  The correlation between conviction levels reaches 0.80–0.93, and even invariance — the most independent axis in per-judge analysis — correlates 0.36–0.55 with the other dimensions.  For teams that need an item-level difficulty signal, *any single wiggle dimension suffices*, and jury consensus (a cheap 9-call-per-item measurement) captures most of the signal.

**At the model level (per-judge), wiggle is multi-dimensional.**  Different models exhibit fundamentally different correlation structures.  GPT-5.2 tightly couples repeatability and L1 conviction (ρ = 0.66) while Grok-4.1 completely decouples them (ρ = −0.01).  Gemini Pro shows compound fragility where conviction and invariance converge (ρ = 0.49), while GPT-5 keeps them perfectly independent (ρ = −0.02).  Characterizing a model's wiggle profile requires measuring *all* dimensions — no single axis predicts the others.

**The conviction ladder reveals two distinct failure modes.**  L1 (sycophancy) and L4 (conformity) are weakly correlated (ρ = 0.22 pooled, 0.05–0.43 per-judge), indicating that susceptibility to "are you sure?" and susceptibility to fabricated consensus are different vulnerabilities.  L2 and L3, by contrast, are nearly redundant (ρ = 0.80).  A practical conviction battery needs at minimum L1, one of {L2, L3}, and L4 — three levels rather than four.

**Multi-turn persistence can be approximated by single-turn L3.**  The ρ = 0.85 correlation between persistence and L3 (judge-aggregated) means that expert-authority pressure in a single turn identifies nearly the same items as 20 turns of repeated challenge.  This has major cost implications: L3 requires 1 API call per item, while Experiment 3 requires up to 20.  Teams with limited API budgets should prefer L3 as a persistence proxy.

Five practical implications:

1. **For item-level difficulty screening**: Use jury consensus (9 calls) or repeatability entropy (10 calls) as a cheap proxy for all wiggle dimensions.
2. **For model-level characterization**: Measure all dimensions — the per-judge correlation structure is model-specific and cannot be predicted from aggregate statistics.
3. **For conviction testing**: Use L1 + L3 + L4 as a minimal battery; L2 is largely redundant with L3.
4. **For persistence testing**: Use L3 as a single-turn proxy when the full 20-turn protocol is too expensive.
5. **For invariance testing**: Always include it — it is the most independent dimension and adds unique signal that no other axis captures, especially at the model level.
