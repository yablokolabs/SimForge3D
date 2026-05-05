"""Episode logging for training and evaluation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TextIO


class EpisodeLogger:
    """Append-only JSONL episode logger."""

    def __init__(self, log_dir: str | Path = "runs") -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._file: TextIO | None = None

    def start_episode(self, episode_id: int, initial_state: dict[str, Any]) -> None:
        self.close()
        path = self.log_dir / f"episode_{episode_id:06d}.jsonl"
        self._file = path.open("w", encoding="utf-8")
        self._write(
            {
                "event": "episode_start",
                "episode_id": episode_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "state": initial_state,
            }
        )

    def log_step(
        self,
        observation: dict[str, Any],
        action: dict[str, Any],
        reward: float,
        done: bool,
        info: dict[str, Any],
    ) -> None:
        self._write(
            {
                "event": "step",
                "observation": observation,
                "action": action,
                "reward": reward,
                "done": done,
                "info": info,
            }
        )

    def end_episode(self, info: dict[str, Any]) -> None:
        self._write({"event": "episode_end", "info": info})
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
