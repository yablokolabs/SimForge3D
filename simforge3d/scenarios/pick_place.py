"""Pick-and-place object interaction scenario."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from simforge3d.agent.base import BaseAgent
from simforge3d.engine.core.scene import SceneManager
from simforge3d.engine.core.types import Vector3, WorldObject
from simforge3d.scenarios.base import BaseScenario


@dataclass
class PickPlaceScenario(BaseScenario):
    start_position: tuple[float, float, float] | Vector3 = (0.0, 0.0, 0.0)
    object_position: tuple[float, float, float] | Vector3 = (1.0, 0.0, 0.2)
    goal_position: tuple[float, float, float] | Vector3 = (4.0, 0.0, 0.0)
    obstacles: list[Iterable[float]] = field(default_factory=list)
    goal_radius: float = 0.75
    step_penalty: float = -0.01
    pickup_reward: float = 1.0
    success_reward: float = 15.0
    progress_reward_scale: float = 0.5
    primary_agent_id: str = "agent_0"
    object_id: str = "payload"
    max_steps: int | None = None
    name: str = "pick_place"

    def __post_init__(self) -> None:
        self._goal = Vector3.from_iterable(self.goal_position)
        self._previous_distance: float | None = None

    def setup(self, scene: SceneManager) -> None:
        scene.add_floor()
        scene.add_agent(
            BaseAgent(
                self.primary_agent_id,
                position=Vector3.from_iterable(self.start_position),
                yaw_degrees=90.0,
            )
        )
        scene.add_object(
            WorldObject(
                object_id=self.object_id,
                kind="pickup_object",
                position=Vector3.from_iterable(self.object_position),
                radius=0.25,
                height=0.5,
                pickupable=True,
                collidable=False,
            )
        )
        scene.add_object(
            WorldObject(
                object_id="goal",
                kind="goal",
                position=self._goal.copy(),
                radius=self.goal_radius,
                height=0.1,
                collidable=False,
            )
        )
        scene.add_obstacles(self.obstacles, radius=0.5)

    def on_reset(self, scene: SceneManager) -> None:
        self._previous_distance = self._task_distance(scene)

    def success(self, scene: SceneManager) -> bool:
        obj = scene.objects[self.object_id]
        return obj.held_by is None and obj.position.distance_xy(self._goal) <= self.goal_radius

    def reward(self, scene: SceneManager) -> float:
        distance = self._task_distance(scene)
        previous = self._previous_distance if self._previous_distance is not None else distance
        reward = self.step_penalty + self.progress_reward_scale * (previous - distance)
        event_types = {event["type"] for event in scene.last_events}
        if "pickup" in event_types:
            reward += self.pickup_reward
        if self.success(scene):
            reward += self.success_reward
        self._previous_distance = distance
        return reward

    def info(self, scene: SceneManager) -> dict[str, object]:
        obj = scene.objects[self.object_id]
        return {
            "scenario": self.name,
            "object_position": obj.position.to_list(),
            "goal_position": self._goal.to_list(),
            "object_held_by": obj.held_by,
            "distance_to_goal": obj.position.distance_xy(self._goal),
        }

    def _task_distance(self, scene: SceneManager) -> float:
        agent = scene.get_agent(self.primary_agent_id)
        obj = scene.objects[self.object_id]
        if agent.held_object_id == self.object_id:
            return agent.position.distance_xy(self._goal)
        return agent.position.distance_xy(obj.position) + obj.position.distance_xy(self._goal)
