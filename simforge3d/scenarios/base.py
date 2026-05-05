"""Scenario interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from simforge3d.engine.core.scene import SceneManager


class BaseScenario(ABC):
    """Contract every scenario must implement."""

    name = "base"
    primary_agent_id = "agent_0"
    max_steps: int | None = None

    def reset(self, scene: SceneManager) -> None:
        scene.clear()
        self.setup(scene)
        self.on_reset(scene)

    @abstractmethod
    def setup(self, scene: SceneManager) -> None:
        """Populate scene with initial state."""

    def on_reset(self, scene: SceneManager) -> None:
        """Optional hook after setup."""
        return None

    @abstractmethod
    def success(self, scene: SceneManager) -> bool:
        """Return true when the scenario objective is complete."""

    def failure(self, scene: SceneManager) -> bool:
        """Return true for terminal failure conditions."""
        return False

    @abstractmethod
    def reward(self, scene: SceneManager) -> float:
        """Compute reward after a simulation step."""

    def info(self, scene: SceneManager) -> dict[str, Any]:
        """Additional diagnostic data returned by env.step()."""
        return {"scenario": self.name}
