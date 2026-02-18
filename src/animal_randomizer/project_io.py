from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict

from .models import (
    AnimalRecord,
    AssignmentRecord,
    AuditEvent,
    ConstraintConfig,
    ProjectModel,
    RandomizationConfig,
    StudyMetadata,
)


def save_project(project: ProjectModel, path: str | Path) -> None:
    payload = asdict(project)
    path = Path(path)
    if path.suffix.lower() != ".nprj":
        path = path.with_suffix(".nprj")
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def load_project(path: str | Path) -> ProjectModel:
    payload: Dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))

    metadata = StudyMetadata(**payload["metadata"])
    animals = [AnimalRecord(**x) for x in payload.get("animals", [])]
    c = payload.get("config", {})
    constraints = ConstraintConfig(**c.get("constraints", {}))
    config = RandomizationConfig(
        method=c["method"],
        group_names=list(c["group_names"]),
        seed=c.get("seed"),
        stratify_by=list(c.get("stratify_by", [])),
        block_size=c.get("block_size"),
        random_block_sizes=list(c.get("random_block_sizes", [])),
        constraints=constraints,
        algorithm_version=c.get("algorithm_version", "1.0.0"),
    )

    model = ProjectModel(
        metadata=metadata,
        animals=animals,
        config=config,
        groups=list(payload.get("groups", [])),
        audit_log=[AuditEvent(**x) for x in payload.get("audit_log", [])],
        assignments=[AssignmentRecord(**x) for x in payload.get("assignments", [])],
        stats=payload.get("stats", {}),
        warnings=list(payload.get("warnings", [])),
        hashes=payload.get("hashes", {}),
        software_version=payload.get("software_version", "0.3.0"),
        build_date=payload.get("build_date", ""),
    )
    return model
