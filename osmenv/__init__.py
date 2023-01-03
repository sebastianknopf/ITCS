import gym

gym.envs.register(
    id='Environment',
    entry_point='osmenv.env:Environment',
    max_episode_steps=100
)