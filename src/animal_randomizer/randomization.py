from __future__ import annotations

import random
import secrets
from collections import defaultdict
from typing import Dict, List

from .models import AnimalRecord, AssignmentRecord, ConstraintConfig, RandomizationConfig


def _normalize_sex(sex: str | None) -> str:
    if sex in ("M", "Male"):
        return "M"
    if sex in ("F", "Female"):
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
        if limited:
            candidates = limited

    if constraints.minimize_cage_clustering:
        min_cage = min(cage_counts[g][cage] for g in candidates)
        candidates = [g for g in candidates if cage_counts[g][cage] == min_cage]

    return rng.choice(candidates)


def _assign_balanced(
    animals: List[AnimalRecord],
    group_names: List[str],
    constraints: ConstraintConfig,
    rng: random.Random,
) -> List[AssignmentRecord]:
    assignments: List[AssignmentRecord] = []
    group_counts = {g: 0 for g in group_names}
    cage_counts: Dict[str, Dict[str, int]] = {g: defaultdict(int) for g in group_names}

    rng.shuffle(animals)
    for animal in animals:
        chosen = _choose_group(animal, group_names, group_counts, cage_counts, constraints, rng)
        group_counts[chosen] += 1
        cage_counts[chosen][str(animal.cage or "NA")] += 1
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
        for _, rows in sorted(strata.items(), key=lambda x: x[0]):
            combined.extend(_assign_balanced(rows, cfg.group_names, cfg.constraints, rng))
        return combined, seed

    if method == "block":
        staged = list(animals)
        rng.shuffle(staged)
        blocks = _build_blocks(staged, cfg, rng)
        combined: List[AssignmentRecord] = []
        for block in blocks:
            combined.extend(_assign_balanced(block, cfg.group_names, cfg.constraints, rng))
        return combined, seed

    raise ValueError(f"Unknown randomization method: {cfg.method}")
