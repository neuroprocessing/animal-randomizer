from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class AnimalRecord:
    animal_id: str
    sex: Optional[str] = None
    weight: Optional[float] = None
    age: Optional[float] = None
    cage: Optional[str] = None
    strain: Optional[str] = None
    species: Optional[str] = None
    notes: Optional[str] = None
    source: Optional[str] = None
    date_of_arrival: Optional[str] = None


@dataclass(slots=True)
class StudyMetadata:
    study_id: str
    title: str
    researcher_name: str
    institution: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(slots=True)
class ConstraintConfig:
    max_animals_per_cage_per_group: Optional[int] = None
    minimize_cage_clustering: bool = True
    weight_balance: bool = True


@dataclass(slots=True)
class RandomizationConfig:
    method: str
    group_names: List[str]
    seed: Optional[int] = None
    stratify_by: List[str] = field(default_factory=list)
    block_size: Optional[int] = None
    random_block_sizes: List[int] = field(default_factory=list)
    constraints: ConstraintConfig = field(default_factory=ConstraintConfig)
    algorithm_version: str = "1.0.0"


@dataclass(slots=True)
class AssignmentRecord:
    animal_id: str
    group: str


@dataclass(slots=True)
class RandomizationArtifacts:
    assignments: List[AssignmentRecord]
    stats: Dict[str, Any]
    warnings: List[str]
    seed: int
    hashes: Dict[str, str]
    generated_at: str


@dataclass(slots=True)
class AuditEvent:
    timestamp: str
    action: str
    details: Dict[str, Any]


@dataclass(slots=True)
class ProjectModel:
    metadata: StudyMetadata
    animals: List[AnimalRecord]
    config: RandomizationConfig
    groups: List[str]
    audit_log: List[AuditEvent] = field(default_factory=list)
    assignments: List[AssignmentRecord] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    hashes: Dict[str, str] = field(default_factory=dict)
    software_version: str = "0.3.0"
    build_date: str = field(default_factory=lambda: datetime.now(timezone.utc).date().isoformat())
