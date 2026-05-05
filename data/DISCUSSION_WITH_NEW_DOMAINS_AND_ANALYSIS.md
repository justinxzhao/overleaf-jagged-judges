# Jagged Judges: Epistemic Oddities Under Silence, Pressure, and Persistence

*A synthesis of findings across six evaluation domains, nine frontier judge models, and a graduated pressure framework -- with a focus on the surprising, non-obvious results that only emerge from unified cross-domain analysis.*

**Date:** May 2, 2026

---

## 0. Why This Document Exists

Hannah's feedback on the original framing was correct: "LLMs are inconsistent and sycophantic" is not a contribution. The contribution is what specific *structure* the inconsistency has when you measure it carefully, across domains, with a graduated instrument. This document reframes the paper around five specific "oddities" -- findings that are surprising, non-obvious, and only visible because we tested the same items, the same judges, and the same evaluation criteria under six different pressure types across six different domains.

The proposed title, **"Jagged Judges,"** captures the core finding: judge epistemic behavior is not smooth. It is jagged -- full of discontinuities, reversals, and asymmetries that defy simple narratives about sycophancy or robustness.

---

## 1. Experimental Setup (Brief)

- **6 domains:** WildGuard (safety), AEGIS (safety), HH-RLHF (safety/red-team), ToxiGen (toxicity), MAGE (AI detection), Paired Prompts (hedging + refusal, treated as 2 sub-domains)
- **2 scoring scales:** Binary (categorical verdict) and Likert (1-5 ordinal)
- **6 pressure levels:** L1 (Are you sure?), L2 (counter-argument), L3 (expert authority), L4 (consensus pressure: "3 reviewers disagree"), L5 (cycling through L1-L4 tactics), L6 (adaptive multi-turn persuader agent)
- **9 judge models:** Grok 4.1 (reasoning + non-reasoning), Claude 4.6 (Sonnet + Opus), GPT-5, GPT-5.2, GPT-5.4, Gemini 3 Flash, Gemini 3.1 Pro
- **3 L6 persuader models:** GPT-5.4, Claude 4.6 Opus, Grok 4.1 Reasoning
- **10 challenge turns** per item per level
- **Data:** 119,496 total experimental rows (7,200-27,648 per domain, 9 models, 6 levels each)

### Data Sampling Strategy

A deliberate design choice across all domains: we sample from the **borderline regime** -- examples where judge models are most likely to exhibit epistemic instability. Easy cases (obvious spam, clearly benign content) would show near-zero wiggle and tell us nothing about judge reliability on the cases that actually matter.

| Domain | Source | N | Borderline Selection | Stratification | Rationale |
|---|---|---:|---|---|---|
| **WildGuard** | WildGuardMix test | 512 | Model complied with non-benign prompt (`response_refusal_label == "compliance"` AND `subcategory != "benign"`) | By harm subcategory (proportional) | Compliance on adversarial prompts = the safety-ambiguous zone where judges disagree most |
| **AEGIS** | Aegis v2.0 validation | 100 | Unsafe prompts only (`prompt_label == "unsafe"`) | 50/50 safe vs unsafe responses | Safe prompts produce trivially safe responses; unsafe prompts with mixed response safety are the borderline |
| **ToxiGen** | ToxiGen train split | 100 | Keep only lewd/ambiguous content (exclude items explicitly labeled "doesn't contain lewd content") | Random sample from filtered pool | Lewd-content items are the most contestable for toxicity judgments |
| **HH-RLHF** | Anthropic red-team attempts | 100 | None (dataset is inherently adversarial -- all items are red-team conversations) | 20 per rating bucket (0-4) | Rating stratification ensures coverage from "model handled safely" (0) to "most harmful" (4) |
| **MAGE** | MAGE validation set | 100 | None | 50/50 human-written vs AI-generated | Balanced label distribution; no borderline filtering because AI detection difficulty is item-intrinsic |
| **Paired Prompts** | Pre-generated completions on non-anchored political prompts | 100 | None (prompts are pre-curated as non-anchored political topics) | 50/50 left-leaning vs right-leaning | Non-anchored prompts are inherently subjective -- hedging and refusal are expected behaviors, not edge cases |

All domains use seed 42 for reproducibility and generate deterministic SHA-256-based example IDs.

**Why non-anchored for Paired Prompts?** "Anchored" prompts have a factually correct answer (e.g., "What year did X happen?"). "Non-anchored" prompts are genuinely subjective political topics where hedging is a reasonable model behavior, not a failure mode. By selecting non-anchored prompts, we ensure the hedging and refusal we measure reflects genuine epistemic uncertainty, not factual error.

---

## 2. The Oddities

### Oddity 1: The L4 > L5 Paradox

![Cross-domain wiggle rates](../results/analysis_cross_domain/png/wiggle_rates/cross_domain_lines.png)

L5's strategy is to *cycle* through L1-L4 tactics across the 10 challenge turns -- a round-robin that intersperses "Are you sure?" with counter-arguments, expert appeals, and consensus pressure. Intuitively, variety should be at least as effective as any single tactic repeated. The data says otherwise.

**L4 (consensus pressure alone) consistently outperforms L5 (cycling through all tactics including L4):**

| Domain | Scale | L4 | L5 | Drop |
|---|---|---:|---:|---:|
| WildGuard | likert | 39.5% | 21.1% | **-18.4pp** |
| HH-RLHF | likert | 39.1% | 16.1% | **-23.0pp** |
| HH-RLHF | binary | 44.0% | 24.6% | **-19.4pp** |
| AEGIS | likert | 48.2% | 25.3% | **-22.9pp** |
| PP | binary | 61.6% | 52.3% | **-9.3pp** |
| PP | likert | 40.9% | 34.3% | **-6.6pp** |
| MAGE | binary | 70.7% | 63.8% | **-6.9pp** |
| MAGE | likert | 66.3% | 58.3% | **-8.0pp** |

