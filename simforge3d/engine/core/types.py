"""Serializable core state types used by the simulation engine."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from math import cos, hypot, radians, sin
from typing import Any


@dataclass(slots=True)
class Vector3:
    """Small dependency-free 3D vector for simulation state."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    @classmethod
    def zero(cls) -> Vector3:
        return cls(0.0, 0.0, 0.0)

    @classmethod
    def from_iterable(cls, value: Iterable[float] | Vector3) -> Vector3:
        if isinstance(value, Vector3):
            return value.copy()
        items = list(value)
        if len(items) != 3:
            raise ValueError(f"Vector3 requires exactly 3 values, got {len(items)}")
        return cls(float(items[0]), float(items[1]), float(items[2]))

    @classmethod
    def forward_from_yaw(cls, yaw_degrees: float) -> Vector3:
        angle = radians(yaw_degrees)
        return cls(sin(angle), cos(angle), 0.0)

    def copy(self) -> Vector3:
        return Vector3(self.x, self.y, self.z)

    def as_tuple(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)

    def to_list(self) -> list[float]:
        return [self.x, self.y, self.z]

    def distance_xy(self, other: Vector3) -> float:
        return hypot(self.x - other.x, self.y - other.y)

    def length_xy(self) -> float:
        return hypot(self.x, self.y)

    def normalized_xy(self) -> Vector3:
        length = self.length_xy()
        if length == 0:
            return Vector3.zero()
        return Vector3(self.x / length, self.y / length, 0.0)

    def scale(self, scalar: float) -> Vector3:
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __add__(self, other: Vector3) -> Vector3:
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Vector3) -> Vector3:
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)


@dataclass(slots=True)
class WorldObject:
    """Object in the simulation world."""

    object_id: str
    kind: str
    position: Vector3
    radius: float = 0.5
    height: float = 1.0
    pickupable: bool = False
    collidable: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    held_by: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "object_id": self.object_id,
            "kind": self.kind,
            "position": self.position.to_list(),
            "radius": self.radius,
            "height": self.height,
            "pickupable": self.pickupable,
            "collidable": self.collidable,
            "metadata": dict(self.metadata),
            "held_by": self.held_by,
        }


@dataclass(slots=True)
class AgentState:
    """Serializable snapshot of an agent."""

    agent_id: str
    position: Vector3
    yaw_degrees: float = 0.0
    radius: float = 0.35
    held_object_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "position": self.position.to_list(),
            "yaw_degrees": self.yaw_degrees,
            "radius": self.radius,
            "held_object_id": self.held_object_id,
            "metadata": dict(self.metadata),
        }
