import gym
import osmenv
import data

environment = gym.make('OSMEnvironment', osm_data_file='data/network.osm.pbf')

print(environment.get_network_state(1))
environment.set_network_state(1, False)
print(environment.get_network_state(1))
environment.set_trip(osmenv.trip.TripStruct(
    data.trip744h['id'],
    data.trip744h['ways']
))
print(environment.observation_space['network_state'])
