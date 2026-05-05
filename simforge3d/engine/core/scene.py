"""Scene management for simulation objects and agents."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from simforge3d.engine.core.config import SimulationConfig
from simforge3d.engine.core.types import Vector3, WorldObject


class SceneManager:
    """Owns mutable world state and keeps it independent from rendering."""

    def __init__(self, config: SimulationConfig | None = None) -> None:
        self.config = config or SimulationConfig()
        self.objects: dict[str, WorldObject] = {}
        self.agents: dict[str, Any] = {}
        self.step_count = 0
        self.elapsed_time = 0.0
        self.last_events: list[dict[str, Any]] = []
        self.panda_root: Any | None = None

    def clear(self) -> None:
        self.objects.clear()
        self.agents.clear()
        self.step_count = 0
        self.elapsed_time = 0.0
        self.last_events.clear()

    def emit_event(self, event_type: str, **payload: Any) -> None:
        self.last_events.append({"type": event_type, **payload})

    def add_object(self, obj: WorldObject) -> WorldObject:
        if obj.object_id in self.objects:
            raise ValueError(f"Duplicate object_id: {obj.object_id}")
        self.objects[obj.object_id] = obj
        return obj

    def remove_object(self, object_id: str) -> WorldObject:
        return self.objects.pop(object_id)

    def add_agent(self, agent: Any) -> Any:
        if agent.agent_id in self.agents:
            raise ValueError(f"Duplicate agent_id: {agent.agent_id}")
        self.agents[agent.agent_id] = agent
        return agent

    def get_agent(self, agent_id: str) -> Any:
        return self.agents[agent_id]

    def add_floor(self, object_id: str = "floor", size: float = 40.0) -> WorldObject:
        return self.add_object(
            WorldObject(
                object_id=object_id,
                kind="floor",
                position=Vector3(0.0, 0.0, -0.05),
                radius=size / 2.0,
                height=0.1,
                collidable=False,
                metadata={"size": size},
            )
        )

    def add_obstacles(self, positions: Iterable[Iterable[float]], radius: float = 0.6) -> list[WorldObject]:
        obstacles: list[WorldObject] = []
        for idx, position in enumerate(positions):
            obstacles.append(
                self.add_object(
                    WorldObject(
                        object_id=f"obstacle_{idx}",
                        kind="obstacle",
                        position=Vector3.from_iterable(position),
                        radius=radius,
                        height=1.0,
                        collidable=True,
                    )
                )
            )
        return obstacles

    def nearby_objects(
        self,
        position: Vector3,
        radius: float,
        *,
        include_held: bool = False,
    ) -> list[WorldObject]:
        objects = []
        for obj in self.objects.values():
            if obj.held_by and not include_held:
                continue
            if position.distance_xy(obj.position) <= radius:
                objects.append(obj)
        return sorted(objects, key=lambda item: position.distance_xy(item.position))

    def environment_state(self) -> dict[str, Any]:
        return {
            "step_count": self.step_count,
            "elapsed_time": self.elapsed_time,
            "object_count": len(self.objects),
            "agent_count": len(self.agents),
        }

    def update(self, dt: float) -> None:
        self.step_count += 1
        self.elapsed_time += dt
        for agent in self.agents.values():
            held_object_id = getattr(agent, "held_object_id", None)
            if held_object_id and held_object_id in self.objects:
                held = self.objects[held_object_id]
                forward = Vector3.forward_from_yaw(agent.yaw_degrees)
                held.position = agent.position + forward.scale(agent.radius + held.radius + 0.25)
                held.position.z = max(held.position.z, 0.25)

    def snapshot(self) -> dict[str, Any]:
        return {
            "step_count": self.step_count,
            "elapsed_time": self.elapsed_time,
            "objects": {object_id: obj.to_dict() for object_id, obj in self.objects.items()},
            "agents": {agent_id: agent.state().to_dict() for agent_id, agent in self.agents.items()},
        }
