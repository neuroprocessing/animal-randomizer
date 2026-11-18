from __future__ import annotations

import random
import secrets
from collections import defaultdict
from math import isfinite
from statistics import mean
from typing import Dict, List

from .models import AnimalRecord, AssignmentRecord, ConstraintConfig, RandomizationConfig


def _normalize_sex(sex: str | None) -> str:
    value = "" if sex is None else str(sex).strip().lower()
    if value in ("m", "male"):
        return "M"
    if value in ("f", "female"):
        return "F"
    return "NA"


def _weight_bin(value: float | None) -> str:
    if value is None:
        return "NA"
    return str(int(float(value) // 5))


def _stratum_key(animal: AnimalRecord, stratify_by: List[str], weight_balance: bool) -> str:
    parts: List[str] = []
    for key in stratify_by:
        if key == "sex":
            parts.append(_normalize_sex(animal.sex))
        elif key == "cage":
            parts.append(str(animal.cage or "NA"))
        elif key == "age":
            parts.append(str(animal.age if animal.age is not None else "NA"))
        elif key == "weight":
            parts.append(_weight_bin(animal.weight))
    if weight_balance and "weight" not in stratify_by:
        parts.append(f"w{_weight_bin(animal.weight)}")
    return "|".join(parts) if parts else "ALL"


def _choose_group(
    animal: AnimalRecord,
    group_names: List[str],
    group_counts: Dict[str, int],
    cage_counts: Dict[str, Dict[str, int]],
    constraints: ConstraintConfig,
    rng: random.Random,
    weight_sums: Dict[str, float],
    target_weight: float | None,
) -> str:
    min_size = min(group_counts.values())
    candidates = [g for g in group_names if group_counts[g] == min_size]

    cage = str(animal.cage or "NA")
    if constraints.max_animals_per_cage_per_group is not None:
        limited = [
            g
            for g in candidates
            if cage_counts[g][cage] < constraints.max_animals_per_cage_per_group
        ]
        if not limited:
            raise ValueError(
                "No feasible group remains for animal "
                f"{animal.animal_id} in cage {cage} under the configured cage constraint."
            )
        candidates = limited

    if constraints.minimize_cage_clustering:
        min_cage = min(cage_counts[g][cage] for g in candidates)
        candidates = [g for g in candidates if cage_counts[g][cage] == min_cage]

    if constraints.weight_balance and target_weight is not None and animal.weight is not None:
        projected: dict[str, float] = {}
        for group in candidates:
            n = group_counts[group]
            projected[group] = (weight_sums[group] + float(animal.weight)) / (n + 1)
        best_distance = min(abs(value - target_weight) for value in projected.values())
        candidates = [group for group in candidates if abs(projected[group] - target_weight) == best_distance]

    return rng.choice(candidates)


def _assign_balanced(
    animals: List[AnimalRecord],
    group_names: List[str],
    constraints: ConstraintConfig,
    rng: random.Random,
    shared_cage_counts: Dict[str, Dict[str, int]] | None = None,
) -> List[AssignmentRecord]:
    assignments: List[AssignmentRecord] = []
    group_counts = {g: 0 for g in group_names}
    cage_counts = shared_cage_counts or {g: defaultdict(int) for g in group_names}
    weight_sums: Dict[str, float] = {g: 0.0 for g in group_names}
    observed_weights = [
        float(animal.weight)
        for animal in animals
        if animal.weight is not None and isfinite(float(animal.weight))
    ]
    target_weight = mean(observed_weights) if observed_weights else None

    rng.shuffle(animals)
    for animal in animals:
        chosen = _choose_group(
            animal,
            group_names,
            group_counts,
            cage_counts,
            constraints,
            rng,
            weight_sums,
            target_weight,
        )
        group_counts[chosen] += 1
        cage_counts[chosen][str(animal.cage or "NA")] += 1
        if animal.weight is not None and isfinite(float(animal.weight)):
            weight_sums[chosen] += float(animal.weight)
        assignments.append(AssignmentRecord(animal_id=animal.animal_id, group=chosen))
    return assignments


def _build_blocks(
    animals: List[AnimalRecord],
    cfg: RandomizationConfig,
    rng: random.Random,
) -> List[List[AnimalRecord]]:
    blocks: List[List[AnimalRecord]] = []
    idx = 0
    while idx < len(animals):
        if cfg.random_block_sizes:
            size = rng.choice(cfg.random_block_sizes)
        else:
            size = cfg.block_size or len(cfg.group_names)
        block = animals[idx : idx + size]
        blocks.append(block)
        idx += size
    return blocks


def randomize(animals: List[AnimalRecord], cfg: RandomizationConfig) -> tuple[List[AssignmentRecord], int]:
    seed = cfg.seed if cfg.seed is not None else secrets.randbelow(2**31 - 1)
    rng = random.Random(seed)

    method = cfg.method.lower()
    if method == "simple":
        constrained = (
            cfg.constraints.weight_balance
            or cfg.constraints.minimize_cage_clustering
            or cfg.constraints.max_animals_per_cage_per_group is not None
        )
        if constrained:
            # A constrained sequential allocation is deliberately used rather
            # than silently claiming that simple randomization honoured a
            # balance/cage constraint it did not implement.
            return _assign_balanced(list(animals), cfg.group_names, cfg.constraints, rng), seed
        shuffled = list(animals)
        rng.shuffle(shuffled)
        assignments = [
            AssignmentRecord(animal_id=a.animal_id, group=cfg.group_names[idx % len(cfg.group_names)])
            for idx, a in enumerate(shuffled)
        ]
        return assignments, seed

    if method == "balanced":
        return _assign_balanced(list(animals), cfg.group_names, cfg.constraints, rng), seed

    if method == "stratified":
        strata: Dict[str, List[AnimalRecord]] = defaultdict(list)
        for animal in animals:
            strata[_stratum_key(animal, cfg.stratify_by, cfg.constraints.weight_balance)].append(animal)
        combined: List[AssignmentRecord] = []
        shared_cage_counts: Dict[str, Dict[str, int]] = {
            g: defaultdict(int) for g in cfg.group_names
        }
        for _, rows in sorted(strata.items(), key=lambda x: x[0]):
            combined.extend(
                _assign_balanced(
                    rows,
                    cfg.group_names,
                    cfg.constraints,
                    rng,
                    shared_cage_counts,
                )
            )
        return combined, seed

    if method == "block":
        staged = list(animals)
        rng.shuffle(staged)
        blocks = _build_blocks(staged, cfg, rng)
        combined: List[AssignmentRecord] = []
        shared_cage_counts: Dict[str, Dict[str, int]] = {
            g: defaultdict(int) for g in cfg.group_names
        }
        for block in blocks:
            combined.extend(
                _assign_balanced(
                    block,
                    cfg.group_names,
                    cfg.constraints,
                    rng,
                    shared_cage_counts,
                )
            )
        return combined, seed

    raise ValueError(f"Unknown randomization method: {cfg.method}")
