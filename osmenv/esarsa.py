import ast
import time
import json

import numpy as np
import pandas as pd


class ExpectedSarsa:

    def __init__(self, environment):

        self._env = environment

        # define fixed epsilon
        self._epsilon_min = 0.025

        # init q table
        self._q_table = dict()

        for r in range(self._env.observation_space[0].n):
            for d in range(self._env.observation_space[1].n):
                for s in range(self._env.observation_space[2].n):
                    self._q_table[(r, d, s)] = np.zeros(self._env.action_space.n)

    def fit(self, gamma, epsilon, epsilon_decay=0.999, alpha=0.8, filename=None):

        # init process monitoring variables
        convergence = False  # convergence flag

        episode_steps = list()
        episode_rewards = list()
        episode_deltas = list()
        episode_durations = list()
        episode_epsilons = list()
        episode_count = 0

        # q-learning implementation
        while convergence is False:

            # resent environment and decay epsilon
            state, _ = self._env.reset()
            action = self._strategy(state, epsilon)

            epsilon = max(epsilon * epsilon_decay, self._epsilon_min)

            # init episode monitoring variables
            episode_step = 0
            episode_reward = 0
            episode_delta = 0

            episode_start = time.time()

            # run each episode
            done = False
            while not done:

                # apply action in environment
                next_state, reward, done, info = self._env.step(action)

                # store q value and next q value for convergence check
                action_probability = self._action_probability(state, epsilon)
                next_actions = self._q_table[next_state]

                expected_action_update = sum([a * b for a, b in zip(action_probability, next_actions)])

                q_value = self._q_table[state][action]
                next_q_value = q_value + reward + alpha * \
                               (gamma * expected_action_update - self._q_table[state][action])

                self._q_table[state][action] = next_q_value
                state = next_state

                episode_step += 1
                episode_reward += (gamma ** episode_step) * reward
                episode_delta = max(episode_delta, q_value - next_q_value)

            episode_end = time.time()

            episode_count += 1

            episode_steps.append(episode_step)
            episode_rewards.append(episode_reward)
            episode_deltas.append(np.absolute(episode_delta))
            episode_durations.append(episode_end - episode_start)
            episode_epsilons.append(epsilon)

            if len(episode_deltas) > 200:
                max_delta = np.max(episode_deltas[-200:])
                convergence = True if max_delta < 0.0001 else False

        # create monitoring file name if required
        if filename is not None:

            df = pd.DataFrame({
                'episode': [e for e in range(1, episode_count + 1)],
                'steps': episode_steps,
                'reward': episode_rewards,
                'delta': episode_deltas,
                'duration': episode_durations,
                'epsilon': episode_epsilons
            })

            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='SARSA', index=False)

            writer.close()

        return episode_count

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

    def _strategy(self, state, epsilon):

        if np.random.random() < epsilon or np.sum(self._q_table[state]) == 0:
            action = np.random.randint(0, self._env.action_space.n)
        else:
            action = np.argmax(self._q_table[state])

        return action

    def _action_probability(self, state, epsilon):

        # calculate the probability for the actions of the state to be chosen
        probability = [epsilon / self._env.action_space.n] * self._env.action_space.n
        probability[np.argmax(self._q_table[state])] += 1.0 - epsilon

        return probability
