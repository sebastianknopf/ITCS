import gym
import osmenv

environment = gym.make('OSMEnvironment', osm_data_file='data/network.osm.pbf')

print(environment.get_network_state(1))
environment.set_network_state(1, False)
print(environment.get_network_state(1))
