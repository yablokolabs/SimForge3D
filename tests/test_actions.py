from simforge3d.agent.actions import AgentAction, DefaultActionSpace


def test_action_normalization():
    assert AgentAction.from_any(1).command == "move"
    assert AgentAction.from_any("turn_left").amount == -1.0
    assert AgentAction.from_any({"command": "move", "amount": -1}).amount == -1.0


def test_action_space_contains():
    space = DefaultActionSpace()
    assert space.contains(0)
    assert space.contains("pickup")
    assert not space.contains(99)
