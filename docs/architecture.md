# SimForge3D Architecture

SimForge3D separates simulation state, rendering, scenarios, agents, and training APIs so the platform can be extended without turning into a monolithic game script.

## Layers

1. **Simulation core (`engine/core`)**
   - `SimulationConfig` stores cross-platform engine settings.
   - `SceneManager` owns deterministic world state: agents, objects, elapsed time, and events.
   - `PhysicsSystem` handles fast XY-plane collisions, bounds, movement, and pick/drop operations.
   - `PandaSimulationApp` configures Panda3D lazily for rendered or headless mode.

2. **Agent interface (`agent`)**
   - `BaseAgent` exposes embodiment state, observation generation, and action application.
   - `AgentAction` normalizes discrete, string, and dictionary actions.
   - Observations include position, yaw, held object, nearby objects, and environment state.

3. **Scenario system (`scenarios`)**
   - `BaseScenario` defines `setup`, `reset`, `success`, `failure`, `reward`, and `info`.
   - Built-ins: `NavigationScenario` and `PickPlaceScenario`.
   - Registry allows configurable scenario creation by name.

4. **Gym-style API (`gym_interface`)**
   - `SimForgeEnv` provides `reset`, `step`, `render`, and `close`.
   - `step` returns the classic Gym tuple: observation, reward, done, info.
   - The default action/observation spaces do not require Gymnasium, but the API is compatible with training loops.

5. **Assets (`assets`)**
   - Asset loading is Panda3D-specific and isolated from simulation state.
   - Primitive floor/marker rendering is included for simple worlds.

6. **Telemetry and replay**
   - JSONL episode logs support offline analysis.
   - Replay recorder stores scene snapshots and actions for debugging.

## Headless mode

Headless mode is the default. It avoids window creation and keeps the core state loop free of graphics dependencies. Rendered mode initializes Panda3D only when `render()` is called with `headless=False`.

## Extension points

- Replace `PhysicsSystem` with a higher-fidelity backend.
- Add custom scenarios via `BaseScenario` or `register_scenario`.
- Add custom agents by subclassing `BaseAgent`.
- Add external model integration through direct Python training loops.
- Add C++ extensions for heavy collision/path planning while preserving Python APIs.
