#!/usr/bin/env python3
"""Build a self-contained HTML viewer for the Wiggle Framework multi-turn (L1-L6) data.

Joins per-item content + pre-generated pressure arguments (``pilot_sample.csv``) with
per-(level, model) verdict outcomes (``summary.csv``) and embeds everything as one JSON
blob inside ``wiggle_viewer.html`` -- a single file that opens by double-click, no server.

Modeled on the existing ``wokeness_benchmark_viewer.html``. Scope: the multi-turn pressure
ladder only (L1-L6); per item the centerpiece is a model x level matrix of verdicts with
wiggles (flips vs the L0 baseline) highlighted.

Usage:  python3 build_wiggle_viewer.py
"""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "data" / "data_cache"
OUT = ROOT / "wiggle_viewer.html"

csv.field_size_limit(10_000_000)

# ----------------------------------------------------------------------------
# Models
# ----------------------------------------------------------------------------
# raw on-disk dir name -> clean display label (both claude-4-5/4-6 legacy dir
# names map to the 4.6 labels used in the paper).
MODEL_NAMES = {
    "gpt-5-chatgpt": "GPT-5",
    "openai-gpt-5-2-responses": "GPT-5.2",
    "openai-gpt-5-4-responses": "GPT-5.4",
    "claude-4-6-sonnet-genai-vertex": "Claude 4.6 Sonnet",
    "claude-4-6-opus-genai-vertex": "Claude 4.6 Opus",
    "claude-4-5-sonnet-genai-vertex": "Claude 4.6 Sonnet",
    "claude-4-5-opus-genai-vertex": "Claude 4.6 Opus",
    "oci-grok-4-1-fast-non-reasoning": "Grok-4.1",
    "oci-grok-4-1-fast-reasoning": "Grok-4.1 R",
    "gemini-3-flash-preview-genai": "Gemini 3 Flash",
    "gemini-3-1-pro-preview-genai": "Gemini 3.1 Pro",
}
MODEL_ORDER = [
    "GPT-5", "GPT-5.2", "GPT-5.4",
    "Claude 4.6 Sonnet", "Claude 4.6 Opus",
    "Grok-4.1", "Grok-4.1 R",
    "Gemini 3 Flash", "Gemini 3.1 Pro",
]
# the 3 L6 adaptive persuaders, in a fixed order so per-persuader detail can be
# stored as a compact index instead of a repeated name.
PERSUADER_ORDER = ["Claude 4.6 Opus", "Grok-4.1 R", "GPT-5.4"]
PIDX = {name: i for i, name in enumerate(PERSUADER_ORDER)}
LEVELS = ["L1", "L2", "L3", "L4", "L5", "L6"]
LEVEL_DIRS = {  # bare level dir-name stem (PP appends a _<rubric> suffix)
    "L1": "conviction_L1", "L2": "conviction_L2", "L3": "conviction_L3",
    "L4": "conviction_L4", "L5": "cycling_L5", "L6": "adaptive_L6",
}


def disp(raw):
    return MODEL_NAMES.get(raw, raw)


# ----------------------------------------------------------------------------
# Per-dataset adapters (content datasets -- 5 of the 6)
# ----------------------------------------------------------------------------
# restrictive / permissive are the binary verdict strings the judges emit.
DATASETS = {
    "wildguard": {
        "label": "WildGuard", "content": "pair",
        "restrictive": "unsafe", "permissive": "safe",
        "gt_col": "response_harm_label", "gt_map": {"harmful": "unsafe", "unharmful": "safe"},
        "tag_cols": ["adversarial", "subcategory", "prompt_harm_label",
                     "response_refusal_label", "response_harm_agreement"],
        # binary is split across 3 runs; likert is one complete run.
        "binary_levels": {
            "L1": "multiturn_wildguard/run_id-n_500_t10_l1-0/conviction_L1",
            "L2": "multiturn_wildguard/run_id-n_500_t10_l2-6-0/conviction_L2",
            "L3": "multiturn_wildguard/run_id-n_500_t10_l2-6-0/conviction_L3",
            "L4": "multiturn_wildguard/run_id-n_500_t10_l2-6-0/conviction_L4",
            "L5": "multiturn_wildguard/run_id-n_500_t10_l2-6-0/cycling_L5",
            "L6": "multiturn_wildguard/run_id-n_500_t10_l6-0/adaptive_L6",
        },
        "binary_pilot": "multiturn_wildguard/run_id-n_500_t10_l1-0/pilot_sample.csv",
        "likert_dir": "multiturn_wildguard_likert/run_id-full-run-0",
    },
    "aegis": {
        "label": "AEGIS", "content": "pair",
        "restrictive": "unsafe", "permissive": "safe",
        "gt_col": "response_label", "gt_map": None,
        "tag_cols": ["prompt_label", "violated_categories", "response_label_source"],
        "binary_dir": "multiturn_aegis/run_id-full-run-0",
        "likert_dir": "multiturn_aegis_likert/run_id-full-run-0",
    },
    "hh_rlhf": {
        "label": "HH-RLHF", "content": "pair",
        "restrictive": "unsafe", "permissive": "safe",
        "gt_col": "rating", "gt_fmt": "harm rating {}/4",
        "tag_cols": ["rating", "min_harmlessness_score_transcript"],
        "binary_dir": "multiturn_hh_rlhf/run_id-full-run-0",
        "likert_dir": "multiturn_hh_rlhf_likert/run_id-full-run-0",
    },
    "toxigen": {
        "label": "ToxiGen", "content": "single",
        "restrictive": "toxic", "permissive": "not toxic",
        "gt_col": "toxicity_human", "gt_fmt": "human tox {}/5", "gt_round": 1,
        "tag_cols": ["target_group", "lewd", "stereotyping", "intent", "framing",
                     "actual_method", "predicted_author"],
        "binary_dir": "multiturn_toxigen/run_id-full-run-0",
        "likert_dir": "multiturn_toxigen_likert/run_id-full-run-0",
    },
    "mage": {
        "label": "MAGE", "content": "single",
        "restrictive": "ai_generated", "permissive": "human_written",
        "gt_col": "label", "gt_map": {"1": "human_written", "0": "ai_generated"},
        "tag_cols": ["src", "label"],
        "binary_dir": "multiturn_mage/run_id-full-run-0",
        "likert_dir": "multiturn_mage_likert/run_id-full-run-0",
    },
}

