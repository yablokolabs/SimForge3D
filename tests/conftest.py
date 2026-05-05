"""Shared test fixtures for SimForge3D tests."""

from __future__ import annotations

import pytest

from simforge3d import NavigationScenario, PickPlaceScenario, SimForgeEnv
from simforge3d.agent.base import BaseAgent
from simforge3d.engine.core.config import SimulationConfig
from simforge3d.engine.core.physics import PhysicsSystem
from simforge3d.engine.core.scene import SceneManager


@pytest.fixture
def config() -> SimulationConfig:
    return SimulationConfig(headless=True, max_steps=100)


@pytest.fixture
def scene(config: SimulationConfig) -> SceneManager:
    return SceneManager(config)


@pytest.fixture
def physics(config: SimulationConfig) -> PhysicsSystem:
    return PhysicsSystem(config)


@pytest.fixture
def agent() -> BaseAgent:
    return BaseAgent("agent_0", position=(0.0, 0.0, 0.0), yaw_degrees=0.0)


@pytest.fixture
def nav_env() -> SimForgeEnv:
    env = SimForgeEnv(NavigationScenario(obstacles=[]), headless=True)
    yield env
    env.close()


@pytest.fixture
def pick_env() -> SimForgeEnv:
    env = SimForgeEnv(
        PickPlaceScenario(object_position=(0.0, 0.5, 0.2), goal_position=(0.0, 1.8, 0.0)),
        headless=True,
    )
    yield env
    env.close()
