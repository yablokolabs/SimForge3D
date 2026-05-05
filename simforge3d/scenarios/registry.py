"""Scenario registry for configurable environments."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from simforge3d.scenarios.base import BaseScenario
from simforge3d.scenarios.navigation import NavigationScenario
from simforge3d.scenarios.pick_place import PickPlaceScenario

ScenarioFactory = Callable[..., BaseScenario]

_REGISTRY: dict[str, ScenarioFactory] = {}


def register_scenario(name: str, factory: ScenarioFactory) -> None:
    if not name:
        raise ValueError("Scenario name cannot be empty")
    _REGISTRY[name] = factory


def make_scenario(name: str, **kwargs: Any) -> BaseScenario:
    try:
        factory = _REGISTRY[name]
    except KeyError as exc:
        available = ", ".join(sorted(_REGISTRY))
        raise KeyError(f"Unknown scenario {name!r}. Available: {available}") from exc
    return factory(**kwargs)


def available_scenarios() -> tuple[str, ...]:
    return tuple(sorted(_REGISTRY))


register_scenario("navigation", NavigationScenario)
register_scenario("pick_place", PickPlaceScenario)
