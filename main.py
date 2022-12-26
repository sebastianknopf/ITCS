import gym
import logging

from keras.models import Sequential
from keras.layers import InputLayer
from keras.layers import LeakyReLU
from keras.layers import Dense

from rlearning.dqn import dqn

# set log level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %I:%M:%S'
)

# load environment
environment = gym.make('OSMEnvironment', osm_data_file='data/network.osm.pbf')

env_input_layer_size = environment.observation_space['network_state'].n + 1
env_output_layer_size = environment.action_space.n
env_hidden_layer_size = int(env_input_layer_size * 0.6667 + env_output_layer_size)

# create neural network model
model = Sequential()
model.add(InputLayer(batch_input_shape=(1, env_input_layer_size), name='InputLayer'))
model.add(Dense(env_hidden_layer_size, name='HiddenLayer1'))
model.add(LeakyReLU(alpha=0.5))
model.add(Dense(env_hidden_layer_size, name='HiddenLayer2'))
model.add(LeakyReLU(alpha=0.25))
model.add(Dense(env_output_layer_size, activation='linear', name='OutputLayer'))

model.compile(loss='mse', optimizer='adam', metrics=['mae'])

# run training DQN
dqn(
    environment, model,
    num_episodes=20
)
