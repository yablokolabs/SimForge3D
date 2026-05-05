"""Configuration objects for SimForge3D."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class CameraConfig:
    position: tuple[float, float, float] = (0.0, -12.0, 9.0)
    look_at: tuple[float, float, float] = (0.0, 0.0, 0.0)
    fov_degrees: float = 70.0


@dataclass(slots=True)
class SimulationConfig:
    """Engine configuration with safe headless defaults for RL training."""

    headless: bool = field(default_factory=lambda: os.getenv("SIMFORGE3D_HEADLESS", "1") != "0")
    fixed_dt: float = 1.0 / 30.0
    target_fps: int = 120
    max_steps: int = 500
    physics_substeps: int = 1
    observation_radius: float = 6.0
    world_bounds: tuple[float, float, float, float] = (-20.0, 20.0, -20.0, 20.0)
    render_width: int = 1280
    render_height: int = 720
    seed: int | None = None
    camera: CameraConfig = field(default_factory=CameraConfig)
    enable_episode_logging: bool = False
    enable_replay: bool = False
    log_dir: str = "runs"
    replay_dir: str = "replays"

    @classmethod
    def from_mapping(cls, values: dict[str, Any]) -> SimulationConfig:
        data = dict(values)
        camera_value = data.get("camera")
        if isinstance(camera_value, dict):
            data["camera"] = CameraConfig(**camera_value)
        if "world_bounds" in data:
            data["world_bounds"] = tuple(float(v) for v in data["world_bounds"])
        return cls(**data)

    @classmethod
    def from_file(cls, path: str | Path) -> SimulationConfig:
        path = Path(path)
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() in {".yaml", ".yml"}:
            try:
                import yaml  # type: ignore
            except ImportError as exc:  # pragma: no cover - optional dependency
                raise RuntimeError("Install SimForge3D[yaml] to load YAML configs") from exc
            data = yaml.safe_load(text) or {}
        else:
            data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError(f"Config file {path} must contain an object/mapping")
        return cls.from_mapping(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
