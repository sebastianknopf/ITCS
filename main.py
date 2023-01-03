import gym

from argparse import ArgumentParser
from osmenv.qlearning import QLearning


# add options parser
parser = ArgumentParser()
parser.add_argument('-q', '--q-learning', dest='run_q_learning', action='store_true')
parser.add_argument('-s', '--sarsa', dest='run_sarsa', action='store_true')

args = parser.parse_args()

# load simulation environment
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
    'data/land744_dev3.json',
], scenarios=[
    10012,
    1772,
    23937
])

env.set_weights({
    'length': 2,
    'stops': 4
})

# run q learning algorithms according to options
if args.run_q_learning:

    print('running q-learning ...')

    q_learning = QLearning(env)
    c = q_learning.fit(gamma=0.95, epsilon=0.8, filename='output/q-learning.xlsx')
    q_learning.save('output/q-learning.json')

    print('found convergence after {0} episodes'.format(c))
    print()

if args.run_sarsa:
    pass

