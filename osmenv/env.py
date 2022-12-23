import gym

from osmenv.osm import OSMNetworkHandler
from osmenv.trip import TripStruct

import numpy as np


class OSMEnvironment(gym.Env):

    def __init__(self, osm_data_file):
        super(OSMEnvironment, self).__init__()

        # action space and observation space are not used internally, for external use
        # function get_available_actions(way) is defined, observation space is not required
        # reset them to none
        self.action_space = None
        self.observation_space = None

        # load OSM network data from compressed PBF file
        # convert OSM network to a set of ways and links in between
        osm_handler = OSMNetworkHandler()
        osm_handler.apply_file(osm_data_file, locations=True)

        self._ways, self._links = osm_handler.generate_network()
        self._size = len(self._ways)

        # internal status variables, _vehicle_position is ID of way where vehicle remains currently
        # _network_state represents usability of each way in the network, default value is 1 for
        # every way being usable initially
        self._vehicle_position = self.np_random.randint(0, self._size)
        self._network_state = np.empty(self._size)
        self._network_state.fill(1)

        # trip container, required to determine a start-, terminal- or deviation state
        self._trip = None

        # container for indicating certain ways in different status types
        self._start_states = list()
        self._terminal_states = list()
        self._deviation_states = list()
        self._unreachable_states = list()

        # build status context first time
        self._update_state_context()

    def set_trip(self, trip: TripStruct, position: int = 0):
        assert trip is None or isinstance(trip, TripStruct), \
            'parameter trip must represent a valid osmenv.trip.Trip object'

        self._trip = trip

        if position > 0 and self._trip is not None:
            # ensure that position is available at all
            assert position in self._ways.keys(), \
                'parameter way must represent a valid way ID'

            self._vehicle_position = position

        # update possible start- and terminal states
        self._update_state_context()

    def get_network_state(self, way):
        assert way in self._ways.keys(), \
            'parameter way must represent a valid way ID'

        return self._network_state[list(self._ways.keys()).index(way)] == 1

    def set_network_state(self, way, state: bool):
        assert way in self._ways.keys(), \
            'parameter way must represent a valid way ID'

        self._network_state[list(self._ways.keys()).index(way)] = 1 if state is True else 0

        # update possible start- and terminal states
        self._update_state_context()

    def get_available_actions(self, way: int = 0):

        # verify way parameter, use current vehicle position if way is not set
        if way == 0:
            way = self._vehicle_position
        else:
            assert way in self._ways.keys(), \
                'parameter way must represent a valid way ID'

        # find possible actions which can be applied from a certain way
        actions = list()
        if way in self._links.keys():
            actions = self._links[way]

        # return only actions which are not part of unreachable state list
        return [a for a in actions if a not in self._unreachable_states]

    def get_deviation_required(self):
        return len(self._start_states) > 0

    def step(self, action):

        # ensure that action is available from current vehicle position
        actions = list()
        if self._vehicle_position in self._links.keys():
            actions = self._links[self._vehicle_position]

        actions = [a for a in actions if a not in self._unreachable_states]

        assert action in actions, \
            'action not available for vehicle position'

        # save last state to determine reward after applying action
        # set vehicle position to the way determined by the action
        last_state = self._vehicle_position
        self._vehicle_position = action

        # check whether a terminal state is reached
        terminated = False
        if self._vehicle_position in self._terminal_states:
            terminated = True

        # get reward of last state and current state
        reward = self._get_reward(last_state, self._vehicle_position)

        # get observation data
        observation = self._get_observation()
        info = self._get_info()

        return observation, reward, terminated, False, info

    def reset(self):
        super().reset()

        # reset agents location and ensure that agents location is not a terminal location

        # re-create status context
        self._update_state_context()

        return self._get_observation(), self._get_info()

    def render(self, mode='human', close=False):
        pass

    def _get_observation(self):
        return {
            'vehicle_position': self._vehicle_position,
            'network_state': self._network_state,
            'start_states': self._start_states,
            'terminal_states': self._terminal_states,
            'deviation_states': self._deviation_states,
            'unreachable_states': self._unreachable_states
        }

    def _get_info(self):
        return {
            'trip': self._trip
        }

    def _update_state_context(self):

        self._start_states = list()
        self._terminal_states = list(self._ways)
        self._deviation_states = list()
        self._unreachable_states = list()

        # only if there's a valid trip object, a start state could be reached
        if self._trip is not None:

            # iterate over all ways of current trip to check whether there's a way blocked currently
            # remember: only if there's a blocked way, a start state could be reached
            first = last = 0
            for w in self._trip.ways:
                if w in self._ways.keys():
                    if self._network_state[list(self._ways.keys()).index(w)] == 0:
                        if first == 0:
                            first = self._trip.ways.index(w)

                        last = self._trip.ways.index(w)

            # reset lists, every state is a deviation state by default now
            self._start_states = list()
            self._terminal_states = list()
            self._deviation_states = list(self._ways)
            self._unreachable_states = list()

            # iterate over all ways and determine start-, terminal- and deviation states
            for w in self._trip.ways:
                if self._trip.ways.index(w) < first:
                    self._deviation_states.remove(w)
                    self._start_states.append(w)
                elif first < self._trip.ways.index(w) < last:
                    pass # simply do nothing here, the way is marked as deviation yet
                elif self._trip.ways.index(w) > last:
                    self._deviation_states.remove(w)
                    self._terminal_states.append(w)
                else:
                    self._deviation_states.remove(w)
                    self._unreachable_states.append(w)

    def _get_reward(self, last_state, current_state):
        if last_state in self._start_states and current_state in self._start_states:
            return 1
        elif last_state in self._start_states and current_state in self._deviation_states:
            return -1
        elif last_state in self._deviation_states and current_state in self._deviation_states:
            return 0
        elif last_state in self._deviation_states and current_state in self._terminal_states:
            return 1
