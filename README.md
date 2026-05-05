# SimForge3D

[![CI](https://github.com/yablokolabs/SimForge3D/actions/workflows/ci.yml/badge.svg)](https://github.com/yablokolabs/SimForge3D/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

SimForge3D is a Panda3D-based simulation platform for training and evaluating AI agents in configurable 3D worlds. It is designed as infrastructure for reinforcement learning and agent evaluation, not as a traditional game demo.

## Features

- **Modular simulation core** built around Panda3D with lazy imports
- **Gym-style Python API**: `reset()`, `step(action)`, `render()`, `close()`
- **Headless execution** for high-throughput RL training loops
- **Scenario system** with reset, reward, success, failure, and info hooks
- **Agent abstraction** with movement and pick/drop interactions
- **Multi-agent support** with per-agent observations and actions
- **Navigation and pick-and-place** scenarios out of the box
- **Simple deterministic physics** suitable for reproducible AI tasks
- **Episode JSONL logging** and replay recording for debugging
- **Dockerized runtime** with non-root security and health checks
- **Cross-platform** Python package for Linux, macOS, and Windows

## Quick Start

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Run an Example

```bash
python examples/random_navigation.py --headless --episodes 3
```

### Run Tests

```bash
pytest
```

> Panda3D is imported lazily. Headless unit tests and core logic can run without opening a window.

---

## Usage Examples

### Basic Training Loop

```python
from simforge3d import SimForgeEnv, NavigationScenario

scenario = NavigationScenario(target_position=(5, 5, 0))
env = SimForgeEnv(scenario=scenario, headless=True)

obs = env.reset(seed=42)
done = False
total_reward = 0.0

while not done:
    action = env.action_space.sample()
    obs, reward, done, info = env.step(action)
    total_reward += reward

print(f"Episode finished: reward={total_reward:.2f}, success={info['success']}")
env.close()
```

### Pick-and-Place Scenario

```python
from simforge3d import SimForgeEnv, PickPlaceScenario

scenario = PickPlaceScenario(
    object_position=(1.0, 0.0, 0.2),
    goal_position=(4.0, 0.0, 0.0),
    goal_radius=0.75,
)
env = SimForgeEnv(scenario=scenario, headless=True)

obs = env.reset(seed=7)
done = False

# Scripted policy: approach, pick up, carry to goal, drop
actions = ["move_forward"] * 10 + ["pickup"] + ["move_forward"] * 25 + ["drop"]
for action in actions:
    obs, reward, done, info = env.step(action)
    if done:
        break

print(f"Object at goal: {info.get('distance_to_goal', 'N/A')}")
env.close()
```

### Multi-Agent Environment

```python
from simforge3d import SimForgeEnv, NavigationScenario
from simforge3d.agent import BaseAgent

# Create environment with an additional agent
extra_agent = BaseAgent("agent_1", position=(1.0, 0.0, 0.0), yaw_degrees=90.0)
env = SimForgeEnv(
    NavigationScenario(obstacles=[]),
    headless=True,
    agents=[extra_agent],
)

obs = env.reset(seed=3)
# obs is now a dict: {"agent_0": {...}, "agent_1": {...}}

# Send per-agent actions
obs, reward, done, info = env.step({
    "agent_0": "move_forward",
    "agent_1": "turn_right",
})

print(f"Agent 0 position: {obs['agent_0']['position']}")
print(f"Agent 1 position: {obs['agent_1']['position']}")
env.close()
```

### Using String and Dictionary Actions

```python
from simforge3d import SimForgeEnv, NavigationScenario

env = SimForgeEnv(NavigationScenario(), headless=True)
env.reset(seed=0)

# Discrete integer
obs, reward, done, info = env.step(1)  # move forward

# String alias
obs, reward, done, info = env.step("turn_left")

# Dictionary with fine-grained control
obs, reward, done, info = env.step({"command": "turn", "amount": 0.5})

env.close()
```

### Loading Configuration from YAML

```python
from simforge3d import SimForgeEnv, NavigationScenario
from simforge3d.engine.core.config import SimulationConfig

config = SimulationConfig.from_file("configs/headless.yaml")
env = SimForgeEnv(NavigationScenario(), config=config)
obs = env.reset()
# ... training loop
env.close()
```

### Enabling Episode Logging and Replay

```python
from simforge3d import SimForgeEnv, NavigationScenario
from simforge3d.replay import ReplayPlayer

env = SimForgeEnv(
    NavigationScenario(),
    config={
        "headless": True,
        "enable_episode_logging": True,
        "enable_replay": True,
        "log_dir": "runs",
        "replay_dir": "replays",
    },
)
obs = env.reset(seed=1)
for _ in range(50):
    obs, reward, done, info = env.step(env.action_space.sample())
    if done:
        break
env.close()

# Replay the episode
player = ReplayPlayer("replays/replay_000001.jsonl")
for state in player.states():
    print(f"Step {state['step_count']}: {state['agents']}")
```

### Creating a Custom Scenario

```python
from simforge3d.scenarios.base import BaseScenario
from simforge3d.scenarios.registry import register_scenario
from simforge3d.engine.core.scene import SceneManager
from simforge3d.agent.base import BaseAgent
from simforge3d.engine.core.types import Vector3


class PatrolScenario(BaseScenario):
    name = "patrol"

    def __init__(self, waypoints: list[tuple[float, float, float]] | None = None):
        self.waypoints = waypoints or [(3, 0, 0), (0, 3, 0), (-3, 0, 0), (0, -3, 0)]
        self._current_wp = 0
        self._visited = 0

    def setup(self, scene: SceneManager) -> None:
        scene.add_floor()
        scene.add_agent(BaseAgent("agent_0", position=(0.0, 0.0, 0.0)))

    def success(self, scene: SceneManager) -> bool:
        return self._visited >= len(self.waypoints)

    def reward(self, scene: SceneManager) -> float:
        agent = scene.get_agent("agent_0")
        target = Vector3.from_iterable(self.waypoints[self._current_wp])
        if agent.position.distance_xy(target) < 0.5:
            self._current_wp = (self._current_wp + 1) % len(self.waypoints)
            self._visited += 1
            return 5.0
        return -0.01


# Register so it can be created by name
register_scenario("patrol", PatrolScenario)
```

---

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

## Project Layout

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

## Headless Mode

Headless mode is the default and is critical for high-throughput RL training:

```python
env = SimForgeEnv(headless=True)
```

When rendering is enabled, Panda3D is configured for an onscreen window. When headless is enabled, Panda3D is configured with `window-type none` and no audio device.

## Docker

### Production

```bash
docker build -t simforge3d .
docker run --rm simforge3d
```

### Development

```bash
docker compose run --rm simforge3d-dev
```

The Docker image runs as a non-root user with a health check configured.

## Configuration

SimForge3D supports configuration via Python objects, dictionaries, JSON, or YAML files:

```python
# From a YAML file (requires pip install SimForge3D[yaml])
config = SimulationConfig.from_file("configs/headless.yaml")

# From a dictionary
env = SimForgeEnv(config={"headless": True, "max_steps": 1000, "fixed_dt": 0.0333})

# Programmatic
from simforge3d import SimulationConfig, CameraConfig
config = SimulationConfig(
    headless=True,
    max_steps=500,
    observation_radius=8.0,
    camera=CameraConfig(position=(0, -15, 12), fov_degrees=60.0),
)
```

## Creating Scenarios

Subclass `BaseScenario` and implement:

- `setup(scene)` — initial state
- `success(scene)` — terminal success condition
- `reward(scene)` — reward function
- `reset(scene)` — inherited reset orchestration, override only when needed

See the [custom scenario example](#creating-a-custom-scenario) above for a full implementation.

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for a detailed overview of the system layers and extension points.

## Contributing

Contributions are welcome! See [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines.

## Security

See [`SECURITY.md`](SECURITY.md) for our vulnerability reporting policy.

## License

MIT — see [`LICENSE`](LICENSE) for details.

## Status

This is an alpha simulation platform with production-oriented architecture, full test coverage, CI/CD pipelines, and Docker support. The physics layer is intentionally simple and deterministic; heavier backends can be added behind the same interfaces or via optional C++ extensions.
