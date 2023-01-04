import abc
import ast
import json

import numpy as np
import pandas as pd


class TemporalDifferenceAlgorithm:

    def __init__(self, environment, episodes=0):

        self._env = environment

        # define convergence criteria
        self._num_episodes = episodes

        # init q table
        self._q_table = dict()

        for r in range(self._env.observation_space[0].n):
            for d in range(self._env.observation_space[1].n):
                for s in range(self._env.observation_space[2].n):
                    self._q_table[(r, d, s)] = np.zeros(self._env.action_space.n)

    @abc.abstractmethod
    def fit(self, gamma, epsilon, epsilon_decay=0.999, alpha=0.8, filename=None):
        return

    def predict(self, state):

        if len(state) == 2:
            state = state[0], 0, state[1]

        if state in self._q_table.keys():
            return np.argmax(self._q_table[state])
        else:
            return -1

    def load(self, filename):

        # read JSON data
        with open(filename, 'r') as f:
            q_data = json.load(f)

            f.close()

        # remap q data to q-table
        q_table = {ast.literal_eval(k): np.array(v) for k, v in q_data.items()}
        self._q_table = q_table

    def save(self, filename):

        # re-map q-table data to JSONable format
        q_data = {str(k): list(v) for k, v in self._q_table.items()}

        # write JSON file
        with open(filename, 'w') as f:
            json.dump(q_data, f)

            f.close()

    @staticmethod
    def _create_monitoring_file(filename, datatype, e_count, e_steps, e_rewards, e_deltas, e_durations, e_epsilons):

        if filename is not None:

            df = pd.DataFrame({
                'episode': [e for e in range(1, e_count + 1)],
                'steps': e_steps,
                'reward': e_rewards,
                'delta': e_deltas,
                'duration': e_durations,
                'epsilon': e_epsilons
            })

            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            df.to_excel(writer, sheet_name=datatype, index=False)

            writer.close()
