import gym
import json

from osmenv.routing import OfflineRouter
from osmenv.data import construct_dataclass
from osmenv.data import Route
from osmenv.data import Deviation


class Environment(gym.Env):

    def __init__(self, osm_file, route_files, deviation_files, scenarios):
        super(Environment, self).__init__()

        # load OSM data in order to calculate length and verify routes
        self._router = OfflineRouter(osm_file, {
            'name': 'bus',
            'weights': {
                'motorway': 0.5,
                'trunk': 0.75,
                'primary': 1.0,
                'secondary': 1.0,
                'tertiary': 1.0,
                'unclassified': 1.0,
                'residential': 1.0,
                'living_street': 1.0,
                'pedestrian': 1.0,
                'footway': 1.0
            },
            'access': ['access', 'walk', 'psv']
        })

        # load available routes
        self._routes = list()

        for route_file in route_files:
            self._load_json_route(route_file)

        # load available deviations
        self._deviations = list()

        for deviation_file in deviation_files:
            self._load_json_deviation(deviation_file)

        # store all sectors which could be blocked as scenario
        self._scenarios = scenarios

        # member variables representing the current state
        self._status_route = 0  # defines the current route viewed
        self._status_deviation = 0  # defines the current deviation the trip remains in
        self._status_scenario = 0  # defines the blocked sector in this

        # define weights for reward calculation
        self._weights = {
            'length': 1,
            'share': 1,
            'stops': 2
        }

        self._max_weight = 4

        # define action and observation space
        self.action_space = gym.spaces.Discrete(len(self._deviations) + 1)  # each possible deviation is an action

        self.observation_space = gym.spaces.Tuple([
            gym.spaces.Discrete(len(self._routes)),
            gym.spaces.Discrete(len(self._deviations) + 1),  # action 0 is no deviation, all others are deviations
            gym.spaces.Discrete(len(scenarios))
        ])

    def set_weights(self, weights, max_weight=4):
        self._weights = weights
        self._max_weight = max_weight

    def step(self, action):

        self._status_deviation = action

        # get observation, reward, terminated flag and info
        observation = self._get_observation()
        reward, terminated = self._get_reward(action)
        info = self._get_info()

        return observation, reward, terminated, info

    def reset(self, **kwargs):

        # reset environment to random variable
        self._status_route = self.np_random.randint(len(self._routes))
        self._status_deviation = 0
        self._status_scenario = self.np_random.randint(len(self._scenarios))

        # get observation and info
        observation = self._get_observation()
        info = self._get_info()

        return observation, info

    def render(self, mode='human'):
        pass

    def _get_observation(self):
        return self._status_route, self._status_deviation, self._status_scenario

    def _get_info(self):
        return {
            'route': self._routes[self._status_route],
            'deviation': self._deviations[self._status_deviation - 1] if self._status_deviation > 0 else None,
            'scenario': self._scenarios[self._status_scenario]
        }

    def _get_reward(self, action):

        # extract current route and used scenario
        route = self._routes[self._status_route]
        scenario = self._scenarios[self._status_scenario]

        # construct current node sequence out of route and chosen deviation
        if self._status_deviation > 0:

            # a deviation was chosen, review the effects of this deviation
            deviation_nodes = self._deviations[self._status_deviation - 1].nodes
            deviation_start = deviation_nodes[0]
            deviation_end = deviation_nodes[-1]

            # check whether deviation begins and ends in the route
            # otherwise it would never be reached, this the vehicle is not deviated
            if deviation_start in route.nodes and deviation_end in route.nodes:

                # take head and tail of current route and put deviation in between
                route_head = route.nodes[0:route.nodes.index(deviation_start)]
                route_tail = route.nodes[route.nodes.index(deviation_end) + 1:-1]

                vehicle_node_sequence = route_head + deviation_nodes + route_tail
            else:
                vehicle_node_sequence = route.nodes
        else:

            # no deviation chosen, thus no nodes available... store this for further processing
            deviation_nodes = list()

            # no deviation was chosen, vehicle remains on route
            vehicle_node_sequence = route.nodes

        terminated = self._scenarios[self._status_scenario] not in vehicle_node_sequence

        # assess action critically
        if scenario in route.nodes:  # deviation is required at all for current trip
            if scenario not in vehicle_node_sequence:  # deviation was successful in general, further review required

                # consider total length of original route and deviation route
                original_route_length = self._router.route_length(route.nodes)
                deviated_route_length = self._router.route_length(vehicle_node_sequence)

                length_factor = (original_route_length / deviated_route_length) ** \
                                (self._weights['length'] / self._max_weight)

                # consider how many stops are missing due to used deviation
                reached_stops = 0
                for stop in route.stops:
                    if stop['node'] in vehicle_node_sequence:
                        reached_stops += 1

                stop_factor = (reached_stops / len(route.stops)) ** \
                              (self._weights['stops'] / self._max_weight)

                # use all factors to determine final deviation quality
                reward = 1 * length_factor * stop_factor
            else:  # deviation was NOT successful at all, trip still affected by scenario
                reward = -1
        else:  # deviation is NOT required for current trip
            if action < 1:  # there was no deviation chosen at all, perfectly
                reward = 1
            else:
                reward = -1  # there was a deviation chosen even if it would not be required ... suboptimal

        return reward, terminated

    def _load_json_route(self, filename):

        with open(filename, 'r') as f:
            route_dict = json.load(f)

            f.close()

        # add route to member
        route = construct_dataclass(Route, route_dict)
        self._routes.append(route)

    def _load_json_deviation(self, filename):

        with open(filename, 'r') as f:
            deviation_dict = json.load(f)

            f.close()

        # add trip route to member
        deviation = construct_dataclass(Deviation, deviation_dict)
        self._deviations.append(deviation)
