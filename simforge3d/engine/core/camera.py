"""Camera helpers for rendered Panda3D mode."""

from __future__ import annotations

from simforge3d.engine.core.config import CameraConfig
from simforge3d.engine.core.types import Vector3


class CameraController:
    """Stores camera intent and applies it to a Panda3D camera when available."""

    def __init__(self, config: CameraConfig | None = None) -> None:
        self.config = config or CameraConfig()
        self.follow_agent_id: str | None = None

    def follow(self, agent_id: str | None) -> None:
        self.follow_agent_id = agent_id

    def apply(self, camera: object, target: Vector3 | None = None) -> None:
        position = self.config.position
        look_at = target.as_tuple() if target else self.config.look_at
        # Panda3D NodePath API is deliberately accessed dynamically to keep this
        # module importable without Panda3D in headless tests.
        camera.setPos(*position)  # type: ignore[attr-defined]
        camera.lookAt(*look_at)  # type: ignore[attr-defined]
        lens = camera.node().getLens()  # type: ignore[attr-defined]
        lens.setFov(self.config.fov_degrees)
