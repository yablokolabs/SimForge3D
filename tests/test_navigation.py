from simforge3d import NavigationScenario, SimForgeEnv


def test_navigation_env_headless_step_contract():
    env = SimForgeEnv(NavigationScenario(obstacles=[]), headless=True)
    obs = env.reset(seed=123)
    assert env.observation_space.contains(obs)
    next_obs, reward, done, info = env.step("move_forward")
    assert env.observation_space.contains(next_obs)
    assert isinstance(reward, float)
    assert isinstance(done, bool)
    assert "distance_to_target" in info
    env.close()


def test_navigation_can_succeed():
    scenario = NavigationScenario(target_position=(0.0, 0.2, 0.0), start_position=(0.0, 0.0, 0.0), obstacles=[], target_radius=0.35)
    env = SimForgeEnv(scenario, headless=True)
    env.reset(seed=1)
    _, reward, done, info = env.step("move_forward")
    assert done
    assert info["success"] is True
    assert reward > 0
    env.close()