# Paired Prompts: outcomes-only (item text is not in the cache; it lives in
# wokeness_benchmark_viewer.html). Each task = (rubric, scale). example_id is
# "<prompt-hash>__<responder-model>"; outcomes are nested by prompt side.
PP_RUNS = {  # scale -> list of run dirs to merge (different levels live in different runs)
    "binary": ["paired_prompts/wiggle_binary/run_id-full-run-0-exp1-5",
               "paired_prompts/wiggle_binary/run_id-full-run-0-exp6"],
    "likert": ["paired_prompts/wiggle/run_id-phase_2-full-t10-exp1-0",
               "paired_prompts/wiggle/run_id-phase_2-full-t10-l23-0",
               "paired_prompts/wiggle/run_id-phase_2-full-t10-l45-0",
               "paired_prompts/wiggle/run_id-phase_2-full-t10-l6-0"],
}
PP_RUBRICS = {
    "hedging": {"restrictive": "hedged", "permissive": "not_hedged"},
    "refusal": {"restrictive": "non_compliant", "permissive": "compliant"},
}

NEUTRAL = {"unknown", "error", "n/a", ""}


# ----------------------------------------------------------------------------
# Loading helpers
# ----------------------------------------------------------------------------
def read_csv(path):
    p = CACHE / path if not isinstance(path, Path) else path
    with open(p, newline="") as f:
        return list(csv.DictReader(f))


def parse_turn(row):
    t = row.get("stop_turn", "")
    if t in ("", None):
        return None
    try:
        return int(float(t))
    except ValueError:
        return None


def outcome_from_row(row, scale):
    """Return (l0, observed, wiggled, turn) from one summary.csv row."""
    if scale == "binary":
        l0 = row.get("l0_verdict", "")
        obs = row.get("observed_verdict", "")
        w = str(row.get("flipped", "")).strip().lower() == "true"
    else:
        l0 = _to_int(row.get("l0_score"))
        obs = _to_int(row.get("observed_score"))
        w = str(row.get("shifted", "")).strip().lower() == "true"
    return l0, obs, w, parse_turn(row)


def _to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return v


def list_model_dirs(level_path):
    p = CACHE / level_path
    if not p.is_dir():
        return []
    return sorted(d.name for d in p.iterdir() if d.is_dir())


def load_level_outcomes(level_path, scale, by_id):
    """Standard (non-L6) level: <level>/<model>/summary.csv keyed by example_id."""
    for model_raw in list_model_dirs(level_path):
        summ = CACHE / level_path / model_raw / "summary.csv"
        if not summ.exists():
            continue
        for row in read_csv(summ):
            ex = row.get("example_id")
            if ex is None:
                continue
            l0, obs, w, t = outcome_from_row(row, scale)
            slot = by_id.setdefault(ex, {})
            m = slot.setdefault(disp(model_raw), {})
            m["L0"] = l0
            m[CUR_LEVEL] = {"v": obs, "w": w, "t": t}


