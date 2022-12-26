import random
import logging
import time

import numpy as np

import simulation
import osmenv
import common


# DQN implementation
def dqn(environment, model, df=0.999, e=0.5, e_df=0.95, num_episodes=500):

    # DQN monitoring and config variables
    cnt_episodes = 1
    min_blocked_ways = 1
    max_blocked_ways = 1
    min_start_distance = 10
    max_start_distance = 15

    for episode in range(num_episodes):

        # episode monitoring variables
        cnt_steps = 0
        start_time = time.time()

        # count down epsilon, reset environment and construct a random state
        e *= e_df
        done = False

        environment.reset()

        # select random trip and construct TripStruct, random position on current trip
        # apply trip to environment, select random ways of current trip and mark them as blocked
        trip = random.choice(simulation.trips)
        trip = osmenv.trip.TripStruct(trip['id'], trip['ways'])

        # select random ways of the trip to block on environment
        """blocked_ways = list()
        k = random.randint(min_blocked_ways, max_blocked_ways)
        for w in random.choices(trip.ways, k=k):
            # save way in list in order to
            blocked_ways.append(w)

            # block selected way on environment
            environment.set_network_state(False, way=w)"""

        blocked_ways = [1039]
        environment.set_network_state(False, way=1039)

        # move start position away from first blocked way
        # use this as position for simulation
        if len(blocked_ways) == 0:
            index = 0
        else:
            index = trip.ways.index(blocked_ways[0])

        """if index >= max_start_distance:
            position = trip.ways[random.randint(index - max_start_distance, index - min_start_distance)]
        else:
            position = trip.ways[random.randint(0, index)]"""

        position = 3532

        # apply trip and position to environment
        environment.set_trip(trip, position)

        logging.info('starting episode #%s with trip %s, start position %s, blocked way(s) %s',
                     str(cnt_episodes),
                     str(trip.id),
                     str(position),
                     str(blocked_ways)
                     )

        # construct current state from environment data by first reset call
        # check whether a deviation is required at all
        state = common.env_state_vector(environment, environment.observation_space['network_state'].n + 1)
        deviation_required = environment.get_deviation_required()

        if deviation_required:
            logging.info('deviation required, running episode')
        else:
            logging.info('no deviation required, skipping episode')

        # run episode in constructed environment
        while not done and deviation_required:

            # available actions
            available_actions = environment.get_available_actions()
            state_prediction = model.predict(state, verbose=0)

            # select an action by epsilon-greedy strategy
            if np.random.random() < e:
                action = random.choice(available_actions)
            else:
                action = common.argmax_restricted(
                    state_prediction[0],
                    available_actions
                )

            # apply action and find state, find available actions of new state after applying action
            next_state, reward, done, info = environment.step(action)
            next_state = common.env_state_vector(environment, environment.observation_space['network_state'].n + 1)

            available_actions = environment.get_available_actions()

            #logging.info(str(position) + ' > ' + str(info['vehicle_position_way']) + ': ' + str(reward))

            # build maximum reward by observing all available actions in next state
            target = reward + df * common.max_restricted(
                model.predict(next_state, verbose=0)[0],
                available_actions
            )

            # build target vector for model training
            target_vector = state_prediction[0]
            target_vector[action] = target

            model.fit(
                state,
                target_vector.reshape(-1, environment.action_space.n),
                epochs=1,
                verbose=0
            )

            state = next_state
            position = info['vehicle_position_way']

            cnt_steps += 1

        # log episode monitoring
        end_time = time.time()

        logging.info('finished episode #%s after %s steps in %s with reward of %s',
                     str(cnt_episodes),
                     str(cnt_steps),
                     '{:5.3f}s'.format(end_time - start_time),
                     str(reward)
                     )

        cnt_episodes += 1
