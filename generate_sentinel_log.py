#!/usr/bin/env python3
"""
generate_sentinel_log.py — Project Sentinel synthetic log generator.

Builds a deliberately messy data/raw/ground_station_log.csv directly FROM 
the raw JSON file (all_neos_data.json), injecting flaws on every run so 
a naive 1:1 join fails:

    1. Dropped ids  (~10% of the input ids are simply missing from the log)
    2. Ghost ids    (~10% extra, fabricated ids appear in the log)
    3. Dirty values (observatory_code and confidence_score have dirty/null values)

Usage (terminal / direct run):
    python generate_sentinel_log.py
"""

import json
import csv
import random
from pathlib import Path

DEFAULT_JSON = Path("data/raw/all_neos_data.json")
DEFAULT_OUTPUT = Path("data/raw/ground_station_log.csv")
FIELDNAMES = ["neo_id", "observatory_code", "confidence_score"]

OBSERVATORY_CODES = ["G96", "703", "I41", "F51", "W88", " G96", "UNKNOWN"]

DROP_RATE = 0.10
GHOST_RATE = 0.10
DIRTY_RATE = 0.15


def _dirty_confidence_score():
    """Mostly a clean 2-decimal float string; occasionally blank, padded, 'N/A', or 'null'."""
    clean = f"{random.uniform(0.50, 0.99):.2f}"
    if random.random() < DIRTY_RATE:
        return random.choice(["", "N/A", "null", f"{clean} "])
    return clean


def _fabricate_ghost_id(used_ids):
    """Build a plausible NEO-id-shaped string that is not already in use."""
    while True:
        candidate = str(random.randint(1_000_000, 4_999_999))
        if candidate not in used_ids:
            return candidate


def load_ids_from_json(json_path):
    """Read the raw JSON file and extract unique neo_reference_ids."""
    p = Path(json_path)
    if not p.exists():
        # محاولة المسار البديل لو تم تشغيله من داخل مجلد notebooks
        alt_p = Path("../data/raw/all_neos_data.json")
        if alt_p.exists():
            p = alt_p
        else:
            raise FileNotFoundError(f"Could not find JSON file at {p} or {alt_p}.")
            
    with p.open("r", encoding="utf-8") as f:
        neos_list = json.load(f)
        
    ids = [str(obj["neo_reference_id"]) for obj in neos_list if "neo_reference_id" in obj]
    return list(dict.fromkeys(ids))  # إزالة التكرار مع الحفاظ على الترتيب


def generate_sentinel_log(json_path=DEFAULT_JSON, output_path=DEFAULT_OUTPUT, seed=None):
    """
    Write a messy ground_station_log.csv built directly from the raw JSON NEO ids.
    """
    if seed is not None:
        random.seed(seed)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # استخراج الـ IDs من ملف الـ JSON مباشرة
    raw_ids = load_ids_from_json(json_path)
    ids = [str(i).strip() for i in raw_ids if str(i).strip()]

    n_drop = round(len(ids) * DROP_RATE)
    dropped = set(random.sample(ids, n_drop)) if n_drop else set()
    surviving_ids = [i for i in ids if i not in dropped]

    n_ghost = round(len(ids) * GHOST_RATE)
    used_ids = set(ids)
    ghost_ids = []
    for _ in range(n_ghost):
        ghost = _fabricate_ghost_id(used_ids)
        used_ids.add(ghost)
        ghost_ids.append(ghost)

    all_ids = surviving_ids + ghost_ids
    random.shuffle(all_ids)

    rows = [
        {
            "neo_id": neo_id,
            "observatory_code": random.choice(OBSERVATORY_CODES),
            "confidence_score": _dirty_confidence_score(),
        }
        for neo_id in all_ids
    ]

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(
        f"[generate_sentinel_log] Loaded {len(ids)} ids from JSON -> Generated {len(rows)} log rows "
        f"({len(dropped)} dropped, {len(ghost_ids)} ghost ids injected) -> {output_path}"
    )
    return output_path


if __name__ == "__main__":
    generate_sentinel_log()