def load_l6_outcomes(level_path, scale, by_id):
    """L6: <adaptive_L6>/<persuader>/<judge>/summary.csv -- aggregate across persuaders."""
    base = CACHE / level_path
    if not base.is_dir():
        return
    # collect per (example_id, judge): list of (persuader, observed, wiggled, turn)
    acc = {}
    l0_map = {}
    for persuader_raw in sorted(d.name for d in base.iterdir() if d.is_dir()):
        for judge_raw in list_model_dirs(f"{level_path}/{persuader_raw}"):
            summ = base / persuader_raw / judge_raw / "summary.csv"
            if not summ.exists():
                continue
            for row in read_csv(summ):
                ex = row.get("example_id")
                if ex is None:
                    continue
                l0, obs, w, t = outcome_from_row(row, scale)
                acc.setdefault((ex, disp(judge_raw)), []).append(
                    {"p": disp(persuader_raw), "v": obs, "w": w, "t": t})
                l0_map[(ex, disp(judge_raw))] = l0
    for (ex, judge), per in acc.items():
        flips = [p for p in per if p["w"]]
        # majority observed verdict among persuaders
        counts = {}
        for p in per:
            counts[p["v"]] = counts.get(p["v"], 0) + 1
        majority = max(counts, key=counts.get)
        turns = [p["t"] for p in flips if p["t"] is not None]
        slot = by_id.setdefault(ex, {})
        m = slot.setdefault(judge, {})
        m.setdefault("L0", l0_map[(ex, judge)])
        m["L6"] = {
            "v": majority,
            "w": len(flips) >= 2,            # majority of persuaders flipped it
            "t": round(sum(turns) / len(turns), 1) if turns else None,
            "k": len(flips), "n": len(per),
            "per": sorted(per, key=lambda x: x["p"]),
        }


CUR_LEVEL = None  # set per-level by build_task (keeps load_level_outcomes generic)


def extract_args(prow):
    """Pull pre-generated pressure arguments out of a pilot_sample row."""
    single, l4 = [], []
    for col, val in prow.items():
        if not val or not val.strip():
            continue
        if col.startswith("argument_"):
            single.append({"label": col[len("argument_"):].replace("_", " "), "text": val})
        elif col.startswith("l4_arg"):
            l4.append({"label": col, "text": val})
    l4.sort(key=lambda x: x["label"])
    return {"single": single, "l4": [x["text"] for x in l4],
            "l4_labels": [x["label"] for x in l4]}


def build_content(ds_key, cfg):
    """Load shared content (used by both scales) for a content dataset."""
    pilot_rel = cfg.get("binary_pilot") or f"{cfg['binary_dir']}/pilot_sample.csv"
    rows = read_csv(pilot_rel)
    content = {}
    for r in rows:
        ex = r.get("example_id")
        if not ex:
            continue
        # ground truth
        gt_raw = r.get(cfg["gt_col"], "")
        if cfg.get("gt_map"):
            truth = cfg["gt_map"].get(gt_raw, gt_raw)
        elif cfg.get("gt_fmt"):
            v = gt_raw
            if cfg.get("gt_round") is not None:
                try:
                    v = round(float(gt_raw), cfg["gt_round"])
                except ValueError:
                    pass
            truth = cfg["gt_fmt"].format(v)
        else:
            truth = gt_raw
        tags = {c: r[c] for c in cfg["tag_cols"] if r.get(c)}
        item = {
            "truth": truth,
            "jury": r.get("jury_majority_verdict") or None,
            "tags": tags,
            "args": extract_args(r),
        }
        if cfg["content"] == "pair":
            item["prompt"] = r.get("prompt", "")
            item["response"] = r.get("response", "")
        else:
            item["text"] = r.get("text") or r.get("response", "")
        content[ex] = item
    return content, [r["example_id"] for r in rows if r.get("example_id")]


def build_task_outcomes(cfg, scale):
    """Return {example_id: {model: {L0, L1..L6}}} for one (dataset, scale)."""
    global CUR_LEVEL
    by_id = {}
    if scale == "binary" and "binary_levels" in cfg:      # wildguard fragmented runs
        level_map = cfg["binary_levels"]
    else:
        run = cfg["binary_dir"] if scale == "binary" else cfg["likert_dir"]
        level_map = {lv: f"{run}/{LEVEL_DIRS[lv]}" for lv in LEVELS}
    for lv in LEVELS:
        path = level_map[lv]
        if lv == "L6":
            load_l6_outcomes(path, scale, by_id)
        else:
            CUR_LEVEL = lv
            load_level_outcomes(path, scale, by_id)
    return by_id


# ----------------------------------------------------------------------------
# Paired Prompts (outcomes-only)
# ----------------------------------------------------------------------------
def build_pp_task(rubric, scale):
    """Walk the nested PP dirs; items keyed by (prompt_side, example_id)."""
    global CUR_LEVEL
    by_key = {}     # composite key -> {model: {...}}, plus the responder model parsed out
    order = []
    seen = set()
    for run in PP_RUNS[scale]:
        run_path = CACHE / run / rubric
        if not run_path.is_dir():
            continue
        for side_dir in sorted(d.name for d in run_path.iterdir() if d.is_dir()):
            for lv in LEVELS:
                level_dir = f"{run}/{rubric}/{side_dir}/{LEVEL_DIRS[lv]}_{rubric}"
                if not (CACHE / level_dir).is_dir():
                    continue
                if lv == "L6":
                    tmp = {}
                    load_l6_outcomes(level_dir, scale, tmp)
                    _merge_pp(tmp, by_key, side_dir, order, seen)
                else:
                    CUR_LEVEL = lv
                    tmp = {}
                    load_level_outcomes(level_dir, scale, tmp)
                    _merge_pp(tmp, by_key, side_dir, order, seen)
    return by_key, order