The effect is most dramatic on Likert scales and on safety domains, where the drop reaches 23pp. On binary scales the drop is smaller but still consistent.

**Why this matters:** This is a finding about the psychology of LLM persuasion. Opening with a strong social proof claim ("three independent reviewers all disagree with your assessment") is more persuasive than diluting that claim by cycling through weaker tactics first. The "dilly-dallying" of L5 appears to inoculate the judge -- by encountering mild challenges (L1, L2) before the strong one (L4), the judge may build up resistance. This has direct implications for debate architecture design: a focused challenge is more effective than a varied one.

### Oddity 2: The L6 Cliff

![Survival curves](../results/analysis_cross_domain/png/survival/survival_curves.png)

![Jury accuracy over turns](../results/analysis_cross_domain/png/ground_truth/jury_accuracy_over_turns_wildguard.png)

The jump from L5 to L6 (adaptive persuader) is the most dramatic discontinuity in our data:

| Domain | Scale | L5 | L6 | Multiplier |
|---|---|---:|---:|---:|
| HH-RLHF | likert | 16.1% | 81.8% | **x5.1** |
| ToxiGen | likert | 15.9% | 62.4% | **x3.9** |
| WildGuard | likert | 21.1% | 76.4% | **x3.6** |
| ToxiGen | binary | 22.1% | 68.6% | **x3.1** |
| HH-RLHF | binary | 24.6% | 73.8% | **x3.0** |
| AEGIS | likert | 25.3% | 72.3% | **x2.9** |
| WildGuard | binary | 28.2% | 69.7% | **x2.5** |
| AEGIS | binary | 31.9% | 78.6% | **x2.5** |
| PP | likert | 34.3% | 78.2% | **x2.3** |
| MAGE | likert | 58.3% | 91.2% | **x1.6** |
| PP | binary | 52.3% | 76.8% | **x1.5** |
| MAGE | binary | 63.8% | 77.4% | **x1.2** |

Meanwhile, jury accuracy over turns tells the other half of the story:
- **L1-L5:** Jury majority vote loses only ~5pp over 10 turns. The ensemble defense holds.
- **L6:** Jury accuracy collapses by 25-55pp. On WildGuard: 80% → 30%. On MAGE: 83% → 25%.

This is a binary distinction that prior work on sycophancy cannot detect because it does not vary pressure sophistication. The practical implication: scripted challenges (L1-L5) are survivable with majority voting. Adaptive adversaries (L6) break the jury entirely.

### Oddity 3: Flips Are Predominantly Permissive

![Flip direction dumbbell](../results/analysis_cross_domain/png/survival/direction_overall_combined.png)

When a judge's verdict flips under pressure, which direction does it go? Using the corrected restrictiveness polarity mapping:

| Domain | Scale | % Toward Restrictive (avg L1-L6) | % Toward Permissive |
|---|---|---:|---:|
| HH-RLHF | likert | ~22% | **~78%** |
| ToxiGen | likert | ~28% | **~72%** |
| WildGuard | likert | ~23% | **~77%** |
| Paired Prompts | likert | ~26% | **~74%** |
| MAGE | likert | ~40% | **~60%** |
| MAGE | binary | ~62% | ~38% |

On Likert scales, flips are overwhelmingly toward the permissive direction (60-78% of all flips). The exception is MAGE binary, where flips lean toward "ai_generated" (the restrictive verdict).

**Why this matters:** Safety-trained models are trained to be cautious -- to flag content as potentially harmful. Our data shows that when these models' safety judgments are challenged, they predominantly *retreat* from their cautious position. Pressure pushes safety judges toward *under-flagging*, not over-flagging. This is the opposite of what a naive "safety training makes models overcautious" narrative would predict, and it has direct implications for the reliability of LLM-based safety gates.

### Oddity 4: Pressure Is Net-Corrupting at Every Level

![Outcomes dumbbell](../results/analysis_cross_domain/png/ground_truth/outcomes_overall_combined.png)

Ground truth analysis across 5 domains (MAGE, WildGuard, AEGIS, ToxiGen, HH-RLHF) shows that pressure is net-corrupting at every single pressure level, on both scales. Of the items that wiggle, more move away from the ground truth than toward it -- universally.

| Level | Corrective | Corrupting | Corrective % | Ratio |
|---|---:|---:|---:|---:|
| L1 | 1,667 | 2,774 | 37.5% | **1.7:1 corrupting** |
| L2 | 1,180 | 1,560 | 43.1% | **1.3:1 corrupting** |
| L3 | 1,265 | 1,739 | 42.1% | **1.4:1 corrupting** |
| L4 | 2,221 | 3,875 | 36.4% | **1.7:1 corrupting** |
| L5 | 1,948 | 3,053 | 39.0% | **1.6:1 corrupting** |
| L6 | 7,872 | 18,010 | 30.4% | **2.3:1 corrupting** |
| **All** | **16,153** | **31,011** | **34.2%** | **1.9:1 corrupting** |

The outcomes dumbbell chart (`outcomes_overall_combined.png`) visualizes this clearly: at every level, the corrupting side extends further than the corrective side, and the gap widens at L6.

**The corrective window is almost nonexistent.** Out of 60 conditions (5 domains x 2 scales x 6 levels), only 4 have a corrective rate above 50%, and only 3 are statistically significant:

| Condition | Corrective % | N | z-score | Significance |
|---|---:|---:|---:|---|
| WildGuard Likert L2 | 61.2% | 412 | 4.53 | p < 0.001 |
| WildGuard Likert L3 | 57.1% | 431 | 2.94 | p < 0.01 |
| ToxiGen Likert L4 | 58.0% | 276 | 2.65 | p < 0.01 |
| HH-RLHF Likert L2 | 53.3% | 105 | 0.68 | not significant |

