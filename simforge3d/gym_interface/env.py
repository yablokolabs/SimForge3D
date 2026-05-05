"""Gym-like environment wrapper for SimForge3D."""

from __future__ import annotations

import random
from collections.abc import Iterable, Mapping
from typing import Any

from simforge3d.agent.actions import AgentAction, DefaultActionSpace
from simforge3d.agent.base import BaseAgent
from simforge3d.engine.core.app import PandaSimulationApp
from simforge3d.engine.core.config import SimulationConfig
from simforge3d.engine.core.physics import PhysicsSystem
from simforge3d.engine.core.scene import SceneManager
from simforge3d.gym_interface.spaces import ObservationSpace
from simforge3d.replay.recorder import ReplayRecorder
from simforge3d.scenarios.base import BaseScenario
from simforge3d.scenarios.navigation import NavigationScenario
from simforge3d.telemetry.episode import EpisodeLogger


class SimForgeEnv:
    """Production-oriented Gym-style API for AI training loops.

    The API intentionally returns the classic four-tuple from ``step``:
    ``observation, reward, done, info``.
    """

    metadata = {"render_modes": ["human", "rgb_array", None]}

    def __init__(
        self,
        scenario: BaseScenario | None = None,
        config: SimulationConfig | Mapping[str, Any] | None = None,
        *,
        headless: bool | None = None,
        agents: Iterable[BaseAgent] | None = None,
    ) -> None:
        if isinstance(config, SimulationConfig):
            self.config = config
        elif isinstance(config, Mapping):
            self.config = SimulationConfig.from_mapping(dict(config))
        else:
            self.config = SimulationConfig()
        if headless is not None:
            self.config.headless = headless

        self.scenario = scenario or NavigationScenario()
        self.scene = SceneManager(self.config)
        self.physics = PhysicsSystem(self.config)
        self.action_space = DefaultActionSpace()
        self.observation_space = ObservationSpace()
        self.extra_agents = list(agents or [])
        self._app: PandaSimulationApp | None = None
        self._done = False
        self._episode_id = 0
        self._logger = (
            EpisodeLogger(self.config.log_dir) if self.config.enable_episode_logging else None
        )
        self._replay = ReplayRecorder(self.config.replay_dir) if self.config.enable_replay else None

    def reset(
        self, seed: int | None = None, options: Mapping[str, Any] | None = None
    ) -> dict[str, Any]:
        del options  # reserved for Gym compatibility
        if seed is not None:
            random.seed(seed)
            self.config.seed = seed
        elif self.config.seed is not None:
            random.seed(self.config.seed)

        self.scenario.reset(self.scene)
        for agent in self.extra_agents:
            agent.reset()
            if agent.agent_id not in self.scene.agents:
                self.scene.add_agent(agent)

        self._done = False
        self._episode_id += 1
        observation = self._collect_observation()
        if self._logger:
            self._logger.start_episode(self._episode_id, self.scene.snapshot())
        if self._replay:
            self._replay.start_episode(self._episode_id, self.scene.snapshot())
        return observation

    def step(self, action: Any) -> tuple[dict[str, Any], float, bool, dict[str, Any]]:
        if self._done:
            raise RuntimeError("Cannot call step() after episode is done. Call reset() first.")

        self.scene.last_events.clear()
        actions = self._normalize_actions(action)
        dt = self.config.fixed_dt / max(1, self.config.physics_substeps)
        normalized_actions: dict[str, dict[str, Any]] = {}
        for _ in range(max(1, self.config.physics_substeps)):
            for agent_id, agent_action in actions.items():
                agent = self.scene.get_agent(agent_id)
                agent.apply_action(agent_action, self.scene, self.physics, dt)
                normalized_actions[agent_id] = agent_action.to_dict()
        self.scene.update(self.config.fixed_dt)

        reward = self.scenario.reward(self.scene)
        success = self.scenario.success(self.scene)
        failure = self.scenario.failure(self.scene)
        scenario_limit = self.scenario.max_steps or self.config.max_steps
        timeout = self.scene.step_count >= scenario_limit
        self._done = bool(success or failure or timeout)

        observation = self._collect_observation()
        info = {
            **self.scenario.info(self.scene),
            "success": success,
            "failure": failure,
            "timeout": timeout,
            "step_count": self.scene.step_count,
            "events": list(self.scene.last_events),
        }

        if self._logger:
            self._logger.log_step(observation, normalized_actions, reward, self._done, info)
            if self._done:
                self._logger.end_episode(info)
        if self._replay:
            self._replay.log_step(
                self.scene.snapshot(), normalized_actions, reward, self._done, info
            )
            if self._done:
                self._replay.end_episode(info)
        return observation, reward, self._done, info

    def render(self) -> Any | None:
        if self.config.headless:
            return None
        if self._app is None:
            self._app = PandaSimulationApp(self.config)
            self._app.attach_scene(self.scene)
        return self._app.render_frame()

    def close(self) -> None:
        if self._app is not None:
            self._app.close()
            self._app = None
        if self._logger:
            self._logger.close()
        if self._replay:
            self._replay.close()

    def add_agent(self, agent: BaseAgent) -> None:
        self.extra_agents.append(agent)
        if self.scene.agents and agent.agent_id not in self.scene.agents:
            self.scene.add_agent(agent)

    def _normalize_actions(self, action: Any) -> dict[str, AgentAction]:
        if isinstance(action, Mapping) and not self._looks_like_single_action(action):
            return {str(agent_id): AgentAction.from_any(raw) for agent_id, raw in action.items()}
        return {self.scenario.primary_agent_id: AgentAction.from_any(action)}

    @staticmethod
    def _looks_like_single_action(value: Mapping[str, Any]) -> bool:
        return "command" in value or "type" in value or "amount" in value

    def _collect_observation(self) -> dict[str, Any]:
        observations = {
            agent_id: agent.observe(self.scene, self.config).to_dict()
            for agent_id, agent in self.scene.agents.items()
        }
        if len(observations) == 1 and self.scenario.primary_agent_id in observations:
            return observations[self.scenario.primary_agent_id]
        return observations
