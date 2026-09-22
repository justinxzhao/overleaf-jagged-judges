#!/usr/bin/env python3
"""Recompute revision metrics from archived Wiggle trajectory summaries.

This script intentionally makes no model calls. It resolves three manuscript
ambiguities using the cached item-level outputs:

* L6 expected single-persuader wiggle versus three-persuader union coverage.
* Ground-truth outcomes under the implemented Likert boundary-crossing rule.
* In-sample versus held-out jury-majority diagnostics.
"""

from __future__ import annotations

import csv
import itertools
import json
import math
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from plot_domains_and_survival_by_scale import LEVELS, load_all_records


ROOT = Path(__file__).resolve().parents[2]
TABLE_DIR = ROOT / "data" / "analysis_cross_domain" / "tables" / "revision"
FIGURE_DIR = ROOT / "data" / "analysis_cross_domain" / "pdf"

SHORT_NAMES = {
    "oci-grok-4-1-fast-reasoning": "Grok-R",
    "oci-grok-4-1-fast-non-reasoning": "Grok",
    "claude-4-6-sonnet-genai-vertex": "C.Son",
    "claude-4-6-opus-genai-vertex": "C.Opus",
    "gpt-5-chatgpt": "GPT-5",
    "openai-gpt-5-2-responses": "GPT-5.2",
    "openai-gpt-5-4-responses": "GPT-5.4",
    "gemini-3-flash-preview-genai": "G.Flash",
    "gemini-3-1-pro-preview-genai": "G.Pro",
}

DISPLAY_NAMES = {
    "Grok-R": "Grok 4.1 R",
    "Grok": "Grok 4.1",
    "C.Son": "Claude 4.6 Sonnet",
    "C.Opus": "Claude 4.6 Opus",
    "GPT-5": "GPT-5",
    "GPT-5.2": "GPT-5.2",
    "GPT-5.4": "GPT-5.4",
    "G.Flash": "Gemini 3 Flash",
    "G.Pro": "Gemini 3.1 Pro",
}

FAMILIES = {
    "oci-grok-4-1-fast-reasoning": "xAI",
    "oci-grok-4-1-fast-non-reasoning": "xAI",
    "claude-4-6-sonnet-genai-vertex": "Anthropic",
    "claude-4-6-opus-genai-vertex": "Anthropic",
    "gpt-5-chatgpt": "OpenAI",
    "openai-gpt-5-2-responses": "OpenAI",
    "openai-gpt-5-4-responses": "OpenAI",
    "gemini-3-flash-preview-genai": "Google",
    "gemini-3-1-pro-preview-genai": "Google",
}

TASK_ORDER = [
    "WildGuard",
    "AEGIS",
    "HH-RLHF",
    "ToxiGen",
    "PP Hedging",
    "PP Refusal",
    "MAGE",
]
SAMPLE_SIZES = {
    "WildGuard": 384,
    "AEGIS": 100,
    "HH-RLHF": 100,
    "ToxiGen": 100,
    # Each Paired Prompts rubric contains 50 pairs, i.e. 100 prompt instances.
    "PP Hedging": 100,
    "PP Refusal": 100,
    "MAGE": 100,
}


def read_truth() -> dict[tuple[str, str], tuple[bool, str]]:
    """Return (high-pole truth, binary truth label) by task and example."""

    specs = [
        (
            "WildGuard",
            ROOT
            / "data/data_cache/multiturn_wildguard/run_id-n_500_t10_l2-6-0/pilot_sample.csv",
            lambda row: row["response_harm_label"] == "harmful",
            ("safe", "unsafe"),
        ),
        (
            "AEGIS",
            ROOT / "data/data_cache/multiturn_aegis/run_id-full-run-0/pilot_sample.csv",
            lambda row: row["response_label"] == "unsafe",
            ("safe", "unsafe"),
        ),
        (
            "HH-RLHF",
            ROOT
            / "data/data_cache/multiturn_hh_rlhf/run_id-full-run-0/pilot_sample.csv",
            lambda row: int(row["rating"]) >= 2,
            ("safe", "unsafe"),
        ),
        (
            "ToxiGen",
            ROOT
            / "data/data_cache/multiturn_toxigen/run_id-full-run-0/pilot_sample.csv",
            lambda row: float(row["toxicity_human"]) >= 3.0,
            ("not toxic", "toxic"),
        ),
        (
            "MAGE",
            ROOT / "data/data_cache/multiturn_mage/run_id-full-run-0/pilot_sample.csv",
            # In the archived MAGE sample, label 0 is machine-generated and
            # label 1 is human-written (also visible in the `src` suffixes).
            lambda row: row["label"] == "0",
            ("human_written", "ai_generated"),
        ),
    ]
    truth: dict[tuple[str, str], tuple[bool, str]] = {}
    for task, path, is_high, labels in specs:
        with path.open(newline="") as handle:
            for row in csv.DictReader(handle):
                high = bool(is_high(row))
                truth[(task, row["example_id"])] = (high, labels[int(high)])
    return truth