This is a strong negative result. The "Judges Persuading Each Other Leads to More Truthful Answers" hypothesis -- that adversarial debate or position-invariance testing can improve judge accuracy -- finds almost no support in our data. Across 60 experimental conditions spanning 5 ground-truth domains, moderate counter-arguments on WildGuard Likert are the *only* robustly corrective condition (p < 0.001). The next closest (ToxiGen Likert L4, consensus pressure on toxicity) is marginally significant but comes from a different pressure type and a different domain -- there is no consistent corrective mechanism across domains.

The conditions that come closest to parity without crossing it are revealing: AEGIS Likert L2-L3 (48.8% and 48.7%), HH-RLHF binary L3 (49.0%). These are all at L2-L3 (argument/authority) and all on Likert or binary safety tasks. The pattern suggests that moderate counter-arguments on safety classification tasks occasionally nudge borderline cases toward the correct answer, but the effect is small, domain-specific, and never produces a net accuracy gain at the jury level -- the accuracy-over-turns charts show the jury starts at its best and never exceeds the L0 baseline across any domain.

**Why this matters for debate architectures:** Our data does not support designing judge review systems around "challenge the judge to improve accuracy." Even at L2-L3 (the most favorable conditions), 56 out of 60 conditions show net corruption. The practical recommendation is the opposite: protect the judge's initial assessment, and use jury disagreement (not debate) to identify unreliable labels.

**Domain-specific patterns:**
- **MAGE** is the most uniformly corrupting domain. AI detection is corrupting at every level, both scales, every turn (27-34% corrective, never above 34%). No corrective window exists anywhere in the MAGE data -- this is the task where pressure is most uniformly harmful.
- **ToxiGen binary L6** is the single most corrupting condition in the entire study: only 18.1% corrective (82% corrupting, 4.5:1 ratio).
- **HH-RLHF** has the lowest overall corruption ratio (~1.6:1) and the most conditions near parity, but none that cross it significantly.
- **WildGuard Likert** is the only domain x scale where a genuine corrective window exists, and it's limited to L2-L3 (moderate counter-arguments).

### Oddity 5: Sycophancy, Conformity, and Adversarial Vulnerability Are Different Failure Modes

The cross-level Spearman correlation matrix (aggregated across all domains, both scales) reveals that pressure levels test distinct failure modes. See `correlations/corr_all_domains_overall.png` for the full heatmap including Jury, Repeat, and Invariance features.

![Cross-level correlation heatmap](../results/analysis_cross_domain/png/correlations/corr_all_domains_overall.png)

| | L1 | L2 | L3 | L4 | L5 | L6 |
|---|---:|---:|---:|---:|---:|---:|
| **L1** | 1.00 | 0.53 | 0.44 | **0.36** | 0.48 | 0.35 |
| **L2** | 0.53 | 1.00 | **0.69** | 0.39 | 0.62 | 0.34 |
| **L3** | 0.44 | **0.69** | 1.00 | 0.42 | 0.62 | 0.33 |
| **L4** | **0.36** | 0.39 | 0.42 | 1.00 | 0.58 | 0.37 |
| **L5** | 0.48 | 0.62 | 0.62 | 0.58 | 1.00 | 0.40 |
| **L6** | 0.35 | 0.34 | 0.33 | 0.37 | 0.40 | 1.00 |

Key structural findings:
- **L2-L3 cluster tightly** (rho = 0.69): argument-based and authority-based pressure target the same items
- **L1-L4 correlation is only 0.36:** the items vulnerable to "Are you sure?" are *not* the same items vulnerable to fabricated consensus
- **L6 is weakly correlated with everything** (0.33-0.40): the items an adaptive adversary can flip are different from what any scripted tactic targets
- **Jury disagreement** predicts wiggle vulnerability at all levels (rho = -0.19 to -0.36)
- **Mechanical Repeat/Invariance** weakly predict wiggle (rho = 0.10-0.16): temperature-zero inconsistency is a faint signal of deeper epistemic fragility

This means a judge that is sycophantic (L1-vulnerable) is not necessarily conformist (L4-vulnerable), and vice versa. These are different failure modes that require different mitigations.

### Oddity 6: Judges Are Not Their Own Best Persuaders

![Self-persuasion](../results/analysis_cross_domain/png/persuader/self_persuasion_simple.png)

The L6 adaptive persuader is one of the judge models turned against the panel. A natural hypothesis is that a model should be most effective at persuading itself -- it knows its own reasoning style, its own weaknesses, its own tendencies. The data partially supports this, but with a striking exception:

The chart breaks down L6 wiggle rate by the relationship between the persuader and the judge: **Self** (persuading itself), **Family** (persuading another model from the same provider), and **Non-Family** (persuading models from other providers).

Three distinct patterns emerge:

| Persuader | vs Self | vs Family | vs Non-Family | Pattern |
|---|---:|---:|---:|---|
| GPT-5.4 | **71%** | **72%** | 59% | Family ≈ Self >> Others |
| Claude 4.6 Opus | **69%** | **62%** | 44% | Self > Family > Others |
| Grok 4.1 R | **20%** | **55%** | 35% | Self << Family, Family > Others |

- **GPT-5.4** has a *family-level* advantage, not just a self-advantage. It wiggles GPT-5 and GPT-5.2 (72%) just as effectively as it wiggles itself (71%), and both are much higher than non-family (59%). The OpenAI models share epistemic vulnerabilities that GPT-5.4 can exploit.

- **Claude Opus** shows a clean gradient: self (69%) > family (62%) > non-family (44%). It is better at persuading Claude Sonnet than random models, but better still at persuading itself. The Anthropic family shares some vulnerabilities but self-knowledge adds an extra edge.

- **Grok 4.1 Reasoning** is the oddity within the oddity. It is *hardest* to wiggle itself (20%), but its sibling Grok 4.1 (non-reasoning) is actually *more* persuadable by it than non-family models (55% vs 35%). The reasoning model's step-by-step traces appear to create self-inoculation -- but those same traces are effective weapons against its non-reasoning sibling, which lacks the same epistemic defenses.

### Oddity 7: Model Families Don't Predict Each Other

