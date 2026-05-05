"""Panda3D application setup.

The Panda3D dependency is imported lazily so pure headless training logic remains
fast to import and easy to test in CI.
"""

from __future__ import annotations

from typing import Any

from simforge3d.assets.manager import AssetManager
from simforge3d.engine.core.camera import CameraController
from simforge3d.engine.core.config import SimulationConfig
from simforge3d.engine.core.scene import SceneManager


class Panda3DUnavailable(RuntimeError):
    """Raised when rendered mode is requested without Panda3D installed."""


def configure_panda3d(config: SimulationConfig) -> None:
    try:
        from panda3d.core import loadPrcFileData
    except ImportError as exc:  # pragma: no cover - depends on optional runtime
        raise Panda3DUnavailable(
            "Panda3D is required for rendered mode. Install with `pip install panda3d`."
        ) from exc

    window_type = "none" if config.headless else "onscreen"
    loadPrcFileData("", f"window-type {window_type}")
    loadPrcFileData("", "audio-library-name null")
    loadPrcFileData("", f"win-size {config.render_width} {config.render_height}")
    loadPrcFileData("", "sync-video false")
    loadPrcFileData("", "show-frame-rate-meter false")


class PandaSimulationApp:
    """Thin wrapper around Panda3D's ShowBase."""

    def __init__(self, config: SimulationConfig | None = None) -> None:
        self.config = config or SimulationConfig()
        configure_panda3d(self.config)
        try:
            from direct.showbase.ShowBase import ShowBase
        except ImportError as exc:  # pragma: no cover - depends on optional runtime
            raise Panda3DUnavailable("Panda3D ShowBase could not be imported") from exc

        self.base = ShowBase(windowType="none" if self.config.headless else "onscreen")
        self.assets = AssetManager(self.base.loader, self.base.render)
        self.camera = CameraController(self.config.camera)

    def attach_scene(self, scene: SceneManager) -> None:
        scene.panda_root = self.base.render.attachNewNode("simforge3d_scene")
        self.assets.sync_scene(scene, scene.panda_root)
        self.camera.apply(self.base.camera)

    def step(self) -> None:
        self.base.taskMgr.step()

    def render_frame(self) -> Any | None:
        self.step()
        return None

    def close(self) -> None:
        self.base.destroy()
