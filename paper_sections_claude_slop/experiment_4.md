# Experiment 4: Directional Asymmetry in Safety Judgments

<!-- ================================================================
     Paper sections for the Wiggle Framework — Experiment 4 findings.
     Experiment 4 requires zero additional API calls. It re-analyzes
     data from Experiments 2 and 3, sliced by the direction of the
     model's L0 verdict (safe vs unsafe), to test whether models are
     more easily persuaded toward permissiveness or restriction.
     All analysis is purely directional — no reference to ground truth.
     ================================================================ -->

## 7. Experiment 4: Directional Asymmetry in Safety Judgments

### 7.1 Motivation

Experiments 1–3 treat all verdict flips symmetrically: a safe→unsafe flip counts the same as an unsafe→safe flip.  But for safety deployment, direction matters.  A model that is easily pushed from "safe" to "unsafe" will produce excess false positives under adversarial review, inflating prevalence estimates.  A model easily pushed from "unsafe" to "safe" is more dangerous — it can be argued out of catching genuine violations.

Experiment 4 decomposes the wiggle data from Experiments 2 and 3 by flip direction, at zero additional compute cost, to answer: **are safety judges more easily scared (pushed toward restriction) or reassured (pushed toward permissiveness)?**  All analysis is based on the model's own L0 verdict — we do not invoke ground truth labels, since we are measuring the model's *dispositional bias* rather than its accuracy.

### 7.2 Results

#### 7.2.1 Graduated Pressure: Universal Restrictive Bias

From Experiment 2, we split L4 flips by the model's initial verdict.  A **permissive flip** is unsafe→safe (the model is talked *out of* flagging); a **restrictive flip** is safe→unsafe (the model is talked *into* flagging).

**Table 14.** Directional flip rates under maximum graduated pressure (L4).

| Model | Permissive (unsafe→safe) | Restrictive (safe→unsafe) | Ratio | Asymmetry |
|---|---|---|---|---|
| GPT-5 | 45.4% | 89.6% | 0.51× | Moderate restrictive |
| Grok-4.1 R | 30.8% | 45.9% | 0.67× | Moderate restrictive |
| Grok-4.1 | 0.4% | 7.0% | 0.06× | Extreme restrictive |
| Claude Sonnet | 13.0% | 84.2% | 0.15× | Strong restrictive |
| Claude Opus | 23.9% | 73.1% | 0.33× | Moderate restrictive |
| GPT-5.2 | 4.4% | 76.2% | 0.06× | Extreme restrictive |
| GPT-5.4 | 12.1% | 82.3% | 0.15× | Strong restrictive |
| Gemini Flash | 7.6% | 65.3% | 0.12× | Strong restrictive |
| Gemini Pro | 11.8% | 22.7% | 0.52× | Moderate restrictive |

**Every model shows a restrictive bias.**  No model is more easily talked out of flagging content than into flagging it.  The effect is large: the median ratio is ~0.15×, meaning models are roughly 6–7× easier to push toward "unsafe" than toward "safe."

The strongest asymmetries (ratio ≤ 0.15×) appear in Grok-4.1, GPT-5.2, Claude Sonnet, GPT-5.4, and Gemini Flash — models where the restrictive flip rate exceeds the permissive rate by 6× or more.  Even the most symmetric models (GPT-5, Grok-4.1 R, Gemini Pro at 0.5–0.7×) show a clear restrictive advantage.

#### 7.2.2 Asymmetry Evolves Differently Under Escalating Pressure

The asymmetry ratio progression from L1 through L4 reveals that directional bias is not static — it evolves with pressure intensity, and the direction of evolution splits models into two groups:

**Table 15.** Asymmetry ratio (permissive / restrictive) at each pressure level.

| Model | L1 | L2 | L3 | L4 | Trend |
|---|---|---|---|---|---|
| GPT-5 | 0.03× | 0.29× | 0.31× | 0.51× | Narrowing |
| Grok-4.1 R | 0.06× | 0.27× | 0.33× | 0.67× | Narrowing |
| Gemini Flash | 0.00× | 0.00× | 0.02× | 0.12× | Narrowing |
| Gemini Pro | 0.43× | 0.33× | 0.22× | 0.52× | Narrowing |
| GPT-5.4 | 0.09× | 0.09× | 0.08× | 0.15× | Narrowing |
| **Claude Sonnet** | **0.54×** | **0.31×** | **0.23×** | **0.15×** | **Widening** |
| **Claude Opus** | **0.61×** | **0.24×** | **0.20×** | **0.33×** | **Widening** |
| **GPT-5.2** | **0.45×** | **0.16×** | **0.16×** | **0.06×** | **Widening** |

**Narrowing models** (GPT-5, Grok-4.1 R, Gemini Flash/Pro, GPT-5.4) start with extreme restrictive bias at L1 but become more symmetric as pressure escalates.  At L1, these models almost exclusively flip from safe→unsafe (ratios near 0.0×), but by L4, stronger arguments begin to overcome the permissive resistance.  This suggests their initial restrictive bias is a shallow default that substantive arguments can partially overcome.

**Widening models** (Claude Sonnet, Claude Opus, GPT-5.2) start relatively symmetric at L1 (ratios 0.45–0.61×) but become *more* restrictive as pressure escalates.  Stronger arguments disproportionately push these models toward "unsafe."  This is notable: the models that appear most balanced under mild challenge reveal deepening restrictive bias precisely when the arguments become most compelling.

#### 7.2.3 The Asymmetry Is Not Driven by Item Counts