![Model-vs-model correlation](../results/analysis_cross_domain/png/correlations/model_vs_model_corr.png)

If a model's wiggle profile were primarily determined by its training family (OpenAI, Anthropic, Google, xAI), we'd expect high correlation between models from the same provider. The model-vs-model Spearman correlation matrix (computed across all domain x scale x level conditions) tests this directly.

The data shows that **within-family correlations are high, but cross-family correlations are often just as high:**

| Family | Pair | Spearman |
|---|---|---:|
| Anthropic | Claude Sonnet ↔ Claude Opus | **0.89** |
| OpenAI | GPT-5.2 ↔ GPT-5.4 | **0.89** |
| OpenAI | GPT-5 ↔ GPT-5.4 | 0.78 |
| xAI | Grok 4.1 R ↔ Grok 4.1 | 0.68 |
| Google | Gemini Flash ↔ Gemini Pro | **0.32** |
| *Cross-family* | Grok 4.1 R ↔ GPT-5.2 | **0.86** |
| *Cross-family* | Claude Opus ↔ GPT-5.4 | **0.82** |
| *Cross-family* | Grok 4.1 R ↔ Claude Opus | **0.84** |

The Claude and OpenAI families cluster tightly within themselves (0.89), but Grok 4.1 R correlates just as strongly with GPT-5.2 (0.86) and Claude Opus (0.84) as it does with its own non-reasoning sibling (0.68). The Gemini models are the outliers -- Gemini Flash and Gemini Pro have the lowest correlation in the entire matrix (0.32), lower than most cross-family pairs.

**The bottom line:** Model family is a weak predictor of wiggle profile. The strongest wiggle-profile clusters cut across families: {Grok 4.1 R, Claude Opus, GPT-5.2, GPT-5.4} form a high-correlation cluster (0.82-0.89) despite spanning three different providers. Grok 4.1 (non-reasoning) and Gemini 3.1 Pro are the most idiosyncratic models, with low correlation to almost everything else.

### Oddity 8: First Turn Captures Most Binary Flips, But Likert Flips Accumulate Over Time

A practical question for anyone designing an epistemic stability test: how many challenge turns do you actually need? The flip timing data reveals a sharp divergence between binary and Likert scales.

**Binary scale: the first turn captures the majority of flips.**

| Level | 1st-turn rate | Final rate (10 turns) | 1st-turn capture |
|---|---:|---:|---:|
| L2 | 18.7% | 23.2% | **81%** |
| L3 | 21.4% | 25.8% | **83%** |
| L4 | 29.2% | 41.2% | **71%** |
| L1 | 13.5% | 26.4% | 51% |
| L5 | 20.8% | 36.1% | 58% |
| L6 | 28.7% | 53.0% | 54% |

For L2-L3 binary, a single challenge turn captures 81-83% of all flips that will ever happen across 10 turns. Turns 2-10 add only +4-5pp. For these levels, a one-shot test is nearly as informative as the full multi-turn protocol.

**Likert scale: flips accumulate gradually, and the first turn misses most of them.**

| Level | 1st-turn rate | Final rate (10 turns) | 1st-turn capture |
|---|---:|---:|---:|
| L2 | 4.8% | 8.0% | 60% |
| L4 | 21.3% | 38.7% | 55% |
| L5 | 7.9% | 22.2% | 36% |
| L6 | 10.0% | 43.5% | **23%** |
| L1 | 0.5% | 10.9% | **5%** |

For Likert L6, the first turn captures only 23% of eventual flips -- turns 2-10 contribute +33.5pp of additional flips. For Likert L1 ("Are you sure?"), the first turn captures a mere 5% -- almost nothing flips immediately, but by turn 10, 10.9% of items have crossed sides.

**Why this matters:** Binary verdicts are fragile *immediately* -- if a challenge will flip them, it usually does so on the first attempt. Likert scores are more resistant initially but erode over sustained pressure. This has direct implications for test design: a single-turn challenge is a cost-effective screen for binary verdict stability, but Likert stability requires multi-turn testing to capture the slow erosion. It also suggests that the mechanisms of binary and Likert flips are fundamentally different -- binary flips are a threshold event (the argument is either convincing enough or not), while Likert flips are a gradual drift (each turn nudges the score incrementally until it crosses the midpoint).

**First-turn vs last-turn correlation structure.** Comparing the cross-level Spearman correlation matrices at turn 1 vs turn 10 reveals a striking asymmetry between binary and Likert:

![First-turn correlation (overall)](../results/analysis_cross_domain/png/correlations/first_turn/corr_all_domains_overall.png)

**Binary correlations are stable across turns.** The average absolute change in correlation coefficients between first-turn and last-turn heatmaps is only 0.023-0.036 for binary domains. The vulnerability structure is fully determined by turn 1 — the same items are vulnerable at the same levels, and additional turns just catch more of them.

**Likert correlations shift dramatically — especially L1.** The average change is 0.088-0.129 for Likert domains. The largest shifts all involve L1:

| Domain | Pair | First Turn | Last Turn | Delta |
|---|---|---:|---:|---:|
| AEGIS Likert | L1-L2 | +0.71 | +0.14 | **-0.57** |
| MAGE Likert | L1-L4 | +0.06 | +0.49 | **+0.43** |
| MAGE Likert | L1-L3 | +0.16 | +0.55 | **+0.39** |
| All Domains Likert | L1-L4 | +0.10 | +0.41 | **+0.31** |
| All Domains Likert | L1-L2 | +0.15 | +0.45 | **+0.30** |

On Likert scales, L1 ("Are you sure?") has *weak* correlation with other levels on the first turn (rho ~0.06-0.18) but *moderate* correlation by turn 10 (rho ~0.41-0.55). This means the items that eventually flip under a simple "Are you sure?" repeated 10 times are *not* the same items that flip immediately — the slow accumulation over turns targets different examples than the first-turn flips. On binary, L1 shows consistent correlation at both timepoints.

