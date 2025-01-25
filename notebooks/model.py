import gymnasium as gym
from gymnasium import spaces
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from stable_baselines3 import DDPG
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.env_checker import check_env

# Load and preprocess the data
data = pd.read_csv("data/soapnutshistory.csv")

# Fill missing values
data = data.ffill()

# Normalize numerical features
scaler = MinMaxScaler()
data[['Product Price', 'Organic Conversion Percentage', 
      'Ad Conversion Percentage', 'Total Profit', 
      'Total Sales']] = scaler.fit_transform(data[['Product Price', 
                                                    'Organic Conversion Percentage', 
                                                    'Ad Conversion Percentage', 
                                                    'Total Profit', 
                                                    'Total Sales']])

# Add cyclical date features
data['Report Date'] = pd.to_datetime(data['Report Date'])
data['Day'] = data['Report Date'].dt.day
data['Month'] = data['Report Date'].dt.month

# Create cyclical features
data['Day_sin'] = np.sin(2 * np.pi * data['Day'] / 30)
data['Day_cos'] = np.cos(2 * np.pi * data['Day'] / 30)
data['Month_sin'] = np.sin(2 * np.pi * data['Month'] / 12)
data['Month_cos'] = np.cos(2 * np.pi * data['Month'] / 12)

# Normalize cyclical features to [0, 1] from [-1, 1]
data['Day_sin'] = (data['Day_sin'] + 1) / 2
data['Day_cos'] = (data['Day_cos'] + 1) / 2
data['Month_sin'] = (data['Month_sin'] + 1) / 2
data['Month_cos'] = (data['Month_cos'] + 1) / 2

# Drop non-numeric columns
data = data.drop(columns=['Report Date', 'Day', 'Month'])

# Ensure all data is float32
data = data.astype(np.float32)


# Define the custom environment
class PriceOptimizationEnv(gym.Env):
    def __init__(self, data):
        super().__init__()
        
        self.data = data
        self.index = 0

        # Define action space (price adjustment: -0.1 to +0.1)
        self.action_space = spaces.Box(low=-0.1, high=0.1, shape=(1,), dtype=np.float32)

        # Define observation space based on the data columns
        num_features = len(data.columns) - 1
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(num_features,),
            dtype=np.float32
        )

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            np.random.seed(seed)
        self.index = 0
        state = self.data.iloc[self.index].values[:-1]
        return state, {}

    def step(self, action):
        current_price = self.data.iloc[self.index]['Product Price']
        new_price = np.clip(current_price + action[0], 0, 1)  # Ensure price stays valid

        self.index += 1
        done = self.index >= len(self.data) - 1

        if done:
            reward = 0
            next_state = np.zeros_like(self.data.iloc[0].values[:-1], dtype=np.float32)
        else:
            sales = self.data.iloc[self.index]['Total Sales']
            profit = self.data.iloc[self.index]['Total Profit']
            reward = (sales * profit) / (1 + abs(new_price - current_price))  # Normalized reward

            next_state = self.data.iloc[self.index].values[:-1]

        return next_state, reward, done, False, {}

# Initialize the environment
env = PriceOptimizationEnv(data)

# Validate the environment
check_env(env)
print("Environment is compatible with Gymnasium.")

# Define the RL model
n_actions = env.action_space.shape[-1]
action_noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))
model = DDPG("MlpPolicy", env, action_noise=action_noise, verbose=1)

# Train the model
print("Training the model...")
model.learn(total_timesteps=10000)

# Save the trained model
model.save("price_optimization_model")

# Test the trained model
print("\nTesting the model...")
state, _ = env.reset()
done = False
total_reward = 0

while not done:
    action, _ = model.predict(state)
    state, reward, done, truncated, _ = env.step(action)
    total_reward += reward
    print(f"Action: {action}, Reward: {reward:.2f}")

print(f"Total Reward: {total_reward:.2f}")
