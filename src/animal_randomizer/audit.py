from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, List

from .models import AuditEvent


class AuditLogger:
    def __init__(self) -> None:
        self._events: List[AuditEvent] = []

    def record(self, action: str, details: Dict[str, Any]) -> None:
        self._events.append(
            AuditEvent(
                timestamp=datetime.now(timezone.utc).isoformat(),
                action=action,
                details=details,
            )
        )

    def events(self) -> List[AuditEvent]:
        return list(self._events)

    def as_json(self) -> List[Dict[str, Any]]:
        return [asdict(event) for event in self._events]