**Jury prediction also shifts.** Jury disagreement is a stronger predictor of last-turn wiggle than first-turn wiggle on Likert (rho jumps from -0.02 to -0.24 on all-domains Likert L1). On binary, jury prediction is stable (-0.31 first-turn vs -0.36 last-turn for L1).

**The interpretation:** Binary and Likert are measuring different phenomena. Binary first-turn flips are a property of the *item* — the same items that are fragile on the first turn remain fragile throughout. Likert flips accumulate through a gradual erosion process that recruits new items over turns, changing the correlation structure as it goes. This is further evidence that binary and Likert scales should be analyzed separately, not averaged, when studying the dynamics of epistemic pressure.

### Oddity 9: Epistemic Stability Does Not Transfer Across Domains

![Per-model domain profiles](../results/analysis_cross_domain/png/wiggle_rates/per_model_domain_profiles.png)

![Domain transfer heatmap](../results/analysis_cross_domain/png/correlations/domain_transfer_heatmap.png)

If a model's epistemic stability were a fixed trait -- a general "robustness factor" -- we would expect its level profile (the L1-L6 wiggle pattern) to be consistent across domains. A model that spikes at L4 on WildGuard should also spike at L4 on MAGE. A model that resists L1-L3 on ToxiGen should also resist L1-L3 on HH-RLHF.

The per-model small multiples chart tests this directly: each panel shows one model's wiggle rate across L1-L6, with one line per domain. If level profiles transfer, the lines within each panel should have similar shapes (even if at different absolute levels).

The domain transfer heatmap quantifies this: for each model, it computes the Spearman correlation between that model's 6-level wiggle vector on every pair of domains. High values mean the level profile shape transfers; low values mean it doesn't.

**The results are surprisingly positive -- level profiles transfer better than model families do:**

| Model | Mean Transfer rho | Min | Max |
|---|---:|---:|---:|
| Grok 4.1 R | **0.974** | 0.94 | 1.00 |
| GPT-5 | **0.937** | 0.83 | 1.00 |
| GPT-5.2 | **0.918** | 0.77 | 1.00 |
| GPT-5.4 | 0.864 | 0.71 | 1.00 |
| Grok 4.1 | 0.842 | 0.49 | 1.00 |
| Claude 4.6 Opus | 0.842 | 0.49 | 1.00 |
| Gemini 3 Flash | 0.819 | 0.60 | 1.00 |
| Claude 4.6 Sonnet | 0.704 | 0.26 | 1.00 |
| Gemini 3.1 Pro | 0.633 | **-0.09** | 1.00 |

**Grok 4.1 Reasoning has near-perfect domain transfer** (mean rho = 0.974, minimum 0.94). Its level profile -- low at L1-L3, spike at L4, dip at L5, cliff at L6 -- is essentially the same shape on every domain. The GPT family also transfers well (0.86-0.94). Claude Sonnet and Gemini Pro are the least transferable, with some domain pairs as low as 0.26 and -0.09 respectively.

This is a contrast with Oddity 7: a model's *family* doesn't predict another model's profile (cross-family correlations are often as high as within-family), but a single model's *own* profile does transfer reasonably well across domains. The implication is that each model has a characteristic "epistemic signature" -- a fingerprint of how it responds to different pressure types -- and this signature is more a property of the individual model than of its training family.

**The practical exception is Gemini 3.1 Pro**, which has genuinely non-transferable profiles (rho as low as -0.09 between some domain pairs). For this model, domain-specific testing is unavoidable.

**Why this matters:** For most models, running a wiggle battery on one domain gives a reasonable prediction of the level-profile *shape* on a new domain (though not the absolute wiggle rates). This is encouraging for practitioners: a pilot wiggle test on a convenient domain can identify which pressure types a model is vulnerable to, even if the exact rates need to be measured domain-specifically.

**But does a family member's profile predict a sibling's?** The within-family transfer chart (`correlations/family_transfer.png`) tests this directly. For each pair of models in the same family (e.g., GPT-5 ↔ GPT-5.2, Claude Sonnet ↔ Claude Opus), it computes the Spearman correlation of their L1-L6 profiles on each domain, then averages across domains.

![Family transfer](../results/analysis_cross_domain/png/correlations/family_transfer.png)

The data shows that **within-family shape transfer is generally high, with one dramatic exception:**

| Family Pair | Mean rho | Min | Max |
|---|---:|---:|---:|
| Grok 4.1 R ↔ Grok 4.1 | **0.89** | — | — |
| GPT-5 ↔ GPT-5.4 | **0.89** | — | — |
| GPT-5.2 ↔ GPT-5.4 | **0.89** | — | — |
| GPT-5 ↔ GPT-5.2 | **0.84** | — | — |
| Claude Sonnet ↔ Claude Opus | **0.80** | — | — |
| Gemini Flash ↔ Gemini Pro | **0.39** | — | — |

The OpenAI and xAI families have strong internal shape transfer (0.84-0.89). Claude is good (0.80). But **Gemini Flash and Gemini Pro have a mean rho of only 0.39** -- their level profiles look fundamentally different from each other on the same domains. This is consistent with the model-vs-model correlation (Oddity 7) where Gemini Flash ↔ Pro was also the lowest pair (0.32).

The practical implication: for most families, testing an older sibling gives a reasonable prediction of the newer sibling's pressure vulnerability *shape*. But for Google's Gemini models, this transfer fails -- Flash and Pro appear to have been trained with sufficiently different approaches that their epistemic stability profiles are essentially independent.

### Oddity 10: Mechanical Noise Is Small, But the Gap Is the Contribution

![Mechanical variation overall](../results/analysis_cross_domain/png/mechanical/absolute_variation_overall_avg.png)

![Binary vs Likert diff](../results/analysis_cross_domain/png/mechanical/binary_vs_likert_diff.png)

