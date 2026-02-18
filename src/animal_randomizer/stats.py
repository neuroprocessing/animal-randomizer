from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from math import sqrt
from statistics import mean, pstdev
from typing import Any, Dict, List

from .models import AnimalRecord, AssignmentRecord


def _cohens_d(values_a: List[float], values_b: List[float]) -> float:
    if len(values_a) < 2 or len(values_b) < 2:
        return 0.0
    mean_a = mean(values_a)
    mean_b = mean(values_b)
    sd_a = pstdev(values_a)
    sd_b = pstdev(values_b)
    pooled = sqrt((sd_a**2 + sd_b**2) / 2.0)
    if pooled == 0:
        return 0.0
    return (mean_a - mean_b) / pooled


def compute_statistics(
    animals: List[AnimalRecord],
    assignments: List[AssignmentRecord],
    weight_d_warning: float = 0.8,
) -> tuple[Dict[str, Any], List[str]]:
    animal_map = {a.animal_id: a for a in animals}
    by_group: Dict[str, List[AnimalRecord]] = defaultdict(list)
    for row in assignments:
        by_group[row.group].append(animal_map[row.animal_id])

    stats: Dict[str, Any] = {"groups": {}, "effect_sizes": {}}
    warnings: List[str] = []

    for group, rows in by_group.items():
        weights = [float(a.weight) for a in rows if a.weight is not None]
        sex_counts: Dict[str, int] = defaultdict(int)
        cage_counts: Dict[str, int] = defaultdict(int)
        for animal in rows:
            sex_counts[str(animal.sex or "NA")] += 1
            cage_counts[str(animal.cage or "NA")] += 1
        stats["groups"][group] = {
            "n": len(rows),
            "weight_mean": round(mean(weights), 4) if weights else None,
            "weight_sd": round(pstdev(weights), 4) if len(weights) > 1 else 0.0,
            "sex_distribution": dict(sex_counts),
            "cage_distribution": dict(cage_counts),
        }

    for ga, gb in combinations(sorted(by_group.keys()), 2):
        wa = [float(a.weight) for a in by_group[ga] if a.weight is not None]
        wb = [float(a.weight) for a in by_group[gb] if a.weight is not None]
        d = round(_cohens_d(wa, wb), 4)
        label = f"{ga} vs {gb}"
        stats["effect_sizes"][label] = {"cohens_d_weight": d}
        if abs(d) >= weight_d_warning:
            warnings.append(f"Weight imbalance warning ({label}): Cohen's d={d}")

    group_sizes = [v["n"] for v in stats["groups"].values()]
    if group_sizes and max(group_sizes) - min(group_sizes) > 1:
        warnings.append("Group size imbalance exceeds 1 animal.")

    return stats, warnings