def _merge_pp(tmp, by_key, side, order, seen):
    for ex, models in tmp.items():
        responder = ex.split("__", 1)[1] if "__" in ex else ""
        key = f"{side}|{ex}"
        if key not in seen:
            seen.add(key)
            order.append(key)
        dst = by_key.setdefault(key, {"_side": side, "_responder": disp(responder),
                                       "_hash": ex.split("__", 1)[0][:12], "out": {}})
        for model, slot in models.items():
            dst["out"].setdefault(model, {}).update(slot)


# ----------------------------------------------------------------------------
# Compact encoding
# ----------------------------------------------------------------------------
# To keep the embedded JSON small, outcomes are stored positionally (indexed by
# MODEL_ORDER) and binary verdicts as integer codes (0=permissive, 1=restrictive,
# 2=other), decoded back to labels in the browser. Likert keeps the raw 1-5 score.
def code_val(v, scale, restrictive, permissive):
    if v is None or v == "":
        return None
    if scale == "binary":
        if v == permissive:
            return 0
        if v == restrictive:
            return 1
        return 2
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _enc_cell(cell, scale, r, p):
    code = code_val(cell["v"], scale, r, p)
    w = 1 if cell["w"] else 0
    return [code, w] if cell["t"] is None else [code, w, cell["t"]]


def _enc_l6(cell, scale, r, p):
    per = [[PIDX.get(x["p"], -1), code_val(x["v"], scale, r, p),
            1 if x["w"] else 0, x["t"]] for x in cell["per"]]
    return [code_val(cell["v"], scale, r, p), 1 if cell["w"] else 0,
            cell["t"], cell["k"], cell["n"], per]


def missing_levels(items):
    """Levels (L1-L6) with no per-item data across the whole task (e.g. WildGuard
    binary L6, which only exists as an aggregate in the cache)."""
    present = set()
    for it in items:
        for pm in it["out"]:
            if not pm:
                continue
            for li, lv in enumerate(LEVELS, start=1):
                if li < len(pm) and pm[li] is not None:
                    present.add(lv)
    return [lv for lv in LEVELS if lv not in present]


def encode_out(models_dict, scale, restrictive, permissive):
    """Turn {model: {L0, L1..L6}} into a list aligned to MODEL_ORDER (None if absent)."""
    arr = []
    for m in MODEL_ORDER:
        md = models_dict.get(m)
        if not md:
            arr.append(None)
            continue
        row = [code_val(md.get("L0"), scale, restrictive, permissive)]
        for lv in ("L1", "L2", "L3", "L4", "L5"):
            c = md.get(lv)
            row.append(_enc_cell(c, scale, restrictive, permissive) if c else None)
        c6 = md.get("L6")
        row.append(_enc_l6(c6, scale, restrictive, permissive) if c6 else None)
        arr.append(row)
    return arr


# ----------------------------------------------------------------------------
# Assemble DATA and write HTML
# ----------------------------------------------------------------------------
def main():
    data = {
        "modelOrder": MODEL_ORDER,
        "persuaders": PERSUADER_ORDER,
        "levels": ["L0"] + LEVELS,
        "datasets": {},   # dataset -> {label, content, restrictive, permissive, items:{id:content}}
        "tasks": [],      # [{key, dataset, scale, restrictive, permissive, items:[{id, out}]}]
    }

    log = []
    for ds_key, cfg in DATASETS.items():
        content, order = build_content(ds_key, cfg)
        data["datasets"][ds_key] = {
            "label": cfg["label"], "content": cfg["content"],
            "restrictive": cfg["restrictive"], "permissive": cfg["permissive"],
            "items": content,
        }
        for scale in ("binary", "likert"):
            by_id = build_task_outcomes(cfg, scale)
            items = [{"id": ex,
                      "out": encode_out(by_id[ex], scale, cfg["restrictive"], cfg["permissive"])}
                     for ex in order if ex in by_id]
            data["tasks"].append({
                "key": f"{ds_key}|{scale}", "dataset": ds_key, "scale": scale,
                "label": cfg["label"], "restrictive": cfg["restrictive"],
                "permissive": cfg["permissive"], "outcomesOnly": False,
                "missing": missing_levels(items), "items": items,
            })
            n_out = sum(len(it["out"]) for it in items)
            log.append(f"  {cfg['label']:10s} {scale:6s}: {len(items):4d} items, "
                       f"{n_out:5d} model-cells")

    # Paired Prompts (outcomes-only)
    for rubric, rc in PP_RUBRICS.items():
        ds_key = f"pp_{rubric}"
        data["datasets"][ds_key] = {
            "label": f"Paired Prompts ({rubric})", "content": "none",
            "restrictive": rc["restrictive"], "permissive": rc["permissive"], "items": {},
        }
        for scale in ("binary", "likert"):
            by_key, order = build_pp_task(rubric, scale)
            items = []
            for key in order:
                rec = by_key[key]
                items.append({"id": key,
                              "out": encode_out(rec["out"], scale, rc["restrictive"], rc["permissive"]),
                              "side": rec["_side"], "responder": rec["_responder"],
                              "hash": rec["_hash"]})
            data["tasks"].append({
                "key": f"{ds_key}|{scale}", "dataset": ds_key, "scale": scale,
                "label": f"Paired Prompts ({rubric})", "restrictive": rc["restrictive"],
                "permissive": rc["permissive"], "outcomesOnly": True,
                "missing": missing_levels(items), "items": items,
            })
            log.append(f"  PP-{rubric:7s} {scale:6s}: {len(items):4d} items")

    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html = HTML_TEMPLATE.replace("/*__DATA__*/", payload)
    OUT.write_text(html, encoding="utf-8")

    size_mb = OUT.stat().st_size / 1e6
    print("Built", OUT.name, f"({size_mb:.1f} MB)")
    print("\n".join(log))
    print(f"Tasks: {len(data['tasks'])}  Datasets: {len(data['datasets'])}")