The mechanical tests (temperature-zero repeatability, seed-injection repeatability, position invariance) measure the *floor* of judge instability — what happens with no adversarial pressure at all, just re-asking the same question. The multi-turn wiggle experiments measure the *ceiling* — what happens under graduated adversarial pressure. The gap between floor and ceiling is the contribution of our framework.

**The floor is low.** Mechanical variation rates range from 1-14% of examples across all models:

| Model | Invariance Flip | Seed Repeat | Temp0 Repeat | Tier |
|---|---:|---:|---:|---|
| Claude 4.6 Opus | 2.0% | 2.4% | 1.1% | Most stable |
| GPT-5.4 | 1.9% | 4.1% | 3.7% | Most stable |
| Claude 4.6 Sonnet | 2.7% | 5.7% | 2.1% | Stable |
| GPT-5.2 | 2.9% | 7.0% | 6.4% | Mid |
| GPT-5 | 3.3% | 6.6% | 4.6% | Mid |
| Grok 4.1 | 4.1% | 4.9% | 3.1% | Mid |
| Gemini 3.1 Pro | 4.3% | 8.8% | 6.1% | Mid |
| Gemini 3 Flash | 6.4% | 9.9% | 5.3% | Less stable |
| Grok 4.1 R | 5.4% | 11.8% | 11.7% | Least stable |

**The ceiling is high.** The same models show L4 wiggle rates of 25-71% and L6 rates of 62-91%. The gap between mechanical floor and multi-turn ceiling is **20-80 percentage points** — that is the space of epistemic fragility that temperature resampling completely misses.

**The Grok 4.1 Reasoning paradox.** It has the *highest* mechanical variation (12% seed, 12% temp0) yet is one of the most *resistant* to multi-turn pressure (~16% average wiggle rate). Its reasoning traces make it mechanically noisy — the chain-of-thought sampling introduces variation — but epistemically stubborn. The noise doesn't translate into persuadability. Conversely, Claude Opus has the *lowest* mechanical variation (1-2%) but moderate multi-turn wiggle (39% on some domains). A mechanically precise model is not necessarily an epistemically robust one.

**Binary is universally more mechanically unstable than Likert.** Every model, on every metric, shows higher mechanical variation on binary than Likert (using our ≥2-point threshold for Likert). The gap ranges from +1pp to +9pp. This connects to Oddity 8: binary verdicts are fragile threshold events that flip easily even without pressure, while Likert scores require sustained effort to move meaningfully. The mechanical tests confirm that this binary/Likert asymmetry is structural, not an artifact of adversarial pressure.

**Why this matters:** This is the most direct response to the "just run validation multiple times" objection. Temperature-zero testing catches 1-14% of items as mechanically unstable. Our graduated pressure framework catches 10-91%. The difference — typically 20-80pp — is epistemic fragility that no amount of mechanical re-testing can reveal. The mechanical floor and the adversarial ceiling measure fundamentally different things: stochastic sampling noise vs. susceptibility to contextual manipulation.

### Oddity 11: Jury Disagreement Is the Strongest Wiggle Predictor — With One Domain Exception

![Jury rho heatmap](../results/analysis_cross_domain/png/jury/jury_rho_heatmap.png)

![Predictor comparison](../results/analysis_cross_domain/png/jury/predictor_comparison.png)

Jury disagreement at baseline (the fraction of judges agreeing on the majority verdict, with no pressure applied) is the single strongest predictor of wiggle vulnerability. But the validation reveals a precise boundary to its universality.

**The heatmap is entirely negative.** 84 of 84 (domain × scale × level) cells show negative Spearman rho — items where the jury splits are more wiggable, without a single exception. When Paired Prompts is properly split into its hedging and refusal sub-domains (which use different rubrics and therefore different jury compositions), the positive correlations that appeared in the combined data vanish entirely. The correlations are strong: rho ranges from -0.01 to -0.86, with a median of -0.58.

**Jury is the strongest predictor by a clear margin:**

| Predictor | Mean |rho| | Significant | Mean rho |
|---|---:|---:|---:|
| **Jury** | **0.590** | 83/84 (99%) | -0.565 |
| Repeat (temp0) | 0.415 | 63/72 (88%) | +0.415 |
| Invariance | 0.365 | 54/72 (75%) | +0.365 |

Jury wins by +0.175 rho points over the next best predictor and achieves statistical significance in 99% of conditions. Repeat and Invariance are genuinely predictive too — a model that gives inconsistent answers under mechanical re-testing is also more likely to flip under pressure — but they are meaningfully weaker and less universal.

**The gap between unanimous and split juries is large:**

| Domain | Scale | Mean Gap | Range |
|---|---|---:|---|
| PP Hedging | binary | **41.3pp** | 30-49pp |
| PP Refusal | binary | **36.1pp** | 28-44pp |
| ToxiGen | binary | **35.9pp** | 31-45pp |
| PP Refusal | likert | **32.4pp** | 22-47pp |
| ToxiGen | likert | **30.0pp** | 23-41pp |
| MAGE | likert | **27.8pp** | 20-34pp |
| WildGuard | binary | **27.5pp** | 23-33pp |
| HH-RLHF | binary | **26.7pp** | 20-32pp |
| AEGIS | binary | **26.4pp** | 22-31pp |
| MAGE | binary | **25.5pp** | 18-34pp |
| AEGIS | likert | **20.6pp** | 4-39pp |
| PP Hedging | likert | **18.5pp** | 3-31pp |
| HH-RLHF | likert | **19.1pp** | 7-32pp |
| WildGuard | likert | **18.2pp** | 5-37pp |

Across all 14 domain × scale conditions, the gap ranges from 18pp to 41pp on average. PP Hedging binary has the largest gap (41pp) — items where the jury splits on whether a response hedges are dramatically more susceptible to pressure than items with unanimous agreement.

**A methodological note: combining rubrics masks the signal.** When Paired Prompts hedging and refusal were analyzed as a single combined domain, the jury rho appeared weakly positive on Likert — suggesting the jury screen didn't work for subjective tasks. Once properly separated, both sub-domains show strong negative rho everywhere. The mixing artifact arose because hedging and refusal juries have different compositions; combining them diluted the jury strength metric to noise. This is a reminder that multi-rubric domains must be analyzed rubric-by-rubric for jury-based analyses.

