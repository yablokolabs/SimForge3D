from simforge3d import PickPlaceScenario, SimForgeEnv


def test_pickup_and_drop_events():
    scenario = PickPlaceScenario(object_position=(0.0, 0.5, 0.2), goal_position=(0.0, 1.8, 0.0))
    env = SimForgeEnv(scenario, headless=True)
    env.reset(seed=2)
    _, reward, done, info = env.step("pickup")
    assert reward > 0
    assert any(event["type"] == "pickup" for event in info["events"])
    _, _, _, info = env.step("drop")
    assert any(event["type"] == "drop" for event in info["events"])
    assert done is False
    env.close()
