"""Tiny scripted pick-and-place example."""

from __future__ import annotations

from simforge3d import PickPlaceScenario, SimForgeEnv


def main() -> None:
    env = SimForgeEnv(PickPlaceScenario(), headless=True)
    try:
        obs = env.reset(seed=7)
        total = 0.0
        # Move toward payload, pick it up, move toward goal, drop it.
        scripted_actions = ["move_forward"] * 10 + ["pickup"] + ["move_forward"] * 25 + ["drop"]
        for action in scripted_actions:
            obs, reward, done, info = env.step(action)
            total += reward
            if done:
                break
        print({"reward": round(total, 3), "done": done, "info": info, "last_obs": obs})
    finally:
        env.close()


if __name__ == "__main__":
    main()
