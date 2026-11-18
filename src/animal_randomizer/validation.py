from __future__ import annotations

from math import isfinite
from typing import Iterable

from .models import AnimalRecord, AssignmentRecord, RandomizationConfig


SUPPORTED_METHODS = {"simple", "balanced", "stratified", "block"}
SUPPORTED_STRATA = {"sex", "cage", "weight", "age"}


def normalize_sex_value(value: str | None) -> str | None:
    """Normalize sex values to canonical form used across the project."""
    if value is None:
        return None
    cleaned = str(value).strip()
    if not cleaned:
        return None

    lowered = cleaned.lower()
    if lowered in {"m", "male"}:
        return "M"
    if lowered in {"f", "female"}:
        return "F"
    if lowered in {"na", "n/a", "none", "unknown", "u", "-"}:
        return None
    raise ValueError(f"invalid sex value: {value}")


def validate_animals(animals: Iterable[AnimalRecord]) -> None:
    seen: set[str] = set()
    for idx, animal in enumerate(animals, start=1):
        animal.animal_id = str(animal.animal_id).strip()
        if not animal.animal_id:
            raise ValueError(f"Animal at row {idx} has empty Animal ID")
        if animal.animal_id in seen:
            raise ValueError(f"Duplicate Animal ID detected: {animal.animal_id}")
        seen.add(animal.animal_id)
        if animal.weight is not None:
            try:
                weight = float(animal.weight)
            except (TypeError, ValueError):
                raise ValueError(f"Animal {animal.animal_id} has a non-numeric weight") from None
            if not isfinite(weight) or weight <= 0:
                raise ValueError(f"Animal {animal.animal_id} has a non-positive or non-finite weight")
            animal.weight = weight
        if animal.age is not None:
            try:
                age = float(animal.age)
            except (TypeError, ValueError):
                raise ValueError(f"Animal {animal.animal_id} has a non-numeric age") from None
            if not isfinite(age) or age < 0:
                raise ValueError(f"Animal {animal.animal_id} has a negative or non-finite age")
            animal.age = age
        try:
            animal.sex = normalize_sex_value(animal.sex)
        except ValueError:
            raise ValueError(f"Animal {animal.animal_id} has invalid sex value: {animal.sex}") from None


def validate_config(config: RandomizationConfig) -> None:
    """Validate configuration before any random state is consumed."""
    method = str(config.method).strip().lower()
    if method not in SUPPORTED_METHODS:
        raise ValueError(f"Unknown randomization method: {config.method}")

    groups = [str(group).strip() for group in config.group_names]
    if len(groups) < 2:
        raise ValueError("At least two non-empty groups are required.")
    if any(not group for group in groups):
        raise ValueError("Group names must be non-empty.")
    if len(set(groups)) != len(groups):
        raise ValueError("Group names must be unique.")

    strata = [str(value).strip().lower() for value in config.stratify_by]
    unknown = sorted(set(strata) - SUPPORTED_STRATA)
    if unknown:
        raise ValueError(f"Unknown stratification field(s): {', '.join(unknown)}")
    if len(set(strata)) != len(strata):
        raise ValueError("Stratification fields must be unique.")

    maximum = config.constraints.max_animals_per_cage_per_group
    if maximum is not None and maximum < 1:
        raise ValueError("max_animals_per_cage_per_group must be a positive integer.")

    if method == "block":
        n_groups = len(groups)
        if config.block_size is not None and config.random_block_sizes:
            raise ValueError("Specify block_size or random_block_sizes, not both.")
        if config.block_size is not None:
            if config.block_size < n_groups or config.block_size % n_groups:
                raise ValueError("block_size must be a positive multiple of the number of groups.")
        if config.random_block_sizes:
            invalid = [size for size in config.random_block_sizes if size < n_groups or size % n_groups]
            if invalid:
                raise ValueError("Every random block size must be a multiple of the number of groups.")
        if config.block_size is None and not config.random_block_sizes:
            raise ValueError("Block method selected but no block size configuration was provided.")


def validate_assignments(
    animals: Iterable[AnimalRecord],
    assignments: Iterable[AssignmentRecord],
    config: RandomizationConfig,
) -> None:
    """Fail closed if an engine ever emits a malformed allocation."""
    animal_ids = [animal.animal_id for animal in animals]
    rows = list(assignments)
    assigned_ids = [row.animal_id for row in rows]
    if len(rows) != len(animal_ids):
        raise ValueError("Allocation does not contain exactly one row per animal.")
    if len(set(assigned_ids)) != len(assigned_ids):
        raise ValueError("Allocation contains duplicate animal IDs.")
    if set(assigned_ids) != set(animal_ids):
        raise ValueError("Allocation IDs do not match the input animal IDs.")
    allowed = set(config.group_names)
    invalid = sorted({row.group for row in rows} - allowed)
    if invalid:
        raise ValueError(f"Allocation contains unknown group(s): {', '.join(invalid)}")


def validate_constraints(
    animals: Iterable[AnimalRecord],
    assignments: Iterable[AssignmentRecord],
    config: RandomizationConfig,
) -> None:
    """Verify hard constraints after allocation, including across strata/blocks."""
    maximum = config.constraints.max_animals_per_cage_per_group
    if maximum is None:
        return
    animal_map = {animal.animal_id: animal for animal in animals}
    counts: dict[tuple[str, str], int] = {}
    for row in assignments:
        cage = str(animal_map[row.animal_id].cage or "NA")
        key = (row.group, cage)
        counts[key] = counts.get(key, 0) + 1
    violations = {
        key: count for key, count in counts.items() if count > maximum
    }
    if violations:
        detail = ", ".join(f"{group}/{cage}={count}" for (group, cage), count in sorted(violations.items()))
        raise ValueError(f"Hard cage constraint violated after allocation: {detail}")


def run_qc_gate(animals: Iterable[AnimalRecord], config: RandomizationConfig) -> None:
    """
    Run pre-randomization QC checks tied to configured strategy/constraints.
    Blocks execution when required balancing fields are missing.
    """
    rows = list(animals)
    validate_config(config)
    stratify = {s.strip().lower() for s in config.stratify_by}
    needs_sex = "sex" in stratify
    needs_weight = "weight" in stratify or config.constraints.weight_balance
    needs_cage = (
        "cage" in stratify
        or config.constraints.minimize_cage_clustering
        or config.constraints.max_animals_per_cage_per_group is not None
    )

    missing_sex = [a.animal_id for a in rows if not a.sex]
    missing_weight = [a.animal_id for a in rows if a.weight is None]
    missing_cage = [a.animal_id for a in rows if not a.cage]

    errors: list[str] = []
    if needs_sex and missing_sex:
        errors.append(
            f"Sex is required by current settings; missing for {len(missing_sex)} animals "
            f"(examples: {', '.join(missing_sex[:5])})."
        )
    if needs_weight and missing_weight:
        errors.append(
            f"Weight is required by current settings; missing for {len(missing_weight)} animals "
            f"(examples: {', '.join(missing_weight[:5])})."
        )
    if needs_cage and missing_cage:
        errors.append(
            f"Cage is required by current settings; missing for {len(missing_cage)} animals "
            f"(examples: {', '.join(missing_cage[:5])})."
        )

    if config.method.lower() == "block":
        if config.block_size is None and not config.random_block_sizes:
            errors.append("Block method selected but no block size configuration was provided.")

    if errors:
        joined = "\n- ".join(errors)
        raise ValueError(f"QC gate failed:\n- {joined}")
