"""Basic Panda3D asset management and primitive creation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from simforge3d.engine.core.scene import SceneManager
from simforge3d.engine.core.types import WorldObject


class AssetManager:
    """Loads models and creates simple render nodes for simulation objects."""

    def __init__(self, loader: Any | None = None, render_root: Any | None = None) -> None:
        self.loader = loader
        self.render_root = render_root
        self.nodes: dict[str, Any] = {}

    def load_model(self, name: str, path: str | Path, parent: Any | None = None) -> Any:
        if self.loader is None:
            raise RuntimeError("Panda3D loader is not available")
        node = self.loader.loadModel(str(path))
        node.reparentTo(parent or self.render_root)
        self.nodes[name] = node
        return node

    def sync_scene(self, scene: SceneManager, parent: Any | None = None) -> None:
        for obj in scene.objects.values():
            if obj.kind == "floor":
                self.nodes[obj.object_id] = self._create_floor(obj, parent)
            elif obj.kind in {"obstacle", "target", "goal", "pickup_object"}:
                self.nodes[obj.object_id] = self._create_marker(obj, parent)

    def _create_floor(self, obj: WorldObject, parent: Any | None) -> Any:
        try:
            from panda3d.core import CardMaker
        except ImportError as exc:  # pragma: no cover - depends on Panda3D
            raise RuntimeError("Panda3D is required to create render assets") from exc
        size = float(obj.metadata.get("size", obj.radius * 2.0))
        maker = CardMaker(obj.object_id)
        maker.setFrame(-size / 2.0, size / 2.0, -size / 2.0, size / 2.0)
        node = (parent or self.render_root).attachNewNode(maker.generate())  # type: ignore[union-attr]
        node.setP(obj.metadata.get("pitch", -90.0))
        node.setPos(*obj.position.as_tuple())
        node.setColor(0.25, 0.25, 0.25, 1.0)
        return node

    def _create_marker(self, obj: WorldObject, parent: Any | None) -> Any:
        try:
            from panda3d.core import CardMaker
        except ImportError as exc:  # pragma: no cover - depends on Panda3D
            raise RuntimeError("Panda3D is required to create render assets") from exc
        size = max(0.2, obj.radius * 2.0)
        maker = CardMaker(obj.object_id)
        maker.setFrame(-size / 2.0, size / 2.0, -size / 2.0, size / 2.0)
        node = (parent or self.render_root).attachNewNode(maker.generate())  # type: ignore[union-attr]
        node.setP(-90.0)
        node.setPos(*obj.position.as_tuple())
        color = {
            "target": (0.0, 1.0, 0.1, 1.0),
            "goal": (0.1, 0.4, 1.0, 1.0),
            "pickup_object": (1.0, 0.8, 0.0, 1.0),
            "obstacle": (0.9, 0.1, 0.1, 1.0),
        }.get(obj.kind, (1.0, 1.0, 1.0, 1.0))
        node.setColor(*color)
        return node
