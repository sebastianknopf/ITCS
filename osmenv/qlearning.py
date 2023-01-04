import time

import numpy as np

from osmenv.algorithm import TemporalDifferenceAlgorithm


class QLearning(TemporalDifferenceAlgorithm):

    def __init__(self, environment, episodes=0):
        super(QLearning, self).__init__(environment, episodes)

    def fit(self, gamma, epsilon, epsilon_decay=0.999, alpha=0.8, filename=None):

        # init process monitoring variables
        terminate = False  # terminate flag

        episode_steps = list()
        episode_rewards = list()
        episode_deltas = list()
        episode_durations = list()
        episode_epsilons = list()
        episode_count = 0

        # q-learning implementation
        while terminate is False:

            # resent environment and decay epsilon
            state, _ = self._env.reset()
            epsilon *= epsilon_decay

            # init episode monitoring variables
            episode_step = 0
            episode_reward = 0
            episode_delta = 0

            episode_start = time.time()

            # run each episode
            done = False
            while not done:

                # pick an action with epsilon-greedy strategy
                if np.random.random() < epsilon or np.sum(self._q_table[state]) == 0:
                    action = np.random.randint(0, self._env.action_space.n)
                else:
                    action = np.argmax(self._q_table[state])

                # apply action in environment
                next_state, reward, done, info = self._env.step(action)

                # store q value and next q value for convergence check
                q_value = self._q_table[state][action]
                next_q_value = q_value + reward + alpha * \
                               (gamma * np.max(self._q_table[next_state]) - self._q_table[state][action])

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
                if self._num_episodes > 0:
                    terminate = True if episode_count >= self._num_episodes else False
                else:
                    max_delta = np.max(episode_deltas[-200:])
                    terminate = True if max_delta < 0.0001 else False

        # create monitoring file name if required
        if filename is not None:
            self._create_monitoring_file(filename, 'Q-Learning',
                                         episode_count,
                                         episode_steps,
                                         episode_rewards,
                                         episode_deltas,
                                         episode_durations,
                                         episode_epsilons)

        return episode_count
