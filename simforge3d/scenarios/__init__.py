"""Built-in scenarios."""

from simforge3d.scenarios.base import BaseScenario
from simforge3d.scenarios.navigation import NavigationScenario
from simforge3d.scenarios.pick_place import PickPlaceScenario
from simforge3d.scenarios.registry import make_scenario, register_scenario

__all__ = [
    "BaseScenario",
    "NavigationScenario",
    "PickPlaceScenario",
    "make_scenario",
    "register_scenario",
]
