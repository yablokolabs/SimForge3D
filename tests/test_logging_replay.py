from pathlib import Path

from simforge3d import NavigationScenario, SimForgeEnv


def test_episode_logging_and_replay(tmp_path: Path):
    env = SimForgeEnv(
        NavigationScenario(obstacles=[], max_steps=1),
        config={
            "headless": True,
            "max_steps": 1,
            "enable_episode_logging": True,
            "enable_replay": True,
            "log_dir": str(tmp_path / "logs"),
            "replay_dir": str(tmp_path / "replays"),
        },
    )
    env.reset(seed=4)
    env.step("noop")
    env.close()
    assert list((tmp_path / "logs").glob("episode_*.jsonl"))
    assert list((tmp_path / "replays").glob("replay_*.jsonl"))
