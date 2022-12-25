import numpy as np

from osmenv.env import OSMEnvironment


def env_state_vector(environment: OSMEnvironment):
    es, _ = environment.get_state()

    state = np.array(es['network_state'])
    state = np.insert(state, 0, es['vehicle_position'])

    return state
