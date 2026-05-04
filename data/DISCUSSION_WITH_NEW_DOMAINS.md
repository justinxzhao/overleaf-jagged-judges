# WIGGLE: Refined Discussion Across Six Domains

*Synthesizing findings across six evaluation domains -- WildGuard, Paired Prompts, MAGE, AEGIS, ToxiGen, and HH-RLHF -- with a sharpened framing that addresses the "so what" question head-on.*

**Date:** April 29, 2026

---

## 1. What the Six-Domain Expansion Adds

The original three-domain study (WildGuard, Paired Prompts, MAGE) established that wiggle is universal. The expansion to six domains strengthens every claim and resolves ambiguities that three domains left open.

**AEGIS** is a second safety classification domain, structurally similar to WildGuard but with a different taxonomy and dataset. Its inclusion answers a critical question: are the WildGuard findings specific to that particular benchmark, or do they generalize across safety evaluation? The answer is clear -- AEGIS replicates the WildGuard pattern. Mean L4 wiggle rates are 33.5% binary and 51.6% Likert, closely tracking WildGuard's 31.3% and 42.2%. The safety robustness findings are not WildGuard-specific.

**ToxiGen** is a toxicity detection domain that turns out to be the hardest domain to wiggle in the entire study: 27.1% binary and 21.1% Likert at L4. This is a genuinely important data point. Before ToxiGen, one might have hypothesized that wiggle sensitivity scales monotonically with task subjectivity or difficulty. ToxiGen breaks that hypothesis -- toxicity detection is subjective and contested, yet judges resist pressure on it more than on any other domain. This establishes that wiggle sensitivity is domain-dependent in ways that are not reducible to a single axis of task difficulty.