# ----------------------------------------------------------------------------
# HTML template  (the /*__DATA__*/ marker is replaced with the JSON payload)
# ----------------------------------------------------------------------------
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html>
<head>
<title>Wiggle Framework Data Viewer</title>
<meta charset="utf-8">
<style>
* { box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 1280px; margin: 0 auto; padding: 20px; background: #fff; color: #1f2937; }
h1 { font-size: 22px; margin: 0 0 4px; }
.sub { color: #6b7280; font-size: 13px; margin-bottom: 14px; }
.controls { display: flex; gap: 16px; align-items: center; padding: 12px 16px; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.controls label { font-size: 13px; font-weight: 600; color: #374151; }
.controls select { padding: 6px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; font-family: inherit; background: #fff; }
.scale-toggle button { padding: 6px 14px; border: 1px solid #d1d5db; background: #fff; cursor: pointer; font-weight: 600; font-size: 13px; }
.scale-toggle button:first-child { border-radius: 6px 0 0 6px; }
.scale-toggle button:last-child { border-radius: 0 6px 6px 0; border-left: none; }
.scale-toggle button.active { background: #2563eb; color: #fff; border-color: #2563eb; }
.stats { display: flex; gap: 22px; padding: 10px 16px; background: #f9fafb; border-radius: 8px; margin-bottom: 14px; font-size: 13px; flex-wrap: wrap; }
.nav { display: flex; align-items: center; gap: 12px; margin: 14px 0; flex-wrap: wrap; }
.nav button { padding: 8px 16px; background: #e5e7eb; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; }
.nav button:disabled { background: #f3f4f6; color: #9ca3af; cursor: default; }
.nav input { padding: 6px 10px; border: 1px solid #d1d5db; border-radius: 4px; }
#goto { width: 80px; } #filter { width: 300px; }
.meta-panel { padding: 14px 16px; background: #fafafa; border: 1px solid #e5e7eb; border-radius: 8px; margin: 14px 0; }
.meta-panel h2 { margin: 0 0 8px; font-size: 16px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.badge { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.02em; }
.badge-ds { background: #f3e8ff; color: #6b21a8; }
.badge-scale { background: #dbeafe; color: #1e40af; }
.badge-truth { background: #fef3c7; color: #92400e; }
.badge-jury { background: #e0e7ff; color: #3730a3; }
.tags { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 6px; }
.tag { font-size: 11px; background: #f1f5f9; color: #475569; padding: 2px 8px; border-radius: 10px; }
.tag b { color: #1e293b; }
.pair-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 12px 0; }
.section-block { padding: 12px 14px; border-radius: 6px; border-left: 4px solid #d1d5db; background: #fff; }
.section-block .label { font-size: 11px; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
.section-block .body { font-size: 14px; line-height: 1.55; white-space: pre-wrap; word-break: break-word; max-height: 320px; overflow-y: auto; }
.section-block.prompt { border-left-color: #2563eb; background: #eff6ff; }
.section-block.response { border-left-color: #7c3aed; }
.note { padding: 10px 14px; background: #fffbeb; border: 1px solid #fde68a; border-radius: 6px; font-size: 13px; color: #92400e; margin: 12px 0; }
.matrix-wrap { overflow-x: auto; margin: 14px 0; border: 1px solid #e5e7eb; border-radius: 8px; }
table.matrix { border-collapse: collapse; width: 100%; font-size: 13px; }
table.matrix th, table.matrix td { padding: 7px 9px; text-align: center; border: 1px solid #eef2f7; white-space: nowrap; }
table.matrix thead th { background: #f9fafb; font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; color: #6b7280; position: sticky; top: 0; }
table.matrix td.model, table.matrix th.model { text-align: left; font-weight: 600; position: sticky; left: 0; background: #fff; z-index: 1; box-shadow: 1px 0 0 #eef2f7; }
table.matrix thead th.model { background: #f9fafb; z-index: 2; }
.cell { border-radius: 4px; padding: 4px 6px; font-weight: 600; display: inline-block; min-width: 46px; cursor: default; }
.cell.l0 { box-shadow: inset 0 0 0 2px #94a3b8; }
.v-perm { background: #d1fae5; color: #065f46; }
.v-rest { background: #fee2e2; color: #991b1b; }
.v-neut { background: #f3f4f6; color: #6b7280; }
.wig { outline: 2px solid #b45309; outline-offset: -2px; }
.wig::after { content: "!"; color: #b45309; font-weight: 800; margin-left: 3px; }
td.l6 { cursor: pointer; }
.k-badge { font-size: 10px; color: #6b7280; display: block; margin-top: 1px; }
.legend { display: flex; gap: 16px; font-size: 12px; color: #6b7280; margin: 8px 2px; flex-wrap: wrap; align-items: center; }
.legend .cell { min-width: 0; padding: 2px 8px; }
.wrate { font-size: 11px; color: #6b7280; }
.collapse .head { cursor: pointer; font-size: 12px; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; user-select: none; padding: 6px 0; }
.collapse .body { display: none; }
.arg { padding: 8px 12px; margin: 6px 0; border-left: 3px solid #cbd5e1; background: #f8fafc; font-size: 13px; line-height: 1.5; border-radius: 0 4px 4px 0; }
.arg .who { font-weight: 700; color: #475569; font-size: 11px; text-transform: uppercase; }
.persuaders { font-size: 12px; }
.persuaders div { padding: 2px 0; }
</style>
</head>
<body>
<h1>Wiggle Framework Data Viewer</h1>
<div class="sub">Multi-turn pressure ladder (L1&ndash;L6). Each item shows how 9 judges held or wiggled vs their L0 baseline under escalating pressure.</div>

<div class="controls">
  <div><label>Dataset</label> <select id="dsSel" onchange="onDataset(this.value)"></select></div>
  <div class="scale-toggle" id="scaleToggle">
    <button data-scale="binary" onclick="onScale('binary')">Binary</button>
    <button data-scale="likert" onclick="onScale('likert')">Likert 1&ndash;5</button>
  </div>
</div>

<div class="stats" id="stats"></div>
<div class="nav">
  <button onclick="go(idx-1)" id="prev">&#8592; Prev</button>
  <span id="counter"></span>
  <button onclick="go(idx+1)" id="next">Next &#8594;</button>
  <div style="margin-left:auto;display:flex;gap:8px;">
    <input id="goto" type="number" min="1" placeholder="#" onchange="go(+this.value-1)">
    <input id="filter" type="text" placeholder="Filter by id, content, truth..." oninput="applyFilter(this.value)">
  </div>
</div>
<div id="content"></div>
<div class="nav" style="margin-top:20px;">
  <button onclick="go(idx-1)" id="prev2">&#8592; Prev</button>
  <span id="counter2"></span>
  <button onclick="go(idx+1)" id="next2">Next &#8594;</button>
</div>

<script>
const DATA = /*__DATA__*/;
const LEVELS = DATA.levels;                 // ["L0","L1",...,"L6"]
const PERSUADERS = DATA.persuaders;         // L6 persuader display names by index
const taskByKey = {}; DATA.tasks.forEach(t => taskByKey[t.key] = t);

let curDataset = DATA.tasks[0].dataset;
let curScale = "binary";
let idx = 0;
let filterQ = "";
let filtered = [];

function esc(s){ const d=document.createElement("div"); d.textContent=String(s==null?'':s); return d.innerHTML; }

function curTask(){ return taskByKey[curDataset + "|" + curScale]; }

function initDatasetSelector(){
  const seen = {}; const opts = [];
  DATA.tasks.forEach(t => { if(!seen[t.dataset]){ seen[t.dataset]=1; opts.push(t.dataset); } });
  const sel = document.getElementById('dsSel');
  sel.innerHTML = opts.map(d => '<option value="'+d+'">'+esc(DATA.datasets[d].label)+'</option>').join('');
  sel.value = curDataset;
}

function onDataset(d){ curDataset=d; reload(); }
function onScale(s){ curScale=s; reload(); }

function syncScaleButtons(){
  document.querySelectorAll('#scaleToggle button').forEach(b =>
    b.classList.toggle('active', b.dataset.scale===curScale));
}

function reload(){ idx=0; filterQ=""; document.getElementById('filter').value=""; syncScaleButtons(); applyFilter(""); }

function itemMatchesFilter(it, q){
  if(!q) return true;
  const ds = DATA.datasets[curTask().dataset];
  const c = ds.items[it.id] || {};
  const hay = [it.id, c.truth, c.jury, c.prompt, c.response, c.text, it.responder].join(' ').toLowerCase();
  return hay.includes(q);
}

function applyFilter(q){
  filterQ = q.toLowerCase();
  filtered = curTask().items.filter(it => itemMatchesFilter(it, filterQ));
  idx = 0; renderStats(); render();
}

function go(i){ idx=Math.max(0, Math.min(i, filtered.length-1)); render(); window.scrollTo(0,0); }

function renderStats(){
  const t = curTask();
  const total = t.items.length;
  document.getElementById('stats').innerHTML =
    '<div><strong>'+total+'</strong> items</div>'+
    '<div><strong>'+DATA.modelOrder.length+'</strong> judges</div>'+
    '<div><strong>6</strong> pressure levels (L1&ndash;L6)</div>'+
    '<div>restrictive=<span class="cell v-rest">'+esc(t.restrictive)+'</span> &nbsp; permissive=<span class="cell v-perm">'+esc(t.permissive)+'</span></div>'+
    (filterQ ? '<div style="color:#2563eb">'+filtered.length+' match filter</div>' : '');
}

// ---- compact-format decoders (see build_wiggle_viewer.py "Compact encoding") ----
// binary: code 0=permissive, 1=restrictive, 2=other.  likert: raw 1-5 score.
function codeText(task, code){
  if(code==null) return "&mdash;";
  if(task.scale==="likert") return String(code);
  return code===0 ? esc(task.permissive) : code===1 ? esc(task.restrictive) : "other";
}
function codeClass(task, code){
  if(code==null) return "v-neut";
  if(task.scale==="likert"){ const n=+code; return n<=2?"v-perm":n>=4?"v-rest":"v-neut"; }
  return code===0?"v-perm":code===1?"v-rest":"v-neut";
}
function cellHtml(task, code, opts){
  opts = opts||{};
  let cls = "cell " + codeClass(task, code);
  if(opts.l0) cls += " l0";
  if(opts.wig) cls += " wig";
  let title = opts.title ? ' title="'+esc(opts.title)+'"' : '';
  let sub = opts.sub ? '<span class="k-badge">'+esc(opts.sub)+'</span>' : '';
  return '<span class="'+cls+'"'+title+'>'+codeText(task, code)+'</span>'+sub;
}

// per-model outcome row: [L0code, c1..c5, c6]; cN(1-5)=[code,w,t?]; c6=[code,w,t,k,n,per]
function modelWiggleRate(pm){
  if(!pm) return null;
  let w=0, n=0;
  for(let li=1; li<=6; li++){ const c=pm[li]; if(c){ n++; if(c[1]) w++; } }
  return n ? (w/n) : null;
}

function renderMatrix(task, item){
  let h = '<div class="matrix-wrap"><table class="matrix"><thead><tr>';
  h += '<th class="model">Judge</th>';
  for(const lv of LEVELS) h += '<th>'+lv+'</th>';
  h += '<th>wiggle</th></tr></thead><tbody>';
  DATA.modelOrder.forEach((model, mi) => {
    const pm = item.out[mi];
    h += '<tr><td class="model">'+esc(model)+'</td>';
    if(!pm){ for(const lv of LEVELS) h+='<td>&mdash;</td>'; h+='<td></td></tr>'; return; }
    h += '<td>'+cellHtml(task, pm[0], {l0:true, title:"L0 baseline"})+'</td>';
    for(let li=1; li<=5; li++){
      const c = pm[li];
      if(!c){ h += '<td>&mdash;</td>'; continue; }
      const t = c.length>2 ? c[2] : null;
      const title = (c[1]?"WIGGLE ":"held ")+"vs L0"+(t!=null?"; flipped at turn "+t:"");
      h += '<td>'+cellHtml(task, c[0], {wig:c[1], title:title})+'</td>';
    }
    const c6 = pm[6];
    if(!c6){ h += '<td>&mdash;</td>'; }
    else {
      const title = "majority of "+c6[4]+" persuaders; "+c6[3]+"/"+c6[4]+" flipped"+(c6[2]!=null?"; mean flip turn "+c6[2]:"");
      h += '<td class="l6" onclick="toggleP(this)" data-mi="'+mi+'">'+
           cellHtml(task, c6[0], {wig:c6[1], title:title, sub:c6[3]+"/"+c6[4]})+'</td>';
    }
    const wr = modelWiggleRate(pm);
    h += '<td class="wrate">'+(wr==null?'&mdash;':Math.round(wr*100)+'%')+'</td></tr>';
  });
  h += '</tbody></table></div>';
  h += '<div class="legend">'+
       '<span><span class="cell v-perm">'+esc(task.permissive)+'</span> permissive</span>'+
       '<span><span class="cell v-rest">'+esc(task.restrictive)+'</span> restrictive</span>'+
       '<span><span class="cell v-neut">&mdash;</span> neutral/midpoint</span>'+
       '<span><span class="cell l0">L0</span> baseline (outlined)</span>'+
       '<span><span class="cell wig">x</span> wiggle vs L0</span>'+
       '<span>L6 = majority of 3 persuaders &middot; click cell to expand</span>'+
       '</div>';
  if(task.missing && task.missing.length){
    h += '<div class="note">No per-item data for '+task.missing.join(', ')+
         ' in this task &mdash; only aggregate rates exist in the cache, so '+
         (task.missing.length>1?'those columns are':'that column is')+' blank above.</div>';
  }
  return h;
}

function toggleP(td){
  const mi = +td.getAttribute('data-mi');
  const item = filtered[idx];
  const pm = item.out[mi];
  const c6 = pm && pm[6];
  if(!c6 || !c6[5]) return;
  let ex = td.querySelector('.persuaders');
  if(ex){ ex.remove(); return; }
  const task = curTask();
  let h = '<div class="persuaders">';
  for(const p of c6[5]){            // [persuaderIdx, code, w, turn]
    h += '<div>'+esc(PERSUADERS[p[0]]||'?')+': <span class="cell '+codeClass(task,p[1])+(p[2]?' wig':'')+'">'+
         codeText(task,p[1])+'</span>'+(p[3]!=null?' (turn '+p[3]+')':'')+'</div>';
  }
  h += '</div>';
  td.insertAdjacentHTML('beforeend', h);
}

function renderContent(task, item){
  const ds = DATA.datasets[task.dataset];
  if(ds.content==="none"){
    return '<div class="note">Item text is not in the data cache for Paired Prompts &mdash; the prompt/response pairs live in '+
           '<code>wokeness_benchmark_viewer.html</code>. Shown here: judge outcomes only. '+
           'Item id encodes the responding model.</div>';
  }
  const c = ds.items[item.id]; if(!c) return '';
  if(ds.content==="pair"){
    return '<div class="pair-grid">'+
      '<div class="section-block prompt"><div class="label">Prompt</div><div class="body">'+esc(c.prompt)+'</div></div>'+
      '<div class="section-block response"><div class="label">Response (being judged)</div><div class="body">'+esc(c.response)+'</div></div>'+
      '</div>';
  }
  return '<div class="section-block response"><div class="label">Text being judged</div><div class="body">'+esc(c.text)+'</div></div>';
}

function renderArgs(task, item){
  const ds = DATA.datasets[task.dataset];
  const c = ds.items[item.id]; if(!c || !c.args) return '';
  const a = c.args;
  if((!a.single || !a.single.length) && (!a.l4 || !a.l4.length)) return '';
  let h = '<div class="collapse"><div class="head" onclick="toggleC(this)">&#9654; Pressure arguments faced (L2&ndash;L4)</div><div class="body">';
  for(const s of (a.single||[])) h += '<div class="arg"><span class="who">argues '+esc(s.label)+'</span><br>'+esc(s.text)+'</div>';
  if(a.l4 && a.l4.length){
    h += '<div style="font-size:11px;font-weight:700;color:#6b7280;margin-top:8px">L4 CONSENSUS (3 reviewers)</div>';
    a.l4.forEach((t,i)=> h += '<div class="arg"><span class="who">reviewer '+(i+1)+'</span><br>'+esc(t)+'</div>');
  }
  h += '</div></div>';
  return h;
}

function toggleC(el){
  const b = el.parentElement.querySelector('.body');
  const open = b.style.display==='block';
  b.style.display = open?'none':'block';
  el.innerHTML = el.innerHTML.replace(/^[▶▼]/, open?'▶':'▼');
}

function render(){
  const task = curTask();
  if(!filtered.length){ document.getElementById('content').innerHTML='<p>No items match.</p>';
    ['counter','counter2'].forEach(id=>document.getElementById(id).textContent=''); return; }
  const item = filtered[idx];
  const ds = DATA.datasets[task.dataset];
  const c = ds.items[item.id] || {};

  let h = '<div class="meta-panel"><h2>';
  h += '<code>'+esc(displayId(item))+'</code> ';
  h += '<span class="badge badge-ds">'+esc(task.label)+'</span> ';
  h += '<span class="badge badge-scale">'+esc(task.scale)+'</span>';
  if(c.truth) h += ' <span class="badge badge-truth">truth: '+esc(c.truth)+'</span>';
  if(c.jury)  h += ' <span class="badge badge-jury">jury: '+esc(c.jury)+'</span>';
  if(item.responder) h += ' <span class="badge badge-jury">responder: '+esc(item.responder)+'</span>';
  if(item.side) h += ' <span class="badge badge-scale">'+esc(item.side)+'</span>';
  h += '</h2>';
  if(c.tags && Object.keys(c.tags).length){
    h += '<div class="tags">'+Object.entries(c.tags).map(([k,v])=>'<span class="tag"><b>'+esc(k)+':</b> '+esc(v)+'</span>').join('')+'</div>';
  }
  h += '</div>';

  h += renderContent(task, item);
  h += renderMatrix(task, item);
  h += renderArgs(task, item);

  document.getElementById('content').innerHTML = h;
  ['counter','counter2'].forEach(id=>document.getElementById(id).textContent='Item '+(idx+1)+' of '+filtered.length);
  ['prev','prev2'].forEach(id=>document.getElementById(id).disabled=idx<=0);
  ['next','next2'].forEach(id=>document.getElementById(id).disabled=idx>=filtered.length-1);
}

function displayId(item){
  if(item.hash) return item.hash + (item.side?(' / '+item.side):'');
  return item.id;
}

initDatasetSelector();
reload();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    sys.exit(main())
