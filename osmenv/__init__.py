import gym

gym.envs.register(
    id='OSMEnvironment',
    entry_point='osmenv.env:OSMEnvironment',
    max_episode_steps=250
)