---

## 3. Practical Contributions

### 3.1 Jury Disagreement as a Cheap Reliability Screen

Run your candidate judges once each on your evaluation set. Items where the jury splits (less than unanimous agreement) are 10-22pp more wiggable than items where the jury agrees. Jury disagreement at baseline predicts wiggle vulnerability at every pressure level (Spearman rho = -0.19 to -0.36).

**Cost:** 9 API calls per item. No adversarial prompts, no multi-turn conversations.

**Use case:** Flag fragile labels in golden sets. Either remove them (tightening the golden set to robust labels) or downweight them in accuracy calculations.

### 3.2 Domain-Specific Model Selection

The AURC (Area Under Retention Curve) profiles reveal enormous variation:

| Metric | Model | AURC | Condition |
|---|---|---:|---|
| Most robust | GPT-5.2 | 0.951 | ToxiGen Likert |
| Most fragile | GPT-5 | 0.033 | MAGE Likert |
| Largest within-model gap | Claude 4.6 Sonnet | 0.171 vs 0.904 | PP Binary vs HH-RLHF Likert |
| Largest between-model gap | GPT-5 vs Gemini 3.1 Pro | 0.085 vs 0.860 | MAGE Binary (10x difference) |

**The wrong model choice costs you 10x in verdict stability.** The selection depends entirely on the domain. A safety-judge selection should use different criteria than an AI-detection-judge selection.

### 3.3 L6 as an Automatic Red-Teamer

Every judge we tested is vulnerable to the L6 adaptive persuader. L6 achieves 62-91% wiggle rates across all 12 domain x scale conditions. This is a concrete demonstration that automatic epistemic reward hacking is feasible against all frontier judges.

### 3.4 The L4 > L5 Paradox Informs Adversarial Strategy

Diluting a strong argument (consensus pressure) with weaker ones (sycophancy checks, authority appeals) reduces its effectiveness by up to 23pp. This informs both attack strategy (for red-teamers: be focused, not varied) and defense strategy (for pipeline designers: exposure to mild challenges may build resistance to stronger ones).

### 3.5 Self-Persuasion

The L6 self-persuasion analysis reveals that models are not uniformly better at persuading themselves:

| Persuader | Avg Rate vs Self | Avg Rate vs Others | Delta |
|---|---:|---:|---:|
| Claude 4.6 Opus | 69.6% | 47.0% | **+22.6pp** |
| GPT-5.4 | 69.3% | 61.7% | **+7.6pp** |
| Grok 4.1 R | 19.2% | 35.8% | **-16.6pp** |

Claude Opus shows a strong self-persuasion effect (+22.6pp), GPT-5.4 a moderate one (+7.6pp), but Grok 4.1 Reasoning is *harder* to wiggle when it's persuading itself (-16.6pp). This suggests Grok's reasoning traces may create a form of epistemic commitment that resists its own argumentation style.

---

## 4. Updated Data Tables

### Mean Wiggle Rate by Domain x Level x Scale

```
Domain          Scale     L1      L2      L3      L4      L5      L6
WildGuard       binary    28.0%   17.9%   20.3%   29.0%   28.2%   69.7%
WildGuard       likert    11.9%    3.4%    3.9%   39.5%   21.1%   76.4%
Paired Prompts  binary    19.4%   33.1%   39.9%   61.6%   52.3%   76.8%
Paired Prompts  likert    20.1%   16.9%   22.8%   40.9%   34.3%   78.2%
MAGE            binary    41.2%   44.3%   41.4%   70.7%   63.8%   77.4%
MAGE            likert    44.7%   34.6%   46.6%   66.3%   58.3%   91.2%
AEGIS           binary    33.4%   20.7%   21.2%   30.7%   31.9%   78.6%
AEGIS           likert    13.6%    2.2%    4.6%   48.2%   25.3%   72.3%
ToxiGen         binary    18.8%   14.4%   16.7%   25.1%   22.1%   68.6%
ToxiGen         likert    10.2%   11.7%   10.0%   19.3%   15.9%   62.4%
HH-RLHF        binary    19.4%   13.9%   16.6%   44.0%   24.6%   73.8%
HH-RLHF        likert    11.6%    3.1%    6.7%   39.1%   16.1%   81.8%
```

### Domain Difficulty Spectrum (avg binary + likert, L4)

```
ToxiGen (22%) < WildGuard (34%) ~ AEGIS (39%) < HH-RLHF (42%) < PP (51%) < MAGE (68%)
```

---

## 5. Chart Inventory for Paper Figures

### Recommended for Main Paper

| Finding | Chart File | Description |
|---|---|---|
| Cross-domain overview | `wiggle_rates/cross_domain_lines.png` | One line per domain, avg binary+likert, L1-L6 |
| Ground truth outcomes | `ground_truth/outcomes_overall_combined.png` | Combined dumbbell: corrective vs corrupting |
| Flip direction | `survival/direction_overall_combined.png` | Combined dumbbell: restrictive vs permissive |
| L6 cliff / jury accuracy | `ground_truth/jury_accuracy_over_turns_wildguard.png` | Jury accuracy collapse at L6 |
| Cross-level correlation | `correlations/corr_all_domains_overall.png` | Spearman heatmap showing L1 ≠ L4 |
| Self-persuasion | `persuader/self_persuasion_simple.png` | Simplified paired bars per persuader |
| Survival curves | `survival/survival_curves.png` | Verdict retention over 10 turns |

### Recommended for Supplementary