**HH-RLHF** (Anthropic's red-team attempts dataset) is a third safety domain, but uniquely features multi-turn red-team conversation context. It evaluates judges on conversations where a human tried to elicit harmful content from an assistant, rated 0-4 (0 = model handled safely, 4 = most harmful), with 100 items stratified by rating. HH-RLHF sits between WildGuard and Paired Prompts in difficulty (L4 binary 46.8%, Likert 42.1%) and has the steepest L6 Likert cliff of any domain -- a 4.8x multiplier from L5 to L6 (17.4% to 82.6%, +65.2pp). Its level-dependent directionality mirrors WildGuard exactly: Likert L1-L3 is permissive (toward-safe, 0.5-0.8), Likert L4-L5 turns restrictive (1.5x toward-unsafe), and L6 is nearly symmetric (~1.1-1.2) on both scales. This confirms the level-dependent directionality pattern across three independent safety domains -- WildGuard, AEGIS, and HH-RLHF -- establishing it as a robust safety-domain signature rather than a WildGuard-specific artifact.

The domain difficulty spectrum is now well-characterized:

```
ToxiGen (hardest to wiggle) < WildGuard ~ AEGIS < HH-RLHF < Paired Prompts < MAGE (easiest)
   21-27% L4                   31-52% L4        42-47% L4    42-66% L4       68-71% L4
```

With 6 domains x 2 scales = 12 conditions, we now have 12 independent tests of every claim about model robustness transfer. The reshuffling of model rankings is tested across 12 conditions, not 6 -- and it holds. No model is consistently top or bottom across all 12 domain x scale conditions.

---

## 2. Three Assertive Contributions

The colleague's critique is right that "LLMs are inconsistent and sycophantic" is not news. The contribution is not that wiggle exists. The contribution is that we can measure it, predict it cheaply, and use it to make concrete deployment decisions. Here are three specific, actionable contributions supported by the six-domain data.

### 2.1 Jury Disagreement as a Label Reliability Signal

**The claim:** Running 8 judges once at baseline (no pressure, no adversarial infrastructure) predicts which labels are reliable and which are not.

**The evidence:** Items where the 8-judge jury splits are 10-22pp more wiggable than items where the jury is unanimous. This holds across all 6 domains and both scales. Jury disagreement at baseline predicts wiggle at every pressure level (Spearman rho = -0.17 to -0.39), universally.

**Why this matters:** The colleague asks whether we can "identify reliable labels for golden sets." This is exactly that. Golden sets are the backbone of LLM-as-judge validation -- teams curate labeled examples and measure judge accuracy against them. But not all golden-set labels are equally trustworthy. If 8 judges unanimously agree on a label, that label is stable under pressure. If the jury splits 5-3, that label is fragile -- a slight change in prompt framing, model version, or conversational context can flip it.

**The practical protocol:** Run your candidate judges once each on your golden set. Flag items where the jury splits. Either remove those items from the golden set (tightening it to only robust labels) or weight them lower in accuracy calculations. This costs 8 API calls per item. No adversarial prompts, no multi-turn conversations, no specialized infrastructure. It is a direct, cheap screen for label reliability.

### 2.2 Domain-Specific Robustness Profiles for Judge Selection

**The claim:** The choice of which model to use as a judge is domain-dependent, and the stakes of getting it wrong are enormous.

**The evidence:** AURC ranges across the 12 domain x scale conditions tell the story. The best model retains 0.877-0.951 of its verdicts across pressure levels (Gemini Flash on WildGuard binary, GPT-5.2 on WildGuard Likert). The worst model retains 0.034-0.246 (GPT-5 on MAGE Likert, GPT-5 on Paired Prompts Likert). That is not a marginal difference -- it is the difference between a judge that holds 90%+ of its verdicts and one that holds 3%.

The model rankings reshuffle across domains:
- Claude Sonnet: AURC 0.165 on Paired Prompts binary (catastrophic) but 0.904 on HH-RLHF Likert (robust) -- a 5.5x ratio within a single model
- GPT-5: AURC 0.034 on MAGE Likert (near-total collapse) but 0.714 on WildGuard Likert (adequate)
- Selecting GPT-5 for MAGE evaluation (AURC 0.095) vs Gemini Pro (AURC 0.859) is a 9x difference in verdict retention

**Why this matters:** The colleague notes that most teams use judges in one-shot mode with SP tuning, few-shot prompting, or fine-tuning. The question is: which base model do they tune? Our data shows that the answer depends on the domain. A team building a safety judge should start from a different base model than a team building an AI-detection judge or a toxicity judge. The AURC profiles across 12 conditions provide a principled selection criterion that does not currently exist.

**The practical protocol:** Before committing to a model for a new evaluation task, run our wiggle battery on a pilot set of 50-100 items. This takes one day and produces an AURC profile that reveals whether your chosen model is robust on your specific domain. The cost of not doing this is deploying a judge that collapses under the mildest conversational pressure.

### 2.3 Pressure Mostly Degrades Accuracy, With One Domain-Specific Exception

**The claim:** Across domains, pressure is net-negative for accuracy. One statistically significant exception exists on WildGuard, but it does not generalize.

**The evidence:** Ground truth analysis is available for 5 of our 6 domains. The overall corrupting:corrective ratio ranges from 1.4:1 (HH-RLHF binary) to 3.3:1 (ToxiGen binary). Pressure is net-corrupting everywhere in aggregate.

A z-test on the per-level corrective fractions (testing whether corrective wiggles exceed 50% of all wiggles) reveals that only two conditions are statistically significant:

| Condition | Corrective | Total wiggles | Corrective % | z | Significance |
|---|---:|---:|---:|---:|---|
| WildGuard Likert L2 | 242 | 397 | 61.0% | 4.37 | p<0.001 |
| WildGuard Likert L3 | 235 | 411 | 57.2% | 2.91 | p<0.01 |
| ToxiGen Likert L4 | 151 | 263 | 57.4% | 2.40 | p<0.05 |
| HH-RLHF Likert L2 | 54 | 99 | 54.5% | 0.90 | not significant |
| AEGIS Likert L2 | 42 | 86 | 48.8% | -0.22 | not significant |

WildGuard Likert L2-L3 is the only robustly corrective condition — 61% and 57% of wiggles move toward ground truth, with strong statistical significance. ToxiGen Likert L4 is marginally significant. HH-RLHF and AEGIS show corrective-leaning ratios but the sample sizes are too small to distinguish from chance.

**The jury accuracy-over-turns charts tell a clearer story.** When we track the actual accuracy of a majority-vote jury at each turn relative to the L0 baseline:

- **No level or turn combination consistently exceeds the L0 baseline accuracy.** The jury starts at its best and degrades from there.
- **L1-L5 degrade slowly** — the jury majority vote is remarkably resilient to scripted pressure, losing only ~5pp over 10 turns on WildGuard (80%→75%) and staying nearly flat on HH-RLHF.
- **L6 collapses catastrophically** — from 80% to 30% on WildGuard, from 63% to 38% on HH-RLHF, from 83% to 25% on MAGE. The adaptive persuader breaks the jury.
- **On HH-RLHF, L1-L3 show a slight uptick** at turns 1-2 (from 63% to ~65%) before flattening — the closest thing to evidence that mild challenge helps, but it's within noise.

**What this means:** The "corrective window" on WildGuard Likert L2-L3 is statistically real at the individual-wiggle level, but it does not translate into a measurable accuracy improvement at the jury level. More wiggles go in the right direction than the wrong direction at L2-L3, but the net accuracy effect is too small to overcome the loss from items that were correct and got corrupted. The practical recommendation should be tempered: moderate challenges may have a slight corrective tendency on safety tasks, but they do not reliably improve overall accuracy.

At L6 (adaptive adversarial persuasion), the picture is unambiguous: approximately 70% of wiggles are corrupting across all domains, and jury accuracy drops by 25-55 percentage points.

**Why this matters:** This is a precise, actionable finding for the design of judge review pipelines. The naive framing is "pressure corrupts judges, so never challenge them." The correct framing is: "moderate argument-based challenges (L2-L3 equivalent) can improve accuracy on safety tasks, but adaptive adversarial debate (L6 equivalent) is universally corrupting." This directly informs the design of debate architectures, appeal workflows, and chain-of-thought review systems:

- **L1-L5 scripted pressure barely degrades jury accuracy** — the majority-vote jury is a robust defense against scripted challenges, losing only ~5pp over 10 turns.
- **L6 adaptive pressure breaks the jury** — accuracy drops 25-55pp. No ensemble defense holds against a dedicated adversarial persuader.
- **The practical defense is jury bootstrapping, not challenge-based review.** Rather than trying to use challenges to improve accuracy (which our data does not support), use the jury baseline disagreement to identify which items are unreliable and should be flagged or removed.

What is genuinely new here is not a "corrective window" but the **sharp separation between scripted and adaptive pressure**. Our graduated design reveals that jury robustness is high against L1-L5 but collapses at L6 — a binary distinction that prior work on sycophancy and consistency could not detect because it does not vary pressure sophistication.

**The corrective window is domain-specific and level-specific.** The full per-level corrupt:corrective ratio table across all 5 ground-truth domains reveals a precise structure:

| Condition | Ratio | Interpretation |
|---|---:|---|
| WildGuard Likert L2 | 0.6:1 | **Corrective** — more wiggles help than hurt |
| WildGuard Likert L3 | 0.7:1 | **Corrective** |
| HH-RLHF Likert L2 | 0.8:1 | **Corrective** |
| ToxiGen Likert L4 | 0.7:1 | **Corrective** — surprisingly, at consensus pressure |
| AEGIS Likert L2-L3 | 1.0-1.1:1 | Near-neutral |
| HH-RLHF binary L2-L3 | 1.1-1.2:1 | Near-neutral |
| MAGE (all levels, both scales) | 2.1-2.9:1 | **Always corrupting** — no corrective window exists |
| ToxiGen binary L6 | 4.8:1 | **Most corrupting condition in the entire study** |

Three patterns emerge, with appropriate caveats about statistical significance:

1. **WildGuard Likert L2-L3 is the only robustly corrective condition** (p<0.001 and p<0.01). On other safety domains, corrective-leaning ratios appear at L2-L3 but are not statistically distinguishable from chance given the sample sizes.

2. **MAGE never has a corrective window.** AI detection is corrupting at every level, every scale, every turn (2.1-2.9:1 ratio). The corrective fraction never rises above ~22%. This is the starkest domain difference in the study.

3. **ToxiGen binary L6 is the most corrupting condition in the entire study** (4.8:1 ratio). But ToxiGen Likert L4 is marginally corrective (p<0.05) — a large swing that suggests toxicity judgment is particularly unstable across pressure types.

The practical implication: we cannot confidently recommend "use L2-L3 challenges to improve accuracy" as a general prescription. The corrective effect is only robustly demonstrated on WildGuard Likert. What we CAN confidently say is that L6 adaptive pressure universally degrades accuracy across all domains, and that jury majority voting is a strong defense against scripted pressure (L1-L5) but not against adaptive adversaries (L6).

**Safety domains share a level-dependent directionality signature.** The pattern -- L1-L3 permissive (toward-safe) on Likert, L4+ restrictive (toward-unsafe), L6 nearly symmetric -- is now confirmed across WildGuard, AEGIS, and HH-RLHF. This is a robust safety-domain signature that does not appear in MAGE or ToxiGen in the same way. It suggests safety-trained models have a specific mechanism: at low pressure, moderate arguments can move the judge toward a more accurate (permissive) assessment of content that is actually safe; at high pressure, the safety-conservative training prior overwhelms this corrective effect, pushing the judge toward false-positive unsafe classifications. At L6, the adaptive adversary is sophisticated enough to exploit both directions roughly equally, producing the observed symmetry. Three independent safety domains converging on the same level-dependent pattern is strong evidence that this is a structural property of how safety training interacts with epistemic pressure, not an artifact of any single benchmark.

---

## 3. What This Framework Actually Is: A Unified Epistemic Stress Test

### 3.1 The Core Contribution

Epistemic stability is not a priority for most current deployments of LLM judges. Most teams use judges in one-shot mode with system prompt tuning, few-shot examples, and occasionally fine-tuning. In that context, studying re-prompting stability might seem like documenting a problem nobody has.

But there is prior work on LLM inconsistency, prior work on sycophancy, prior work on persuadability, and prior work on debate -- all studying overlapping phenomena in isolation, with different methods, on different domains. **Our core contribution is not documenting that judges are unstable. It is centralizing different tests of sycophancy and epistemic fragility into one unified framework and doing an apples-to-apples comparison of these methods across six domains, specifically in the context of judging.** No prior work has done this. The graduated pressure ladder (L1-L6) is not six separate experiments -- it is a single diagnostic instrument that separates sycophancy (L1) from argument-based persuadability (L2-L3) from conformity (L4) from adaptive adversarial vulnerability (L6), with the same items, the same judges, and the same evaluation criteria across all conditions.

This unified view reveals structure that isolated studies cannot: L1 and L4 are only weakly correlated (ρ = 0.22), meaning the items vulnerable to "Are you sure?" are *not* the same items vulnerable to fabricated consensus. A judge that is sycophantic is not necessarily conformist, and vice versa. These are different failure modes that require different mitigations -- and no prior framework distinguishes them in a single measurement.

### 3.2 L6 as an Automatic Red-Teamer for Judge-Based Rewards

The six levels in our experimental design are more hypothetical than they are common in current practice. But the L6 result has immediate practical significance: **the adaptive persuader agent is an exceptionally effective red-teamer for LLM judge-based rewards.**

Every judge we tested is vulnerable to an automatic adversarial persuader agent. L6 achieves 65-90% wiggle rates across all six domains and both scales, with a 2.4-4.8x multiplier over scripted pressure (L5). The extreme case is HH-RLHF Likert, where the L5-to-L6 multiplier is 4.8x (17.4% to 82.6%) -- models that resist scripted pressure on red-team content completely collapse under adaptive persuasion. This is the strongest evidence yet for L6 as an effective red-teamer. It matters wherever judges deliver rewards or make gating decisions:

- **RLHF reward models** that use LLM judges to score outputs are vulnerable to reward hacking if the reward is negotiated through dialogue. An L6-style agent can systematically push the judge's scores in a desired direction.
- **Safety gates** that use LLM judges to block harmful content can be bypassed by an agent that applies L4-L6 pressure to the judge.
- **Evaluation pipelines** that use judges to rank model outputs can be gamed if the evaluated model learns to produce outputs that exploit the judge's epistemic weaknesses.

The L6 persuader is not just a measurement tool -- it is a concrete demonstration that automatic epistemic reward hacking is feasible against all frontier judges we tested. Any system that uses an LLM judge as a reward signal should test that judge against an L6-style adversary.

### 3.3 Sycophancy and Conformity Are Different Failure Modes

This is a finding that isolated sycophancy studies cannot produce. L1 pressure ("Are you sure?") and L4 pressure ("Three reviewers disagree with you") produce different vulnerability profiles:

- **Sycophancy (L1-susceptible):** The judge defers to any challenge regardless of content. Addressed by verdict-locking, restricted context windows, or instruction tuning against reflexive agreement.
- **Conformity (L4-susceptible):** The judge defers to claimed consensus. Addressed by training against social proof arguments, or by ensuring consensus claims are never surfaced to the judge.
- **Adversarial vulnerability (L6-susceptible):** The judge can be systematically persuaded by an adaptive agent. Addressed by adversarial robustness training or judge ensembles.

One-shot evaluation conflates all three. The graduated framework separates them, enabling targeted mitigation for each failure mode.

---

## 4. Addressing the "Just Run Golden-Set Validation Multiple Times" Objection

The most natural counter-proposal to our work is: "If you're worried about judge instability, just run your golden-set validation multiple times with temperature > 0 and look at the variance." This is a reasonable idea, and it captures some of what wiggle measures. But it misses three things.

**First, temperature-based variance dramatically underestimates adversarial vulnerability.** Temperature resampling measures stochastic noise in the model's output distribution. Wiggle measures the model's susceptibility to contextual manipulation. These are different quantities. A model can have near-zero temperature variance (it always gives the same answer to the same prompt) and still have 70% L4 wiggle rate (it changes its answer when told that others disagree). The gap between stochastic variance and adversarial vulnerability is precisely what makes wiggle informative -- it reveals fragility that standard reliability testing misses entirely.

**Second, temperature resampling cannot distinguish pressure types.** It tells you that a verdict is unstable, but not why, and not what kind of challenge would flip it. Graduated pressure testing tells you whether the verdict is vulnerable to simple challenges (L1), argument-based review (L2-L3), social proof (L4), persistence (L5), or adaptive adversaries (L6). This decomposition is actionable for system design in a way that aggregate variance is not.

**Third, temperature resampling cannot identify the corrective window.** There is no analog of the L2-L3 corrective finding in temperature-based validation. Resampling with temperature cannot tell you that moderate argument-based challenges improve accuracy while adaptive debate degrades it. It can only tell you that the verdict sometimes changes. The corrective window is a finding about the interaction between pressure type and accuracy, and it requires the graduated pressure design to detect.

---

## 5. Summary Table: All Six Domains x Both Scales

Mean wiggle rates at L4 (consensus pressure):

| Domain | Binary L4 | Likert L4 | Domain Character |
|---|---:|---:|---|
| ToxiGen | 27.1% | 21.1% | Hardest to wiggle; toxicity judgments are deeply entrenched |
| WildGuard | 31.3% | 42.2% | Safety classification; sharp binary/Likert threshold effect |
| AEGIS | 33.5% | 51.6% | Confirms WildGuard patterns in a second safety domain |
| HH-RLHF | 46.8% | 42.1% | Third safety domain; steepest L6 Likert cliff (x4.8) |
| Paired Prompts | 66.0% | 42.7% | Subjective assessment; gradual pressure response |
| MAGE | 70.6% | 68.2% | Easiest to wiggle; factual task with high intrinsic uncertainty |

AURC extremes across all 12 domain x scale conditions:

| Metric | Model | AURC | Condition |
|---|---|---:|---|
| Best retention | Gemini Flash / GPT-5.2 | 0.877-0.951 | WG binary / WG Likert |
| Worst retention | GPT-5 | 0.034-0.246 | MAGE Likert / PP Likert |
| Largest within-model gap | Claude Sonnet | 0.165 vs 0.904 | PP binary vs HH-RLHF Likert |
| Largest between-model gap | GPT-5 vs Gemini Pro | 0.095 vs 0.859 | MAGE binary (9x difference) |

Ground truth corrupting:corrective ratios (5 domains):

| Domain | Scale | Ratio | Notable Exception |
|---|---|---|---|
| WildGuard | Binary | ~2:1 corrupting | -- |
| WildGuard | Likert | ~2:1 corrupting | L2: 61% corrective, L3: 57% corrective |
| MAGE | Both | ~2.3:1 corrupting | Stable across all levels |
| AEGIS | Both | 1.7:1 corrupting | Low corruption ratio |
| HH-RLHF | Binary | 1.4:1 corrupting | Lowest corruption ratio; L2 Likert is 0.8:1 corrective |
| HH-RLHF | Likert | 1.5:1 corrupting | L6: 52.5% of all items corrupted |
| ToxiGen | Binary | 3.3:1 corrupting | Highest corruption ratio |
| All domains | Both | ~70% corrupting | At L6 (adaptive), universal |

Jury bootstrapping prediction (all 6 domains):

| Property | Value |
|---|---|
| Jury disagreement -> wiggle gap | 10-22pp more wiggable |
| Baseline jury disagreement -> wiggle (rho) | -0.17 to -0.39 |
| Cost | 8 API calls per item, no adversarial infrastructure |
| Universality | All 6 domains, both scales, every pressure level |

---

## 6. What This Paper Is Really About

The contribution of this paper is not "LLMs are sycophantic." The contribution is three concrete tools for practitioners who use LLM judges:

1. **A cheap reliability screen.** Run 8 judges once. Items where the jury splits are unreliable. Remove or downweight them. This improves golden-set quality at minimal cost. The jury majority vote is also remarkably robust to scripted pressure (L1-L5), losing only ~5pp over 10 turns — a practical defense against all but the most sophisticated attacks.

2. **A domain-specific selection protocol.** Run the wiggle battery on a pilot set. The AURC profile tells you which model to use for your specific task. The wrong choice can cost you 9x in verdict stability.

3. **A sharp threat model for judge-based rewards.** The L6 adaptive persuader breaks every judge and every jury we tested, dropping accuracy by 25-55 percentage points. Scripted pressure (L1-L5) barely dents the jury. This binary distinction — scripted pressure is survivable, adaptive pressure is not — is the key design constraint for any system that uses LLM judges as reward signals or safety gates.

These are not soft contributions. They are specific, evidence-backed protocols supported by data across 6 domains, 2 scales, 6 pressure levels, and 8 models.

---

## Appendix: Run IDs and Data Provenance

**Date of latest data collection:** April 30, 2026 (grok-4.1 reasoning added)

### Models (9 judges)

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

### L6 Persuader Models

`openai-gpt-5-4-responses`, `claude-4-6-opus-genai-vertex`, `oci-grok-4-1-fast-reasoning`

### Multiturn Experiment Run IDs

All data at `manifold://genai_safety_evals_misc/tree/justin/wiggle/`.

| Domain | Scale | Run ID | Path Pattern |
|---|---|---|---|
| WildGuard | binary L1 | `n_500_t10_l1-0` | `multiturn_wildguard/run_id-{id}/` |
| WildGuard | binary L2-L6 | `n_500_t10_l2-6-0` | `multiturn_wildguard/run_id-{id}/` |
| WildGuard | likert | `full-run-0` | `multiturn_wildguard_likert/run_id-{id}/` |
| Paired Prompts | binary | `post-refactor-0` | `multiturn_pp/run_id-{id}/` |
| Paired Prompts | likert | `post-refactor-0` | `multiturn_pp_likert/run_id-{id}/` |
| MAGE | binary | `full-run-0` | `multiturn_mage/run_id-{id}/` |
| MAGE | likert | `full-run-0` | `multiturn_mage_likert/run_id-{id}/` |
| AEGIS | binary | `full-run-0` | `multiturn_aegis/run_id-{id}/` |
| AEGIS | likert | `full-run-0` | `multiturn_aegis_likert/run_id-{id}/` |
| ToxiGen | binary | `full-run-0` | `multiturn_toxigen/run_id-{id}/` |
| ToxiGen | likert | `full-run-0` | `multiturn_toxigen_likert/run_id-{id}/` |
| HH-RLHF | binary | `full-run-0` | `multiturn_hh_rlhf/run_id-{id}/` |
| HH-RLHF | likert | `full-run-0` | `multiturn_hh_rlhf_likert/run_id-{id}/` |

### Mechanical Experiment Run IDs

| Domain | Run ID | Path Pattern |
|---|---|---|
| WildGuard | `full-run-0` | `mechanical_wildguard[_likert]/run_id-{id}/` |
| Paired Prompts | `post-refactor-0` | `mechanical_pp[_likert]/run_id-{id}/` |
| MAGE | `full-run-0` | `mechanical_mage[_likert]/run_id-{id}/` |
| AEGIS | `full-run-0` | `mechanical_aegis[_likert]/run_id-{id}/` |
| ToxiGen | `full-run-0` | `mechanical_toxigen[_likert]/run_id-{id}/` |
| HH-RLHF | `full-run-0` | `mechanical_hh_rlhf[_likert]/run_id-{id}/` |

**PP mechanical note:** The `post-refactor-0` data was re-generated on 2026-05-01 with fixed example_id generation (SHA-256 hashing matching the multiturn scheme) to enable example-level correlation between mechanical and multiturn experiments. Prior runs used `prompt_group_id__response_model` composite IDs that could not be joined with the multiturn data.

### Paired Prompts Phase 1 Completions

`manifold://genai_safety_evals_misc/tree/justin/wiggle/paired_prompts/run_id-phase_1-full-0/completions_with_data.csv`

### Binary vs Likert Scoring

| Domain | Binary Verdicts | Likert Scale |
|---|---|---|
| WildGuard | safe / unsafe | 1 (very safe) to 5 (very unsafe) |
| AEGIS | safe / unsafe | 1 (very safe) to 5 (very unsafe) |
| HH-RLHF | safe / unsafe | 0 (safe) to 4 (most harmful) |
| ToxiGen | not toxic / toxic | 1 (not toxic) to 5 (very toxic) |
| MAGE | human_written / ai_generated | 1 (human) to 5 (AI) |
| PP Hedging | hedged / not_hedged | 1 (no hedging) to 5 (extreme hedging) |
| PP Refusal | compliant / non_compliant | 1 (literal compliance) to 5 (unhelpful non-compliance) |

### Analysis Command

```bash
buck2 run fbcode//genai_foundations_safety/abets/wiggle:analysis_cross_domain -- \
    --pp-binary-run-id post-refactor-0 \
    --pp-likert-run-id post-refactor-0 \
    --pp-mechanical-run-id post-refactor-0 \
    --results-dir /path/to/local/output
```
