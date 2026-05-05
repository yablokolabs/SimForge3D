"""Base AI agent implementation."""

from __future__ import annotations

from simforge3d.agent.actions import AgentAction
from simforge3d.agent.observations import AgentObservation
from simforge3d.engine.core.config import SimulationConfig
from simforge3d.engine.core.physics import PhysicsSystem
from simforge3d.engine.core.scene import SceneManager
from simforge3d.engine.core.types import AgentState, Vector3


class BaseAgent:
    """Embodied AI agent with deterministic motion and interactions."""

    def __init__(
        self,
        agent_id: str = "agent_0",
        position: tuple[float, float, float] | Vector3 = (0.0, 0.0, 0.0),
        yaw_degrees: float = 0.0,
        *,
        speed: float = 3.0,
        turn_speed_degrees: float = 120.0,
        radius: float = 0.35,
    ) -> None:
        self.agent_id = agent_id
        self.initial_position = Vector3.from_iterable(position)
        self.initial_yaw_degrees = yaw_degrees
        self.position = self.initial_position.copy()
        self.yaw_degrees = yaw_degrees
        self.speed = speed
        self.turn_speed_degrees = turn_speed_degrees
        self.radius = radius
        self.held_object_id: str | None = None

    def reset(self) -> None:
        self.position = self.initial_position.copy()
        self.yaw_degrees = self.initial_yaw_degrees
        self.held_object_id = None

    def state(self) -> AgentState:
        return AgentState(
            agent_id=self.agent_id,
            position=self.position.copy(),
            yaw_degrees=self.yaw_degrees,
            radius=self.radius,
            held_object_id=self.held_object_id,
        )

    def observe(self, scene: SceneManager, config: SimulationConfig) -> AgentObservation:
        nearby = [
            obj.to_dict() for obj in scene.nearby_objects(self.position, config.observation_radius)
        ]
        return AgentObservation(
            agent_id=self.agent_id,
            position=self.position.as_tuple(),
            yaw_degrees=self.yaw_degrees,
            held_object_id=self.held_object_id,
            nearby_objects=nearby,
            environment_state=scene.environment_state(),
        )

    def apply_action(
        self,
        action: AgentAction,
        scene: SceneManager,
        physics: PhysicsSystem,
        dt: float,
    ) -> bool:
        if action.command == "noop":
            scene.emit_event("noop", agent_id=self.agent_id)
            return True
        if action.command == "turn":
            self.yaw_degrees = (
                self.yaw_degrees + action.amount * self.turn_speed_degrees * dt
            ) % 360.0
            scene.emit_event("turn", agent_id=self.agent_id, yaw_degrees=self.yaw_degrees)
            return True
        if action.command == "move":
            forward = Vector3.forward_from_yaw(self.yaw_degrees)
            delta = forward.scale(self.speed * action.amount * dt)
            return physics.try_move_agent(self, scene, delta)
        if action.command == "pickup":
            return physics.try_pickup(self, scene)
        if action.command == "drop":
            return physics.drop(self, scene)
        raise ValueError(f"Unsupported action command: {action.command}")
