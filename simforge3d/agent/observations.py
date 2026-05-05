"""Observation models returned to AI agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AgentObservation:
    agent_id: str
    position: tuple[float, float, float]
    yaw_degrees: float
    held_object_id: str | None
    nearby_objects: list[dict[str, Any]] = field(default_factory=list)
    environment_state: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "position": list(self.position),
            "yaw_degrees": self.yaw_degrees,
            "held_object_id": self.held_object_id,
            "nearby_objects": self.nearby_objects,
            "environment_state": self.environment_state,
        }