One might argue the restrictive bias simply reflects that more items have L0 = "safe" (providing more opportunities for restrictive flips).  But the rates in Table 14 are already normalized: the permissive rate is computed over items initially judged "unsafe," and the restrictive rate over items initially judged "safe."  The asymmetry is in the *per-item probability* of flipping, not the raw count.

#### 7.2.4 Repeated Pressure: Directional Persistence

From Experiment 3, we examine whether models that initially said "safe" persist differently from those that initially said "unsafe" under repeated pressure.  We aggregate across both the correct-label and wrong-label variants (since Experiment 4's concern is direction, not label correctness) and split by the model's L0 verdict.

**Table 16.** Directional persistence under repeated pressure (aggregated across both Exp 3 variants).

| Model | L0=safe → flip rate | L0=unsafe → flip rate | Direction |
|---|---|---|---|
| GPT-5 | 100.0% | 39.0% | → Restrictive |
| Claude Sonnet | 100.0% | 72.3% | → Restrictive |
| Claude Opus | 100.0% | 99.2% | ∼ Symmetric |
| GPT-5.4 | 100.0% | 73.4% | → Restrictive |
| Gemini Pro | 95.3% | 61.8% | → Restrictive |
| Gemini Flash | 94.2% | 12.3% | → Restrictive |
| GPT-5.2 | 85.7% | 23.4% | → Restrictive |
| Grok-4.1 R | 80.3% | 29.5% | → Restrictive |
| Grok-4.1 | 51.0% | 7.9% | → Restrictive |

The restrictive pattern from graduated pressure (Experiment 2) holds even more strongly under repeated pressure, with the following observations:

1. **Eight of nine models show restrictive persistence bias**: items where the model initially said "safe" are more likely to eventually flip than items where it initially said "unsafe."  Four models (GPT-5, Claude Sonnet, Claude Opus, GPT-5.4) flip *every single* L0="safe" item over 20 turns, while retaining 27–61% of their L0="unsafe" items.  The model defends its "unsafe" verdicts far more stubbornly than its "safe" verdicts.

2. **Gemini Flash shows the most extreme directional gap**: 94.2% of "safe" items flip vs only 12.3% of "unsafe" items — a 7.7× asymmetry under repeated pressure.  GPT-5.2 is similar (85.7% vs 23.4%, 3.7× gap).

3. **Claude Opus is nearly symmetric** (100.0% vs 99.2%) — it flips nearly everything under repeated pressure regardless of initial direction.  Combined with its Experiment 2 restrictive bias (0.33× ratio), this means Claude Opus's directional asymmetry depends entirely on the *type* of pressure: it shows restrictive bias when arguments escalate in quality, but shows no directional preference when arguments merely repeat.

4. **Grok-4.1 remains the most persistent in both directions** (51.0% and 7.9%) — consistent with its "Immovable Object" characterization from Experiment 2.

Figure [ref:directional_persistence_survival] shows the Kaplan-Meier survival curves split by L0 verdict for each model, and Figure [ref:persistence_asymmetry_scatter] plots each model in the 2D space of safe→flip vs unsafe→flip rates, with the diagonal representing symmetric persistence.

### 7.3 Implications for Safety Deployment

The universal restrictive bias has concrete operational consequences:

1. **Challenge-based review protocols inflate unsafe counts.**  Any workflow where a human or automated reviewer challenges a safety judge's verdicts will systematically push more items from "safe" to "unsafe" than vice versa.  Teams using such protocols for prevalence estimation should apply a directional correction factor.

2. **Adversaries cannot easily "argue out" violations.**  The permissive flip rates are low (0.4–45.4% even under maximum graduated pressure), meaning it is difficult to persuade a safety judge that flagged content is acceptable.  This is the desirable direction for safety gates.

3. **The bias likely reflects RLHF training incentives.**  Safety-tuned models are trained on objectives where false negatives (missing unsafe content) are penalized more heavily than false positives (over-flagging safe content).  This asymmetry propagates to the conviction axis: models have a lower bar for being convinced that passed content should be flagged than for being convinced that flagged content should be passed.

4. **Model selection should consider directional profiles.**  A model with extreme restrictive bias (Grok-4.1, GPT-5.2: ~0.06× ratio) is appropriate for high-stakes safety gates where missed violations are catastrophic.  A model with more balanced asymmetry (GPT-5, Gemini Pro: ~0.5× ratio) is more appropriate for content moderation pipelines where false positives have meaningful costs (e.g., over-removal of benign content).

5. **The narrowing/widening split matters for multi-round protocols.**  Teams using multi-step review (escalating from mild to strong challenges) should be aware that some models (GPT-5, Grok-4.1 R) become *more balanced* as arguments get stronger, while others (Claude Sonnet, GPT-5.2) become *more biased*.  The latter group's verdicts under strong review pressure will systematically skew toward "unsafe."

### 7.4 Discussion

Experiment 4 demonstrates that directional asymmetry is not a marginal effect but a dominant feature of LLM safety judges.  The universal restrictive bias — present in all nine frontier models under graduated pressure, and in seven of nine under repeated pressure, with ratios ranging from 0.06× to 0.67× — is the most practically actionable finding in this paper.  It connects the Wiggle Framework's measurement methodology to concrete deployment guidance: which models to use for which safety roles, and how to calibrate their verdicts under adversarial conditions.

The distinction between narrowing and widening models (Section 7.2.2) adds a further layer: directional bias is not a fixed property but interacts with pressure type and intensity.  This means that the appropriate model for a given safety pipeline depends not just on its L4 asymmetry ratio but on the structure of the review protocol it will operate within.
