import gym
import osmenv

environment = gym.make('OSMEnvironment', osm_data_file='data/network.osm.pbf')

print(environment.get_network_state(index=1))
environment.set_network_state(False, way=2)
print(environment.get_network_state(index=1))
"""environment.set_trip(osmenv.trip.TripStruct(
    data.trip744h['id'],
    data.trip744h['ways']
))"""

state, _ = environment.reset(seed=15)
print(environment.observation_space.sample())
print(state['vehicle_position'])
print(list(state['network_state']))
