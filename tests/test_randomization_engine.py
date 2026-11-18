from __future__ import annotations

from collections import Counter

import pytest

from animal_randomizer.models import AnimalRecord, AssignmentRecord, ConstraintConfig, RandomizationConfig
from animal_randomizer.io_handlers import export_blinding_files
from animal_randomizer.randomization import randomize
from animal_randomizer.service import RandomizerService
from animal_randomizer.models import ProjectModel, StudyMetadata
from animal_randomizer.validation import run_qc_gate, validate_animals, validate_config
from animal_randomizer.report import generate_html_report


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


def test_sex_normalization_accepts_common_values():
    animals = [
        AnimalRecord("A1", sex="m"),
        AnimalRecord("A2", sex=" FEMALE "),
        AnimalRecord("A3", sex="na"),
    ]
    validate_animals(animals)
    assert animals[0].sex == "M"
    assert animals[1].sex == "F"
    assert animals[2].sex is None


def test_qc_gate_blocks_missing_required_fields():
    animals = [
        AnimalRecord("A1", sex="M", weight=200.0, cage="C1"),
        AnimalRecord("A2", sex=None, weight=None, cage=None),
    ]
    cfg = RandomizationConfig(
        method="stratified",
        group_names=["Ctl", "Drug"],
        stratify_by=["sex", "weight", "cage"],
        constraints=ConstraintConfig(weight_balance=True, minimize_cage_clustering=True),
    )
    try:
        run_qc_gate(animals, cfg)
        assert False, "Expected QC gate to fail for missing sex/weight/cage."
    except ValueError as exc:
        msg = str(exc)
        assert "Sex is required" in msg
        assert "Weight is required" in msg
        assert "Cage is required" in msg


def test_blinding_exports_are_generated(tmp_path):
    assignments = [
        AssignmentRecord(animal_id="A1", group="Ctl"),
        AssignmentRecord(animal_id="A2", group="Drug"),
    ]
    paths = export_blinding_files(assignments, output_dir=tmp_path, seed=123, stem="alloc")
    assert paths["blinded"].exists()
    assert paths["blinding_key"].exists()


def test_infeasible_cage_constraint_fails_closed():
    animals = [
        AnimalRecord("A1", cage="C1"),
        AnimalRecord("A2", cage="C1"),
        AnimalRecord("A3", cage="C1"),
    ]
    cfg = RandomizationConfig(
        method="balanced",
        group_names=["G1", "G2"],
        seed=1,
        constraints=ConstraintConfig(max_animals_per_cage_per_group=1),
    )
    try:
        randomize(animals, cfg)
        assert False, "Expected infeasible cage constraint to fail closed."
    except ValueError as exc:
        assert "No feasible group remains" in str(exc)


def test_config_rejects_duplicate_groups_and_invalid_blocks():
    with pytest.raises(ValueError, match="unique"):
        validate_config(RandomizationConfig(method="balanced", group_names=["A", "A"]))
    with pytest.raises(ValueError, match="multiple"):
        validate_config(
            RandomizationConfig(method="block", group_names=["A", "B", "C"], block_size=4)
        )


def test_html_report_escapes_user_content_and_qualifies_constraints(tmp_path):
    meta = StudyMetadata(
        study_id="<study>",
        title="Title & details",
        researcher_name="Researcher",
        institution="Institution",
    )
    cfg = RandomizationConfig(
        method="balanced",
        group_names=["A <unsafe>", "B"],
        seed=3,
        constraints=ConstraintConfig(weight_balance=True),
    )
    project = ProjectModel(
        metadata=meta,
        animals=[AnimalRecord("A1")],
        config=cfg,
        groups=cfg.group_names,
        assignments=[AssignmentRecord("A1", "A <unsafe>")],
        warnings=["warning <tag>"],
    )
    path = generate_html_report(project, tmp_path / "report.html")
    html = path.read_text(encoding="utf-8")
    assert "<study>" not in html
    assert "&lt;study&gt;" in html
    assert "warning &lt;tag&gt;" in html
    assert "configuration specified" in html
