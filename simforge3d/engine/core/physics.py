"""Deterministic lightweight physics and collision handling."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from simforge3d.engine.core.config import SimulationConfig
from simforge3d.engine.core.scene import SceneManager
from simforge3d.engine.core.types import Vector3, WorldObject


@runtime_checkable
class SimAgent(Protocol):
    """Structural interface for agents used by the physics system."""

    agent_id: str
    position: Vector3
    yaw_degrees: float
    radius: float
    held_object_id: str | None


class PhysicsSystem:
    """Simple XY-plane physics used for fast RL training loops.

    Panda3D can still render the world, but simulation state remains deterministic
    and testable without a graphics context.
    """

    def __init__(self, config: SimulationConfig | None = None) -> None:
        self.config = config or SimulationConfig()

    def try_move_agent(self, agent: SimAgent, scene: SceneManager, delta: Vector3) -> bool:
        current = agent.position
        candidate = current + delta
        if not self._within_bounds(candidate, agent.radius):
            scene.emit_event("collision", agent_id=agent.agent_id, object_id="world_bounds")
            return False

        for obj in scene.objects.values():
            if not obj.collidable or obj.held_by is not None:
                continue
            if candidate.distance_xy(obj.position) < agent.radius + obj.radius:
                scene.emit_event("collision", agent_id=agent.agent_id, object_id=obj.object_id)
                return False

        for other in scene.agents.values():
            if other is agent:
                continue
            if candidate.distance_xy(other.position) < agent.radius + other.radius:
                scene.emit_event(
                    "agent_collision", agent_id=agent.agent_id, other_agent_id=other.agent_id
                )
                return False

        agent.position = candidate
        scene.emit_event("move", agent_id=agent.agent_id, position=candidate.to_list())
        return True

    def try_pickup(
        self, agent: SimAgent, scene: SceneManager, *, interact_radius: float = 1.25
    ) -> bool:
        if agent.held_object_id:
            return False
        candidates = [
            obj
            for obj in scene.objects.values()
            if obj.pickupable
            and obj.held_by is None
            and obj.position.distance_xy(agent.position) <= interact_radius
        ]
        if not candidates:
            scene.emit_event("pickup_failed", agent_id=agent.agent_id)
            return False
        target = min(candidates, key=lambda obj: obj.position.distance_xy(agent.position))
        target.held_by = agent.agent_id
        agent.held_object_id = target.object_id
        scene.emit_event("pickup", agent_id=agent.agent_id, object_id=target.object_id)
        return True

    def drop(self, agent: SimAgent, scene: SceneManager, *, distance: float = 0.85) -> bool:
        object_id = agent.held_object_id
        if not object_id or object_id not in scene.objects:
            scene.emit_event("drop_failed", agent_id=agent.agent_id)
            return False

        obj = scene.objects[object_id]
        forward = Vector3.forward_from_yaw(agent.yaw_degrees)
        candidate = agent.position + forward.scale(distance + obj.radius)
        candidate.z = max(candidate.z, obj.radius)
        if not self._within_bounds(candidate, obj.radius):
            scene.emit_event("drop_failed", agent_id=agent.agent_id, reason="world_bounds")
            return False

        if self._object_would_collide(obj, candidate, scene):
            scene.emit_event("drop_failed", agent_id=agent.agent_id, reason="collision")
            return False

        obj.position = candidate
        obj.held_by = None
        agent.held_object_id = None
        scene.emit_event(
            "drop", agent_id=agent.agent_id, object_id=obj.object_id, position=candidate.to_list()
        )
        return True

    def _within_bounds(self, position: Vector3, radius: float) -> bool:
        min_x, max_x, min_y, max_y = self.config.world_bounds
        return (
            min_x + radius <= position.x <= max_x - radius
            and min_y + radius <= position.y <= max_y - radius
        )

    @staticmethod
    def _object_would_collide(obj: WorldObject, candidate: Vector3, scene: SceneManager) -> bool:
        for other in scene.objects.values():
            if (
                other.object_id == obj.object_id
                or not other.collidable
                or other.held_by is not None
            ):
                continue
            if candidate.distance_xy(other.position) < obj.radius + other.radius:
                return True
        return False
