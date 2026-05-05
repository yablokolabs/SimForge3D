"""Replay recording utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TextIO


class ReplayRecorder:
    """Records full scene snapshots for deterministic replay/debugging."""

    def __init__(self, replay_dir: str | Path = "replays") -> None:
        self.replay_dir = Path(replay_dir)
        self.replay_dir.mkdir(parents=True, exist_ok=True)
        self._file: TextIO | None = None

    def start_episode(self, episode_id: int, initial_state: dict[str, Any]) -> None:
        self.close()
        self._file = (self.replay_dir / f"replay_{episode_id:06d}.jsonl").open(
            "w", encoding="utf-8"
        )
        self._write({"event": "start", "state": initial_state})

    def log_step(
        self,
        state: dict[str, Any],
        action: dict[str, Any],
        reward: float,
        done: bool,
        info: dict[str, Any],
    ) -> None:
        self._write(
            {
                "event": "step",
                "state": state,
                "action": action,
                "reward": reward,
                "done": done,
                "info": info,
            }
        )

    def end_episode(self, info: dict[str, Any]) -> None:
        self._write({"event": "end", "info": info})
        self.close()

    def close(self) -> None:
        if self._file is not None:
            self._file.close()
            self._file = None

    def _write(self, payload: dict[str, Any]) -> None:
        if self._file is None:
            return
        self._file.write(json.dumps(payload, sort_keys=True) + "\n")
        self._file.flush()
