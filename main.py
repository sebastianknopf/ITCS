import gym

from argparse import ArgumentParser
from osmenv.qlearning import QLearning
from osmenv.sarsa import Sarsa
from osmenv.esarsa import ExpectedSarsa


# add options parser
parser = ArgumentParser()
parser.add_argument('-q', '--q-learning', dest='run_q_learning', action='store_true')
parser.add_argument('-s', '--sarsa', dest='run_sarsa', action='store_true')
parser.add_argument('-e', '--expected-sarsa', dest='run_esarsa', action='store_true')
parser.add_argument('-f', '--full', dest='env_full', action='store_true')

args = parser.parse_args()

# load simulation environment
if args.env_full:

    env = gym.make('Environment', osm_file='data/network.osm.pbf', route_files=[
        'data/city2.json',
        'data/land743.json',
        'data/land744.json',
        'data/village715.json'
    ], deviation_files=[
        'data/city2_dev1.json',
        'data/city2_dev2.json',
        'data/city2_dev3.json',
        'data/city2_dev4.json',
        'data/land743_dev1.json',
        'data/land743_dev2.json',
        'data/land744_dev1.json',
        'data/land744_dev2.json',
        'data/land744_dev3.json',
        'data/village715_dev1.json',
        'data/village715_dev2.json',
        'data/village715_dev3.json',
        'data/village715_dev4.json'
    ], scenarios=[
        1772,
        23937,
        10292
    ])
else:

    env = gym.make('Environment', osm_file='data/network.osm.pbf', route_files=[
        'data/city2.json',
        'data/land743.json',
        'data/land744.json'
    ], deviation_files=[
        'data/city2_dev1.json',
        'data/city2_dev2.json',
        'data/city2_dev3.json',
        'data/city2_dev4.json',
        'data/land743_dev1.json',
        'data/land743_dev2.json',
        'data/land744_dev1.json',
        'data/land744_dev2.json',
        'data/land744_dev3.json'
    ], scenarios=[
        1772,
        23937,
        10292
    ])

env.set_weights({
    'length': 2,
    'stops': 4
})

# run learning algorithms according to options
if args.run_q_learning:

    print('running q-learning ...')

    q_learning = QLearning(env)
    c = q_learning.fit(gamma=0.95, epsilon=0.5, filename='output/q-learning.xlsx')
    q_learning.save('output/q-learning.json')

    print('found convergence after {0} episodes'.format(c))
    print()

if args.run_sarsa:

    print('running sarsa ...')

    sarsa = Sarsa(env)
    c = sarsa.fit(gamma=0.95, epsilon=0.5, epsilon_decay=0.9, filename='output/sarsa.xlsx')
    sarsa.save('output/sarsa.json')

    print('found convergence after {0} episodes'.format(c))
    print()

if args.run_esarsa:
    print('running expected sarsa ...')

    expected_sarsa = ExpectedSarsa(env)
    c = expected_sarsa.fit(gamma=0.95, epsilon=0.5, epsilon_decay=0.9, filename='output/expected-sarsa.xlsx')
    expected_sarsa.save('output/expected-sarsa.json')

    print('found convergence after {0} episodes'.format(c))
    print()