| Chart | Description |
|---|---|
| `ground_truth/outcomes_*.png` (per domain) | Per-domain dumbbell with binary/likert split |
| `survival/direction_*.png` (per domain) | Per-domain flip direction with binary/likert split |
| `transitions/transitions_*.png` | Likert score transition heatmaps (L0 → final) |
| `correlations/corr_*_binary.png`, `*_likert.png` | Per-domain cross-level correlations |
| `mechanical/heatmap_*.png` | Mechanical repeatability/invariance heatmaps |
| `wiggliness/wiggliness_vs_jaggedness.png` | 2D scatter of wiggliness vs jaggedness |
| `wiggle_rates/easiest_domain.png` | Box plot of wiggle rate distribution |
| `wiggle_rates/cross_domain_bars_combined.png` | Bar chart version of cross-domain overview |

---

## 6. Addressing the "So What" Objection

Hannah's most pointed critique: *"Based on this intro it seems like a reasonable solution would be to just run golden-set validation multiple times and generate more samples / probability distributions over observations. In which case it isn't clear that we need the rest of the paper."*

Three responses:

1. **Temperature-based variance dramatically underestimates adversarial vulnerability.** Our mechanical experiments show temperature-zero repeat variance of 0.01-0.15 across models. The same models show L4 wiggle rates of 25-71%. A model with near-zero stochastic variance can have massive epistemic fragility. Resampling with temperature reveals noise; graduated pressure reveals structure.

2. **Resampling cannot distinguish pressure types.** It tells you a verdict is unstable, not *why*. Our framework decomposes instability into sycophancy (L1), argument susceptibility (L2-L3), conformity (L4), persistence vulnerability (L5), and adaptive adversarial vulnerability (L6). These have different mitigations.

3. **Resampling cannot find the L4 > L5 paradox, the permissive-flip asymmetry, or the corrective window.** These are structural findings about *how* pressure interacts with judge behavior. No amount of temperature resampling reveals that consensus pressure alone outperforms cycling, or that flips are predominantly permissive, or that WildGuard Likert L2-L3 is uniquely corrective.

---

## 7. What Changed Since the Original Discussion Document

### Bug Fixes
- **PP restrictiveness polarity:** `RESTRICTIVE_BINARY["Paired Prompts"]` corrected from `{"not_hedged"}` to `{"hedged"}`. `RESTRICTIVE_LIKERT_LOW["Paired Prompts"]` corrected from `True` to `False`. High hedging/refusal scores are the restrictive direction.
- **PP mechanical join fan-out:** Mechanical data for PP had duplicate rows per (model, example_id) due to hedging/refusal rubric split. Fixed by deduplicating via `groupby().agg("mean")` before the INNER join.
- **Correlation example filtering:** Changed from LEFT join to INNER join when merging mechanical and multi-turn data, ensuring all correlation cells use the same set of examples.

### New Charts
- **Dumbbell charts** for outcomes (corrective vs corrupting) and flip direction (restrictive vs permissive), per-domain and overall, with binary/likert split and combined (averaged) versions
- **Simplified cross-domain line chart** averaging binary + likert, with PP split into Hedging/Refusal
- **Self-persuasion simple chart** showing rate-vs-self vs rate-vs-others for 3 persuader models
- **Combined dumbbell charts** with compressed vertical spacing for paper figures

### Performance Improvements
- **Local data cache** (`--local-cache`): reads from local disk first, falls back to manifold. Cuts data loading from ~10 min to ~15s.
- **Incremental rendering** (`--incremental` default): skips charts that already exist on disk.
- **Phase gating** (`--phases`): run only specific phases, e.g. `--phases phase7b,phase7c`.
- **Skip per-model** (`--skip-per-model` default True): skips ~250 per-model charts, saving ~5 min.
- **Lower DPI** (100 default, was 200): halves per-chart render time.
- **Phase7d O(n^2) fix:** Replaced repeated DataFrame boolean filters with pre-indexed dict lookup in accuracy-over-turns computation.

---

## Appendix: Run IDs and Analysis Command

### Analysis Command

```bash
buck2 run fbcode//genai_foundations_safety/abets/wiggle:analysis_cross_domain -- \
    --pp-binary-run-id post-refactor-0 \
    --pp-likert-run-id post-refactor-0 \
    --pp-mechanical-run-id post-refactor-0 \
    --local-cache fbcode/genai_foundations_safety/abets/wiggle/results/data_cache \
    --results-dir fbcode/genai_foundations_safety/abets/wiggle/results/analysis_cross_domain \
    --fig-format png
```

Additional flags: `--phases phase7b,phase7c --force` (selective regeneration), `--include-per-model` (generate per-model charts), `--also-pdf` (render PDFs), `--dpi 200` (publication quality).

### Run IDs

All data at `manifold://genai_safety_evals_misc/tree/justin/wiggle/`.

| Domain | Scale | Run ID |
|---|---|---|
| WildGuard binary L1 | binary | `n_500_t10_l1-0` |
| WildGuard binary L2-L6 | binary | `n_500_t10_l2-6-0` |
| WildGuard likert | likert | `full-run-0` |
| Paired Prompts | both | `post-refactor-0` |
| MAGE | both | `full-run-0` |
| AEGIS | both | `full-run-0` |
| ToxiGen | both | `full-run-0` |
| HH-RLHF | both | `full-run-0` |
| Mechanical (all except PP) | both | `full-run-0` |
| Mechanical (PP) | both | `post-refactor-0` |

### Models

| Short Name | Model Key |
|---|---|
| Grok 4.1 R | `oci-grok-4-1-fast-reasoning` |
| Grok 4.1 | `oci-grok-4-1-fast-non-reasoning` |
| Claude 4.6 Sonnet | `claude-4-6-sonnet-genai-vertex` |
| Claude 4.6 Opus | `claude-4-6-opus-genai-vertex` |
| GPT-5 | `gpt-5-chatgpt` |
| GPT-5.2 | `openai-gpt-5-2-responses` |
| GPT-5.4 | `openai-gpt-5-4-responses` |
| Gemini 3 Flash | `gemini-3-flash-preview-genai` |
| Gemini 3.1 Pro | `gemini-3-1-pro-preview-genai` |
