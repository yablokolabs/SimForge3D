# SimForge3D

SimForge3D is a Panda3D-based simulation platform for training and evaluating AI agents in configurable 3D worlds. It is designed as infrastructure for reinforcement learning and agent evaluation, not as a traditional game demo.

## What it provides

- Modular simulation core built around Panda3D
- Gym-style Python API: `reset()`, `step(action)`, `render()`, `close()`
- Headless execution for fast training loops
- Scenario system with reset, reward, success, and info hooks
- Agent abstraction with movement and pick/drop interactions
- Navigation and pick-and-place scenarios out of the box
- Simple physics/collision layer suitable for AI tasks
- Episode JSONL logging and replay recording
- Dockerized runtime
- Cross-platform Python package structure for Linux, macOS, and Windows

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python examples/random_navigation.py --headless --episodes 3
pytest
```

> Panda3D is imported lazily. Headless unit tests and core logic can run without opening a window.

## Minimal training loop

```python
from simforge3d import SimForgeEnv
from simforge3d.scenarios import NavigationScenario

scenario = NavigationScenario(target_position=(5, 5, 0))
env = SimForgeEnv(scenario=scenario, headless=True)

obs = env.reset(seed=42)
done = False
while not done:
    action = env.action_space.sample()
    obs, reward, done, info = env.step(action)

env.close()
```

## Actions

The default discrete action space maps to:

| ID | Action |
| --- | --- |
| `0` | no-op |
| `1` | move forward |
| `2` | move backward |
| `3` | turn left |
| `4` | turn right |
| `5` | pick up nearest object |
| `6` | drop held object |

Actions can also be strings or dictionaries:

```python
env.step("move_forward")
env.step({"command": "turn", "amount": 1.0})
env.step({"agent_0": "move_forward", "agent_1": "turn_left"})  # multi-agent
```

## Project layout

```text
simforge3d/
  engine/core/       Panda3D app setup, scene manager, physics, camera, config
  agent/             Agent base class, actions, observations
  scenarios/         Base scenario API + navigation and pick/place scenarios
  gym_interface/     Gym-like environment wrapper and fallback spaces
  assets/            Basic model/primitive asset helpers
  telemetry/         Episode logging
  replay/            Replay recording and playback utilities
assets/              Place custom models/textures here
configs/             Example configuration files
examples/            Runnable API examples
tests/               Headless unit tests
cpp/                 Optional C++ acceleration extension sketch
```

## Headless mode

Headless mode is the default and is critical for high-throughput RL training:

```python
env = SimForgeEnv(headless=True)
```

When rendering is enabled, Panda3D is configured for an onscreen window. When headless is enabled, Panda3D is configured with `window-type none` and no audio device.

## Docker

```bash
docker build -t simforge3d .
docker run --rm simforge3d
```

For development:

```bash
docker compose run --rm simforge3d-dev pytest
```

## Creating scenarios

Subclass `BaseScenario` and implement:

- `setup(scene)` — initial state
- `success(scene)` — terminal success condition
- `reward(scene)` — reward function
- `reset(scene)` — inherited reset orchestration, override only when needed

```python
from simforge3d.scenarios.base import BaseScenario

class MyScenario(BaseScenario):
    name = "my_scenario"

    def setup(self, scene):
        ...

    def success(self, scene):
        return False

    def reward(self, scene):
        return 0.0
```

## Status

This is an alpha simulation platform scaffold with production-oriented architecture, tests, and Docker support. The current physics layer is intentionally simple and deterministic; heavier collision/pathing can be added behind the same interfaces or via optional C++ extensions.
