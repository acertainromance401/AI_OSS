from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Final

BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent
PRIMARY_DATASET: Final[Path] = BASE_DIR / "data" / "color_emotion_labeled_updated.csv"
WARMTH_DATASET: Final[Path] = BASE_DIR / "data" / "colorassociations_warmth - colorwarmth.csv"
K_NEIGHBORS: Final[int] = 5
EPSILON: Final[float] = 1e-6


@dataclass
class RGB:
    r: int
    g: int
    b: int


@dataclass(frozen=True)
class LabeledColor:
    emotion: str
    color_name: str
    rgb: RGB


@dataclass(frozen=True)
class ColorAssociation:
    is_warm: bool
    associations: tuple[str, ...]


_DATASET_CACHE: list[LabeledColor] | None = None
_ASSOCIATION_CACHE: dict[str, ColorAssociation] | None = None
_EMOTIONS_CACHE: list[str] | None = None


def _clamp_channel(value: int) -> int:
    return max(0, min(255, int(value)))


def _normalize_label(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _read_primary_dataset() -> list[LabeledColor]:
    if not PRIMARY_DATASET.exists():
        raise ValueError(f"Primary dataset not found: {PRIMARY_DATASET}")

    rows: list[LabeledColor] = []
    with PRIMARY_DATASET.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            emotion_raw = (row.get("emotion") or "").strip()
            r_raw = (row.get("R") or "").strip()
            g_raw = (row.get("G") or "").strip()
            b_raw = (row.get("B") or "").strip()
            color_name = _normalize_label(row.get("color_name") or "unknown")

            if not emotion_raw or not r_raw or not g_raw or not b_raw:
                continue

            try:
                rgb = RGB(r=int(float(r_raw)), g=int(float(g_raw)), b=int(float(b_raw)))
            except ValueError:
                continue

            rows.append(
                LabeledColor(
                    emotion=_normalize_label(emotion_raw),
                    color_name=color_name,
                    rgb=normalize_rgb(rgb),
                )
            )

    if not rows:
        raise ValueError("Primary dataset is empty or malformed")
    return rows


def _read_warmth_dataset() -> dict[str, ColorAssociation]:
    associations: dict[str, ColorAssociation] = {}
    if not WARMTH_DATASET.exists():
        return associations

    with WARMTH_DATASET.open("r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) < 10:
                continue

            color_id = _normalize_label(row[1])
            if not color_id or color_id == "color_id":
                continue

            warm_raw = (row[6] or "").strip()
            assoc_raw = [row[7], row[8], row[9]]
            assoc = tuple(
                _normalize_label(value)
                for value in assoc_raw
                if value and _normalize_label(value)
            )

            associations[color_id] = ColorAssociation(
                is_warm=warm_raw == "1",
                associations=assoc,
            )

    return associations


def _load_resources() -> tuple[list[LabeledColor], dict[str, ColorAssociation], list[str]]:
    global _DATASET_CACHE, _ASSOCIATION_CACHE, _EMOTIONS_CACHE

    if _DATASET_CACHE is None:
        _DATASET_CACHE = _read_primary_dataset()
    if _ASSOCIATION_CACHE is None:
        _ASSOCIATION_CACHE = _read_warmth_dataset()
    if _EMOTIONS_CACHE is None:
        _EMOTIONS_CACHE = sorted({sample.emotion for sample in _DATASET_CACHE})

    return _DATASET_CACHE, _ASSOCIATION_CACHE, _EMOTIONS_CACHE


def normalize_rgb(color: RGB) -> RGB:
    return RGB(
        r=_clamp_channel(color.r),
        g=_clamp_channel(color.g),
        b=_clamp_channel(color.b),
    )


def _distance(a: RGB, b: RGB) -> float:
    dr = float(a.r - b.r)
    dg = float(a.g - b.g)
    db = float(a.b - b.b)
    return (dr * dr + dg * dg + db * db) ** 0.5


def rgb_to_emotion_scores(color: RGB) -> dict[str, float]:
    dataset, assoc_map, emotion_labels = _load_resources()
    target = normalize_rgb(color)

    neighbors = sorted(
        dataset,
        key=lambda sample: _distance(target, sample.rgb),
    )[:K_NEIGHBORS]

    raw_scores: dict[str, float] = defaultdict(float)
    for sample in neighbors:
        dist = _distance(target, sample.rgb)
        base_weight = 1.0 / (dist + EPSILON)
        raw_scores[sample.emotion] += base_weight

        info = assoc_map.get(sample.color_name)
        if info and info.associations:
            warmth_multiplier = 1.1 if info.is_warm else 1.0
            bonus = (base_weight * 0.15) * warmth_multiplier
            for assoc in info.associations:
                raw_scores[assoc] += bonus / len(info.associations)

    total = sum(raw_scores.values())
    if total <= 0:
        uniform = round(1.0 / len(emotion_labels), 4)
        return {label: uniform for label in emotion_labels}

    return {
        label: round(raw_scores.get(label, 0.0) / total, 4)
        for label in emotion_labels
    }


def aggregate_palette(
    colors: list[RGB],
    weights: list[float] | None = None,
) -> tuple[str, dict[str, float]]:
    if not colors:
        raise ValueError("At least one color is required.")

    if weights is None:
        weights = [1.0 for _ in colors]

    if len(weights) != len(colors):
        raise ValueError("weights length must match colors length")

    safe_weights = [max(0.0, float(w)) for w in weights]
    weight_total = sum(safe_weights)
    if weight_total == 0:
        safe_weights = [1.0 for _ in colors]
        weight_total = float(len(colors))

    _, _, emotion_labels = _load_resources()
    merged = {label: 0.0 for label in emotion_labels}
    for color, weight in zip(colors, safe_weights):
        local_scores = rgb_to_emotion_scores(color)
        for label, score in local_scores.items():
            merged[label] += score * (weight / weight_total)

    best_emotion = max(merged, key=merged.get)
    rounded = {label: round(score, 4) for label, score in merged.items()}
    return best_emotion, rounded
