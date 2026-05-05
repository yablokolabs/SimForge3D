"""Reach-target navigation scenario."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from simforge3d.agent.base import BaseAgent
from simforge3d.engine.core.scene import SceneManager
from simforge3d.engine.core.types import Vector3, WorldObject
from simforge3d.scenarios.base import BaseScenario


@dataclass
class NavigationScenario(BaseScenario):
    target_position: tuple[float, float, float] | Vector3 = (5.0, 5.0, 0.0)
    start_position: tuple[float, float, float] | Vector3 = (0.0, 0.0, 0.0)
    start_yaw_degrees: float = 45.0
    obstacles: list[Iterable[float]] = field(
        default_factory=lambda: [(2.0, 2.0, 0.0), (3.0, 3.0, 0.0)]
    )
    target_radius: float = 0.65
    step_penalty: float = -0.01
    success_reward: float = 10.0
    progress_reward_scale: float = 1.0
    obstacle_radius: float = 0.5
    primary_agent_id: str = "agent_0"
    max_steps: int | None = None
    name: str = "navigation"

    def __post_init__(self) -> None:
        self._target = Vector3.from_iterable(self.target_position)
        self._previous_distance: float | None = None

    def setup(self, scene: SceneManager) -> None:
        scene.add_floor()
        scene.add_agent(
            BaseAgent(
                self.primary_agent_id,
                position=Vector3.from_iterable(self.start_position),
                yaw_degrees=self.start_yaw_degrees,
            )
        )
        scene.add_object(
            WorldObject(
                object_id="target",
                kind="target",
                position=self._target.copy(),
                radius=self.target_radius,
                height=0.2,
                collidable=False,
                metadata={"success_radius": self.target_radius},
            )
        )
        scene.add_obstacles(self.obstacles, radius=self.obstacle_radius)

    def on_reset(self, scene: SceneManager) -> None:
        self._previous_distance = self._distance(scene)

    def success(self, scene: SceneManager) -> bool:
        return self._distance(scene) <= self.target_radius

    def reward(self, scene: SceneManager) -> float:
        distance = self._distance(scene)
        previous = self._previous_distance if self._previous_distance is not None else distance
        progress = previous - distance
        reward = self.step_penalty + self.progress_reward_scale * progress
        if self.success(scene):
            reward += self.success_reward
        self._previous_distance = distance
        return reward

    def info(self, scene: SceneManager) -> dict[str, object]:
        return {
            "scenario": self.name,
            "distance_to_target": self._distance(scene),
            "target_position": self._target.to_list(),
        }

    def _distance(self, scene: SceneManager) -> float:
        agent = scene.get_agent(self.primary_agent_id)
        return agent.position.distance_xy(self._target)
