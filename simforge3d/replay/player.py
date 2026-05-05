"""Replay playback helpers."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any


class ReplayPlayer:
    """Iterates over JSONL replay events."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def events(self) -> Iterator[dict[str, Any]]:
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    yield json.loads(line)

    def states(self) -> Iterator[dict[str, Any]]:
        for event in self.events():
            if "state" in event:
                yield event["state"]
