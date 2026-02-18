from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone

from .audit import AuditLogger
from .hashing import sha256_of
from .models import ProjectModel, RandomizationArtifacts
from .randomization import randomize
from .stats import compute_statistics
from .validation import validate_animals


class RandomizerService:
    def __init__(self) -> None:
        self.audit = AuditLogger()

    def run(self, project: ProjectModel) -> RandomizationArtifacts:
        validate_animals(project.animals)
        self.audit.record("validation", {"animals": len(project.animals)})

        assignments, seed = randomize(project.animals, project.config)
        project.config.seed = seed
        self.audit.record("randomization", {"method": project.config.method, "seed": seed})

        stats, warnings = compute_statistics(project.animals, assignments)
        input_hash = sha256_of([asdict(a) for a in project.animals])
        config_hash = sha256_of(asdict(project.config))
        output_hash = sha256_of([asdict(a) for a in assignments])

        project.assignments = assignments
        project.stats = stats
        project.warnings = warnings
        project.hashes = {
            "input_hash": input_hash,
            "config_hash": config_hash,
            "output_hash": output_hash,
        }
        project.audit_log.extend(self.audit.events())

        return RandomizationArtifacts(
            assignments=assignments,
            stats=stats,
            warnings=warnings,
            seed=seed,
            hashes=project.hashes,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )
