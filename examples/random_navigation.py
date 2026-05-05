"""Run a random policy in the navigation scenario."""

from __future__ import annotations

import argparse

from simforge3d import NavigationScenario, SimForgeEnv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true", help="Run without rendering")
    parser.add_argument("--episodes", type=int, default=1)
    parser.add_argument("--max-steps", type=int, default=200)
    args = parser.parse_args()

    env = SimForgeEnv(
        scenario=NavigationScenario(max_steps=args.max_steps),
        config={"headless": args.headless, "max_steps": args.max_steps},
    )
    try:
        for episode in range(args.episodes):
            obs = env.reset(seed=episode)
            done = False
            total_reward = 0.0
            while not done:
                obs, reward, done, info = env.step(env.action_space.sample())
                total_reward += reward
                if not args.headless:
                    env.render()
            print(
                f"episode={episode} reward={total_reward:.3f} "
                f"success={info['success']} steps={info['step_count']}"
            )
    finally:
        env.close()


if __name__ == "__main__":
    main()
