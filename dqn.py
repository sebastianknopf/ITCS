import gym
import random
import logging

import numpy as np

import data
import osmenv
import common

from keras.models import Sequential
from keras.layers import InputLayer
from keras.layers import Dense

# set log level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %I:%M:%S'
)

# load environment
environment = gym.make('OSMEnvironment', osm_data_file='data/network.osm.pbf')

# create neural network model
model = Sequential()
model.add(InputLayer(batch_input_shape=(1, 1246)))
model.add(Dense(environment.observation_space['network_state'].n + 1, activation='relu'))
model.add(Dense(environment.action_space.n, activation='linear'))
model.compile(loss='mse', optimizer='adam', metrics=['mae'])

# DQN implementation
df = 0.95
e = 0.5
e_df = 0.999

num_episodes = 100
cnt_episodes = 1
max_blocked_ways = 1

for episode in range(num_episodes):

    # count down epsilon, reset environment and construct a random state
    e *= e_df
    done = False

    environment.reset()

    # select random trip and construct TripStruct, random position on current trip
    # apply trip to environment, select random ways of current trip and mark them as blocked
    trip = random.choice(data.trips)
    trip = osmenv.trip.TripStruct(trip['id'], trip['ways'])

    position = random.choice(trip.ways)

    environment.set_trip(trip, position)

    logging.info('starting episode #%s with trip %s, start position %s',
                 str(cnt_episodes),
                 str(trip.id),
                 str(position)
                )

    k = random.randint(0, max_blocked_ways)
    for w in random.choices(trip.ways, k=k):
        environment.set_network_state(False, way=w)

        logging.info('blocked way %s', str(w))

    if k == 0:
        logging.info('no blocked ways')

    # construct current state from environment data
    state = common.env_state_vector(environment)

    logging.info('deviation required? %s', str(environment.get_deviation_required()))

    """while not done:

        

        if np.random.random() < e:
            action = random.choice(environment.get_available_actions())
        else:
            action = np.argmax(
                model.predict(
                    np.identity(1246)[state:state + 1]
                )
            )

        next_state, reward, done, _ = environment.step(action)

        target = reward + df * np.max(
            model.predict(
                np.identity(1246)[next_state:next_state + 1]
            )
        )

        target_vector = model.predict(
            np.identity(1246)[state:state + 1]
        )[0]

        target_vector[action] = target

        model.fit(
            np.identity(1246)[state:state + 1],
            target_vector.reshape(-1, 1245),
            epochs=1,
            verbose=0
        )

        state = next_state """

    cnt_episodes += 1