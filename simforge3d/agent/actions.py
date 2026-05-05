"""Action normalization and default action spaces."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Literal

ActionCommand = Literal["noop", "move", "turn", "pickup", "drop"]

_DISCRETE_ACTIONS: dict[int, tuple[ActionCommand, float]] = {
    0: ("noop", 0.0),
    1: ("move", 1.0),
    2: ("move", -1.0),
    3: ("turn", -1.0),
    4: ("turn", 1.0),
    5: ("pickup", 1.0),
    6: ("drop", 1.0),
}

_STRING_ALIASES: dict[str, AgentAction] = {}


@dataclass(frozen=True, slots=True)
class AgentAction:
    command: ActionCommand = "noop"
    amount: float = 0.0

    @classmethod
    def from_discrete(cls, action_id: int) -> AgentAction:
        try:
            command, amount = _DISCRETE_ACTIONS[int(action_id)]
        except KeyError as exc:
            raise ValueError(f"Unknown discrete action: {action_id}") from exc
        return cls(command=command, amount=amount)

    @classmethod
    def from_any(cls, value: Any) -> AgentAction:
        if isinstance(value, AgentAction):
            return value
        if isinstance(value, int):
            return cls.from_discrete(value)
        if isinstance(value, str):
            key = value.strip().lower()
            if not _STRING_ALIASES:
                _init_aliases()
            if key not in _STRING_ALIASES:
                raise ValueError(f"Unknown action string: {value!r}")
            return _STRING_ALIASES[key]
        if isinstance(value, dict):
            command = str(value.get("command", value.get("type", "noop"))).lower()
            amount = float(value.get("amount", 0.0))
            return cls(command=_normalize_command(command), amount=amount)
        raise TypeError(f"Cannot convert {type(value)!r} to AgentAction")

    def to_dict(self) -> dict[str, float | str]:
        return {"command": self.command, "amount": self.amount}


def _normalize_command(command: str) -> ActionCommand:
    aliases = {
        "noop": "noop",
        "none": "noop",
        "move": "move",
        "forward": "move",
        "backward": "move",
        "turn": "turn",
        "left": "turn",
        "right": "turn",
        "pickup": "pickup",
        "pick": "pickup",
        "drop": "drop",
    }
    if command not in aliases:
        raise ValueError(f"Unknown action command: {command!r}")
    return aliases[command]  # type: ignore[return-value]


def _init_aliases() -> None:
    _STRING_ALIASES.update(
        {
            "noop": AgentAction("noop", 0.0),
            "move_forward": AgentAction("move", 1.0),
            "forward": AgentAction("move", 1.0),
            "move_backward": AgentAction("move", -1.0),
            "backward": AgentAction("move", -1.0),
            "turn_left": AgentAction("turn", -1.0),
            "left": AgentAction("turn", -1.0),
            "turn_right": AgentAction("turn", 1.0),
            "right": AgentAction("turn", 1.0),
            "pickup": AgentAction("pickup", 1.0),
            "pick": AgentAction("pickup", 1.0),
            "drop": AgentAction("drop", 1.0),
        }
    )


class DefaultActionSpace:
    """Small Gym-like discrete action space without a hard dependency on Gym."""

    n = len(_DISCRETE_ACTIONS)

    def sample(self) -> int:
        return random.randrange(self.n)

    def contains(self, value: object) -> bool:
        if isinstance(value, int):
            return 0 <= value < self.n
        try:
            AgentAction.from_any(value)
        except (TypeError, ValueError):
            return False
        return True

    def __repr__(self) -> str:
        return f"DefaultActionSpace(n={self.n})"
