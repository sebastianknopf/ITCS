import time

import numpy as np

from osmenv.sarsa import Sarsa


class ExpectedSarsa(Sarsa):

    def __init__(self, environment, episodes=0):
        super(ExpectedSarsa, self).__init__(environment, episodes)

    def fit(self, gamma, epsilon, epsilon_decay=0.999, alpha=0.8, filename=None):

        # init process monitoring variables
        terminate = False  # terminate flag

        episode_steps = list()
        episode_rewards = list()
        episode_deltas = list()
        episode_durations = list()
        episode_epsilons = list()
        episode_count = 0

        # expected sarsa implementation
        while terminate is False:

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
                if self._num_episodes > 0:
                    terminate = True if episode_count >= self._num_episodes else False
                else:
                    max_delta = np.max(episode_deltas[-200:])
                    terminate = True if max_delta < 0.0001 else False

        # create monitoring file name if required
        if filename is not None:
            self._create_monitoring_file(filename, 'Expected SARSA',
                                         episode_count,
                                         episode_steps,
                                         episode_rewards,
                                         episode_deltas,
                                         episode_durations,
                                         episode_epsilons)

        return episode_count

    def _action_probability(self, state, epsilon):

        # calculate the probability for the actions of the state to be chosen
        probability = [epsilon / self._env.action_space.n] * self._env.action_space.n
        probability[np.argmax(self._q_table[state])] += 1.0 - epsilon

        return probability
