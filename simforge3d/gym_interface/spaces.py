"""Lightweight fallback observation spaces."""

from __future__ import annotations

from typing import Any


class ObservationSpace:
    """Structural validator for SimForge3D observations."""

    required_keys = {"agent_id", "position", "yaw_degrees", "nearby_objects", "environment_state"}

    def contains(self, value: object) -> bool:
        if not isinstance(value, dict):
            return False
        if self.required_keys.issubset(value):
            return True
        return all(isinstance(item, dict) and self.required_keys.issubset(item) for item in value.values())

    def sample(self) -> dict[str, Any]:
        return {
            "agent_id": "agent_0",
            "position": [0.0, 0.0, 0.0],
            "yaw_degrees": 0.0,
            "held_object_id": None,
            "nearby_objects": [],
            "environment_state": {"step_count": 0, "elapsed_time": 0.0},
        }

    def __repr__(self) -> str:
        return "ObservationSpace(SimForge3DDict)"