def pearson(xs: list[float], ys: list[float]) -> float:
    x = np.asarray(xs, dtype=float)
    y = np.asarray(ys, dtype=float)
    if len(x) < 2 or np.std(x) == 0 or np.std(y) == 0:
        return math.nan
    return float(np.corrcoef(x, y)[0, 1])


def rank_average(values: list[float]) -> np.ndarray:
    series = pd.Series(values, dtype=float)
    return series.rank(method="average").to_numpy(dtype=float)


def spearman(xs: list[float], ys: list[float]) -> float:
    return pearson(rank_average(xs).tolist(), rank_average(ys).tolist())


def prepare_records() -> pd.DataFrame:
    records = load_all_records()
    records["short_name"] = records["judge"].map(SHORT_NAMES)
    if records["short_name"].isna().any():
        missing = sorted(records.loc[records["short_name"].isna(), "judge"].unique())
        raise ValueError(f"Missing short-name mapping: {missing}")
    return records


def l6_tables(records: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    l6 = records[records["level"] == "L6"].copy()
    expected = (
        l6.groupby(["task", "scale", "judge", "short_name"], as_index=False)[
            "changed"
        ]
        .mean()
        .rename(columns={"changed": "mean_per_persuader"})
    )
    union = (
        l6.groupby(
            ["task", "scale", "judge", "short_name", "example_id"],
            as_index=False,
        )["changed"]
        .max()
        .groupby(["task", "scale", "judge", "short_name"], as_index=False)[
            "changed"
        ]
        .mean()
        .rename(columns={"changed": "union_coverage"})
    )
    model = expected.merge(
        union, on=["task", "scale", "judge", "short_name"], validate="one_to_one"
    )
    task = (
        model.groupby(["task", "scale"], as_index=False)[
            ["mean_per_persuader", "union_coverage"]
        ]
        .mean()
    )
    return task, model


def add_truth_states(records: pd.DataFrame) -> pd.DataFrame:
    truth = read_truth()
    data = records[records["task"].isin({"WildGuard", "AEGIS", "HH-RLHF", "ToxiGen", "MAGE"})].copy()
    data["truth_high"] = [truth[(task, item)][0] for task, item in zip(data["task"], data["example_id"])]
    data["truth_label"] = [truth[(task, item)][1] for task, item in zip(data["task"], data["example_id"])]
    data["initial_state"] = pd.NA
    data["outcome"] = pd.NA

    binary = data["scale"] == "binary"
    has_labels = binary & data["l0"].notna() & data["observed"].notna()
    initial_correct = data.loc[has_labels, "l0"].astype(str).eq(
        data.loc[has_labels, "truth_label"].astype(str)
    )
    data.loc[has_labels, "initial_state"] = np.where(
        initial_correct, "correct", "incorrect"
    )
    final_correct = data.loc[has_labels, "observed"].astype(str).eq(
        data.loc[has_labels, "truth_label"].astype(str)
    )
    data.loc[has_labels, "baseline_correct"] = initial_correct.astype(float)
    data.loc[has_labels, "final_correct"] = final_correct.astype(float)
    changed_binary = has_labels & data["changed"]
    data.loc[changed_binary, "outcome"] = np.where(
        data.loc[changed_binary, "initial_state"].eq("correct"),
        "corrupting",
        "corrective",
    )

    likert = data["scale"] == "likert"
    l0 = pd.to_numeric(data.loc[likert, "l0"], errors="coerce")
    observed = pd.to_numeric(data.loc[likert, "observed"], errors="coerce")
    high = data.loc[likert, "truth_high"].astype(bool)
    aligned = (high & (l0 >= 4)) | (~high & (l0 <= 2))
    misaligned = (high & (l0 <= 2)) | (~high & (l0 >= 4))
    states = np.where(aligned, "aligned", np.where(misaligned, "misaligned", "midpoint"))
    data.loc[likert, "initial_state"] = states
    changed_likert_index = data.index[likert & data["changed"]]
    for index in changed_likert_index:
        toward_high = float(data.at[index, "observed"]) > float(data.at[index, "l0"])
        corrective = toward_high == bool(data.at[index, "truth_high"])
        data.at[index, "outcome"] = "corrective" if corrective else "corrupting"
    return data


def conditional_tables(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    usable = data[data["initial_state"].notna()].copy()
    task = (
        usable.groupby(["task", "scale", "level", "initial_state"], as_index=False)
        .agg(n=("changed", "size"), wiggles=("changed", "sum"), wiggle_rate=("changed", "mean"))
    )
    macro = (
        task.groupby(["scale", "level", "initial_state"], as_index=False)
        .agg(tasks=("task", "nunique"), mean_wiggle_rate=("wiggle_rate", "mean"))
    )

    binary = usable[(usable["scale"] == "binary") & usable["baseline_correct"].notna()].copy()
    accuracy = (
        binary.groupby(["task", "level"], as_index=False)
        .agg(
            n=("changed", "size"),
            baseline_accuracy=("baseline_correct", "mean"),
            final_accuracy=("final_correct", "mean"),
        )
    )
    accuracy["accuracy_change"] = accuracy["final_accuracy"] - accuracy["baseline_accuracy"]
    return task, macro, accuracy


def outcome_table(data: pd.DataFrame) -> pd.DataFrame:
    outcomes = data[data["changed"] & data["outcome"].notna()].copy()
    grouped = (
        outcomes.groupby(["task", "scale", "level", "outcome"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    # The compact WildGuard binary L6 archive lacks trajectory-specific labels;
    # use the archived direction counts for this single descriptive cell.
    archived = pd.read_csv(
        ROOT / "data/analysis_cross_domain/tables/ground_truth/ground_truth.csv"
    )
    row = archived[
        (archived["domain"] == "WildGuard")
        & (archived["scale"] == "binary")
        & (archived["level"] == "L6")
    ].iloc[0]
    grouped = pd.concat(
        [
            grouped,
            pd.DataFrame(
                [
                    {
                        "task": "WildGuard",
                        "scale": "binary",
                        "level": "L6",
                        "corrective": int(row["corrective"]),
                        "corrupting": int(row["corrupting"]),
                    }
                ]
            ),
        ],
        ignore_index=True,
    )
    for column in ["corrective", "corrupting"]:
        if column not in grouped:
            grouped[column] = 0
        grouped[column] = grouped[column].fillna(0).astype(int)
    grouped["total_wiggles"] = grouped["corrective"] + grouped["corrupting"]
    grouped["corrective_pct"] = grouped["corrective"] / grouped["total_wiggles"]
    grouped["corrupting_pct"] = grouped["corrupting"] / grouped["total_wiggles"]
    return grouped.sort_values(["task", "scale", "level"])


def model_retention_tables(
    l6_model: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    detail = pd.read_csv(
        ROOT / "data/analysis_cross_domain/tables/wiggliness/detail.csv"
    )
    detail = detail[detail["level"] != "L6"].copy()
    detail["short_name"] = detail["judge_model"].map(SHORT_NAMES)
    revised_l6 = l6_model.rename(columns={"mean_per_persuader": "wiggle_rate"})[
        ["judge", "short_name", "task", "scale", "wiggle_rate"]
    ].rename(columns={"judge": "judge_model", "task": "domain"})
    revised_l6["level"] = "L6"
    rates = pd.concat(
        [
            detail[
                ["judge_model", "short_name", "domain", "scale", "level", "wiggle_rate"]
            ],
            revised_l6[
                ["judge_model", "short_name", "domain", "scale", "level", "wiggle_rate"]
            ],
        ],
        ignore_index=True,
    )
    retention = (
        rates.groupby(["domain", "scale", "short_name"], as_index=False)[
            "wiggle_rate"
        ]
        .mean()
        .assign(retention_rate=lambda frame: 1 - frame["wiggle_rate"])
    )

    l6_task, _ = l6_tables(prepare_records())
    task_rates = (
        rates.groupby(["domain", "scale", "level"], as_index=False)["wiggle_rate"]
        .mean()
    )
    summaries = []
    for (task, scale), group in retention.groupby(["domain", "scale"]):
        best = group.loc[group["retention_rate"].idxmax()]
        worst = group.loc[group["retention_rate"].idxmin()]
        lookup = task_rates[(task_rates["domain"] == task) & (task_rates["scale"] == scale)].set_index("level")["wiggle_rate"]
        union = l6_model[(l6_model["task"] == task) & (l6_model["scale"] == scale)]["union_coverage"].mean()
        summaries.append(
            {
                "task": task,
                "scale": scale,
                "L1": lookup["L1"],
                "L4": lookup["L4"],
                "L6_mean": lookup["L6"],
                "L6_union": union,
                "most_robust": best["short_name"],
                "most_robust_retention": best["retention_rate"],
                "most_fragile": worst["short_name"],
                "most_fragile_retention": worst["retention_rate"],
            }
        )
    return rates, retention, pd.DataFrame(summaries)


def jaggedness_sensitivity(rates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for level in LEVELS:
        raw_means, raw_sds, logit_means, logit_sds = [], [], [], []
        for _, group in rates[rates["level"] == level].groupby("short_name"):
            raw = group["wiggle_rate"].to_numpy(dtype=float)
            logits = []
            for item in group.itertuples():
                # L6 mean rates pool three separate persuader trajectories.
                n = SAMPLE_SIZES[item.domain] * (3 if item.level == "L6" else 1)
                adjusted = (item.wiggle_rate * n + 0.5) / (n + 1)
                logits.append(math.log(adjusted / (1 - adjusted)))
            raw_means.append(float(np.mean(raw)))
            raw_sds.append(float(np.std(raw, ddof=1)))
            logit_means.append(float(np.mean(logits)))
            logit_sds.append(float(np.std(logits, ddof=1)))
        rows.append(
            {
                "level": level,
                "raw_r": pearson(raw_means, raw_sds),
                "empirical_logit_r": pearson(logit_means, logit_sds),
            }
        )
    return pd.DataFrame(rows)


def majority_strength(values: tuple[str, ...]) -> float:
    return max(Counter(values).values()) / len(values)


def jury_holdout(records: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (task, scale), task_records in records.groupby(["task", "scale"]):
        baseline = task_records[task_records["level"] == "L1"].pivot_table(
            index="example_id", columns="judge", values="l0", aggfunc="first"
        )
        judges = sorted(baseline.columns)
        for level in LEVELS:
            outcomes = task_records[task_records["level"] == level].pivot_table(
                index="example_id", columns="judge", values="changed", aggfunc="mean"
            )
            common_items = baseline.index.intersection(outcomes.index)
            for target in judges:
                others = [judge for judge in judges if judge != target]
                y = outcomes.loc[common_items, target].astype(float).tolist()
                for size in [3, 5, 8]:
                    correlations = []
                    for panel in itertools.combinations(others, size):
                        x = [
                            majority_strength(tuple(str(value) for value in row))
                            for row in baseline.loc[common_items, list(panel)].itertuples(
                                index=False, name=None
                            )
                        ]
                        value = spearman(x, y)
                        if not math.isnan(value):
                            correlations.append(abs(value))
                    if correlations:
                        rows.append(
                            {
                                "task": task,
                                "scale": scale,
                                "level": level,
                                "target_judge": SHORT_NAMES[target],
                                "panel_size": size,
                                "mean_abs_rho": float(np.mean(correlations)),
                            }
                        )
    detail = pd.DataFrame(rows)
    summary = (
        detail.groupby("panel_size", as_index=False)
        .agg(
            mean_abs_rho=("mean_abs_rho", "mean"),
            median_abs_rho=("mean_abs_rho", "median"),
            cells=("mean_abs_rho", "size"),
        )
    )
    detail.to_csv(TABLE_DIR / "jury_holdout_detail.csv", index=False)
    return summary


def out_of_family_l6(records: pd.DataFrame) -> pd.DataFrame:
    l6 = records[records["level"] == "L6"].copy()
    l6["judge_family"] = l6["judge"].map(FAMILIES)
    l6["persuader_family"] = l6["persuader"].map(FAMILIES)
    rows = []
    for (judge, short), group in l6.groupby(["judge", "short_name"]):
        rows.append(
            {
                "judge": short,
                "all_persuaders": group["changed"].mean(),
                "out_of_family": group.loc[
                    group["judge_family"] != group["persuader_family"], "changed"
                ].mean(),
                "same_family": group.loc[
                    group["judge_family"] == group["persuader_family"], "changed"
                ].mean(),
            }
        )
    return pd.DataFrame(rows)


def plot_framework_summary(rates: pd.DataFrame) -> pd.DataFrame:
    old = pd.read_csv(
        ROOT
        / "data/analysis_cross_domain/tables/wiggle_rates/wiggle_framework_summary.csv"
    )
    multi = (
        rates.groupby("short_name", as_index=False)["wiggle_rate"]
        .mean()
        .rename(columns={"wiggle_rate": "multi_turn"})
    )
    old["short_name"] = old["model"].map(
        {value: key for key, value in DISPLAY_NAMES.items()}
    )
    revised = old.drop(columns=["multi_turn", "multi_turn_ci_lo", "multi_turn_ci_hi"]).merge(
        multi, on="short_name", validate="one_to_one"
    )

    rng = np.random.default_rng(42)
    ci_rows = []
    for short, group in rates.groupby("short_name"):
        task_means = group.groupby(["domain", "scale"])["wiggle_rate"].mean().to_numpy()
        boot = rng.choice(task_means, size=(4000, len(task_means)), replace=True).mean(axis=1)
        lo, hi = np.quantile(boot, [0.025, 0.975])
        ci_rows.append((short, lo, hi))
    ci = pd.DataFrame(ci_rows, columns=["short_name", "multi_turn_ci_lo", "multi_turn_ci_hi"])
    revised = revised.merge(ci, on="short_name", validate="one_to_one")

    labels = revised["model"].tolist()
    x = np.arange(len(labels))
    width = 0.24
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    colors = {"mechanical": "#66c2a5", "single_turn": "#fc8d62", "multi_turn": "#8da0cb"}
    names = {"mechanical": "Mechanical", "single_turn": "Single-Turn", "multi_turn": "Multi-Turn (10)"}
    for offset, metric in zip([-width, 0, width], ["mechanical", "single_turn", "multi_turn"]):
        y = revised[metric].to_numpy()
        lo = revised[f"{metric}_ci_lo"].to_numpy()
        hi = revised[f"{metric}_ci_hi"].to_numpy()
        ax.bar(x + offset, y, width, color=colors[metric], label=names[metric])
        ax.errorbar(x + offset, y, yerr=np.vstack([y - lo, hi - y]), fmt="none", ecolor="black", capsize=3, linewidth=1)
    ax.set_ylabel("Wiggle Rate")
    highest_ci = revised[
        ["mechanical_ci_hi", "single_turn_ci_hi", "multi_turn_ci_hi"]
    ].to_numpy().max()
    y_max = max(0.65, math.ceil((highest_ci + 0.05) * 20) / 20)
    ax.set_ylim(0, y_max)
    ax.set_xticks(x, labels, rotation=25, ha="right")
    ax.grid(axis="y", alpha=0.2)
    ax.set_axisbelow(True)
    ax.legend(loc="upper right")
    fig.tight_layout()
    output = FIGURE_DIR / "wiggle_rates" / "wiggle_framework_summary.pdf"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)
    return revised


def plot_direction_and_outcomes(outcomes: pd.DataFrame) -> None:
    direction = pd.read_csv(
        ROOT
        / "data/analysis_cross_domain/tables/survival/restrictiveness_direction.csv"
    )
    direction["restrictive_flips"] = direction["toward_restrictive"] * direction["n_flips"]
    pooled_direction = (
        direction.groupby(["scale", "level"], as_index=False)
        .agg(restrictive_flips=("restrictive_flips", "sum"), flips=("n_flips", "sum"))
    )
    pooled_direction["restrictive_fraction"] = pooled_direction["restrictive_flips"] / pooled_direction["flips"]

    pooled_outcomes = outcomes.groupby("level", as_index=False)[["corrective", "corrupting"]].sum()
    pooled_outcomes["corrective_fraction"] = pooled_outcomes["corrective"] / (
        pooled_outcomes["corrective"] + pooled_outcomes["corrupting"]
    )

    x = np.arange(len(LEVELS))
    width = 0.36
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.2))
    for offset, scale, color in [(-width / 2, "binary", "#4c78a8"), (width / 2, "likert", "#f58518")]:
        values = pooled_direction.set_index(["scale", "level"]).loc[
            [(scale, level) for level in LEVELS], "restrictive_fraction"
        ].to_numpy()
        axes[0].bar(x + offset, values, width, label=scale.title(), color=color)
    axes[0].axhline(0.5, color="#777777", linestyle="--", linewidth=1)
    axes[0].set_title("Direction of qualifying wiggles")
    axes[0].set_ylabel("Fraction toward restrictive pole")
    axes[0].set_xticks(x, LEVELS)
    axes[0].set_ylim(0, 1)
    axes[0].legend()

    corrected = pooled_outcomes.set_index("level").loc[LEVELS, "corrective_fraction"].to_numpy()
    axes[1].bar(x, corrected, color="#59a14f", label="Corrective")
    axes[1].bar(x, 1 - corrected, bottom=corrected, color="#e15759", label="Corrupting")
    axes[1].axhline(0.5, color="#777777", linestyle="--", linewidth=1)
    axes[1].set_title("Ground-truth direction of qualifying wiggles")
    axes[1].set_ylabel("Fraction of wiggles")
    axes[1].set_xticks(x, LEVELS)
    axes[1].set_ylim(0, 1)
    axes[1].legend()
    for axis in axes:
        axis.grid(axis="y", alpha=0.18)
        axis.set_axisbelow(True)
    fig.tight_layout()
    output = FIGURE_DIR / "combined" / "direction_and_outcomes.pdf"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def plot_jaggedness(rates: pd.DataFrame) -> None:
    colors = {
        "Grok-R": "#1f77b4",
        "Grok": "#ff7f0e",
        "C.Son": "#2ca02c",
        "C.Opus": "#d62728",
        "GPT-5": "#8c564b",
        "GPT-5.2": "#e377c2",
        "GPT-5.4": "#7f7f7f",
        "G.Flash": "#bcbd22",
        "G.Pro": "#17becf",
    }
    titles = {
        "L1": "Are You Sure?",
        "L2": "Counter-Argument",
        "L3": "Expert Authority",
        "L4": "Consensus Pressure",
        "L5": "Strategy Cycling",
        "L6": "Adaptive Persuader",
    }
    fig, axes = plt.subplots(2, 3, figsize=(12.5, 7.2))
    for level, axis in zip(LEVELS, axes.flat):
        points = []
        for short, group in rates[rates["level"] == level].groupby("short_name"):
            points.append(
                {
                    "short": short,
                    "mean": group["wiggle_rate"].mean(),
                    "sd": group["wiggle_rate"].std(ddof=1),
                }
            )
        frame = pd.DataFrame(points)
        for item in frame.itertuples():
            axis.scatter(item.mean, item.sd, color=colors[item.short], s=34, label=item.short)
        slope, intercept = np.polyfit(frame["mean"], frame["sd"], 1)
        xs = np.linspace(0, 1, 100)
        axis.plot(xs, slope * xs + intercept, color="#e15759", linestyle="--", linewidth=1.5)
        r = pearson(frame["mean"].tolist(), frame["sd"].tolist())
        axis.text(
            0.97,
            0.94,
            rf"$R^2 = {r*r:.2f}$  ($r = {r:+.2f}$)",
            ha="right",
            va="top",
            transform=axis.transAxes,
            fontsize=9,
        )
        axis.set_title(f"{level} - {titles[level]}")
        axis.set_xlim(0, 1)
        axis.set_ylim(bottom=0)
        axis.grid(alpha=0.18)
    for axis in axes[:, 0]:
        axis.set_ylabel("Cross-Task SD")
    for axis in axes[1, :]:
        axis.set_xlabel("Mean Wiggle Rate")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.subplots_adjust(top=0.84, bottom=0.10, hspace=0.34, wspace=0.28)
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.985),
        ncol=5,
        frameon=False,
    )
    output = FIGURE_DIR / "wiggliness" / "per_level_scatter_combined.pdf"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    records = prepare_records()
    l6_task, l6_model = l6_tables(records)
    truth_records = add_truth_states(records)
    conditional_task, conditional_summary, accuracy = conditional_tables(truth_records)
    outcomes = outcome_table(truth_records)
    pooled_outcomes = outcomes.groupby("level", as_index=False)[
        ["corrective", "corrupting"]
    ].sum()
    pooled_outcomes["total_wiggles"] = (
        pooled_outcomes["corrective"] + pooled_outcomes["corrupting"]
    )
    pooled_outcomes["corrective_pct"] = (
        pooled_outcomes["corrective"] / pooled_outcomes["total_wiggles"]
    )
    pooled_outcomes["corrupting_pct"] = (
        pooled_outcomes["corrupting"] / pooled_outcomes["total_wiggles"]
    )
    accuracy_summary = accuracy.groupby("level", as_index=False).agg(
        tasks=("task", "nunique"),
        mean_baseline_accuracy=("baseline_accuracy", "mean"),
        mean_final_accuracy=("final_accuracy", "mean"),
        mean_accuracy_change=("accuracy_change", "mean"),
    )
    rates, retention, task_summary = model_retention_tables(l6_model)
    jaggedness = jaggedness_sensitivity(rates)
    jury = jury_holdout(records)
    family = out_of_family_l6(records)

    if not (l6_task["mean_per_persuader"] <= l6_task["union_coverage"]).all():
        raise AssertionError("L6 union coverage must dominate mean-per-persuader rate")
    binary_conditional = conditional_summary[
        conditional_summary["scale"] == "binary"
    ].pivot(index="level", columns="initial_state", values="mean_wiggle_rate")
    if not (binary_conditional["incorrect"] > binary_conditional["correct"]).all():
        raise AssertionError("Expected incorrect Binary L0 verdicts to be more flippable")
    if set(jury["panel_size"]) != {3, 5, 8}:
        raise AssertionError("Held-out jury summary is missing a panel size")
    framework = plot_framework_summary(rates)
    # Figure 5 retains the paper's original diverging lollipop visualization.
    # Its source artifact is intentionally not overwritten by this recomputation.
    plot_jaggedness(rates)

    outputs = {
        "l6_task_rates.csv": l6_task,
        "l6_model_rates.csv": l6_model,
        "conditional_flip_rates.csv": conditional_task,
        "conditional_flip_summary.csv": conditional_summary,
        "binary_accuracy_changes.csv": accuracy,
        "corrected_ground_truth_outcomes.csv": outcomes,
        "pooled_ground_truth_outcomes.csv": pooled_outcomes,
        "binary_accuracy_summary.csv": accuracy_summary,
        "revised_level_rates.csv": rates,
        "revised_model_retention.csv": retention,
        "revised_task_summary.csv": task_summary,
        "jaggedness_sensitivity.csv": jaggedness,
        "jury_holdout_summary.csv": jury,
        "l6_family_normalization.csv": family,
        "revised_wiggle_framework_summary.csv": framework,
    }
    for filename, frame in outputs.items():
        frame.to_csv(TABLE_DIR / filename, index=False)

    headline = {
        "L4_task_range": [
            float(task_summary["L4"].min()),
            float(task_summary["L4"].max()),
        ],
        "L6_mean_task_range": [
            float(task_summary["L6_mean"].min()),
            float(task_summary["L6_mean"].max()),
        ],
        "L6_union_task_range": [
            float(task_summary["L6_union"].min()),
            float(task_summary["L6_union"].max()),
        ],
    }
    (TABLE_DIR / "headline_summary.json").write_text(
        json.dumps(headline, indent=2) + "\n"
    )
    print(json.dumps(headline, indent=2))


if __name__ == "__main__":
    main()
