from __future__ import annotations

from collections import Counter

from animal_randomizer.models import AnimalRecord, ConstraintConfig, RandomizationConfig
from animal_randomizer.randomization import randomize
from animal_randomizer.service import RandomizerService
from animal_randomizer.models import ProjectModel, StudyMetadata


def sample_animals(n: int = 24):
    rows = []
    for i in range(1, n + 1):
        rows.append(
            AnimalRecord(
                animal_id=f"RAT_{i:03d}",
                sex="M" if i % 2 else "F",
                weight=240 + (i % 7) * 3,
                cage=f"C{((i - 1) // 3) + 1}",
                age=10 + (i % 4),
            )
        )
    return rows


def test_seed_reproducibility():
    cfg = RandomizationConfig(method="balanced", group_names=["A", "B"], seed=42)
    animals = sample_animals()
    out1, seed1 = randomize(animals, cfg)
    out2, seed2 = randomize(animals, cfg)
    assert seed1 == 42
    assert seed2 == 42
    assert [(x.animal_id, x.group) for x in out1] == [(x.animal_id, x.group) for x in out2]


def test_balanced_sizes():
    cfg = RandomizationConfig(method="balanced", group_names=["A", "B", "C"], seed=7)
    assignments, _ = randomize(sample_animals(25), cfg)
    c = Counter(x.group for x in assignments)
    assert max(c.values()) - min(c.values()) <= 1


def test_cage_constraint_max_one_per_group_in_small_case():
    animals = [
        AnimalRecord("A1", cage="C1"),
        AnimalRecord("A2", cage="C1"),
        AnimalRecord("A3", cage="C2"),
        AnimalRecord("A4", cage="C2"),
    ]
    cfg = RandomizationConfig(
        method="balanced",
        group_names=["G1", "G2"],
        seed=1,
        constraints=ConstraintConfig(max_animals_per_cage_per_group=1, minimize_cage_clustering=True, weight_balance=False),
    )
    assignments, _ = randomize(animals, cfg)
    group_cage = Counter((x.group, next(a.cage for a in animals if a.animal_id == x.animal_id)) for x in assignments)
    assert max(group_cage.values()) <= 1


def test_service_produces_hashes_and_stats():
    meta = StudyMetadata(study_id="T1", title="Title", researcher_name="R", institution="I")
    cfg = RandomizationConfig(method="stratified", group_names=["Ctl", "Drug"], seed=12, stratify_by=["sex", "weight"])
    project = ProjectModel(metadata=meta, animals=sample_animals(20), config=cfg, groups=cfg.group_names)

    out = RandomizerService().run(project)

    assert out.hashes["input_hash"]
    assert out.hashes["config_hash"]
    assert out.hashes["output_hash"]
    assert "groups" in out.stats
