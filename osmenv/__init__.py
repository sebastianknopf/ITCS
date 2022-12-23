import gym

gym.envs.register(
    id='OSMEnvironment',
    entry_point='osmenv.env:OSMEnvironment'
)