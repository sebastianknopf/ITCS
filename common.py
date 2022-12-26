import numpy as np

from osmenv.env import OSMEnvironment


def env_state_vector(environment: OSMEnvironment, env_input_layer_size):
    es, _ = environment.get_state()

    state = np.array(es['network_state'])
    state = np.insert(state, 0, es['vehicle_position'])

    return state.reshape(-1, env_input_layer_size)


def argmax_restricted(array, restriction):
    kv_map = {k: v for k, v in enumerate(array) if k in restriction}
    result = max(kv_map, key=kv_map.get)

    return result


def max_restricted(array, restriction):
    kv_map = {k: v for k, v in enumerate(array) if k in restriction}
    result = max(kv_map.values())

    return result
