from simforge3d import NavigationScenario, SimForgeEnv
from simforge3d.agent import BaseAgent


def test_multi_agent_action_mapping_returns_multi_observation():
    env = SimForgeEnv(
        NavigationScenario(obstacles=[]),
        headless=True,
        agents=[BaseAgent("agent_1", position=(1.0, 0.0, 0.0), yaw_degrees=0.0)],
    )
    obs = env.reset(seed=3)
    assert set(obs) == {"agent_0", "agent_1"}
    obs, _, _, info = env.step({"agent_0": "move_forward", "agent_1": "turn_right"})
    assert set(obs) == {"agent_0", "agent_1"}
    assert info["step_count"] == 1
    env.close()
