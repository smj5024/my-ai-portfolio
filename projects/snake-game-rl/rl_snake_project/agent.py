"""
Deep Q-Network (DQN) Agent for Snake Game

This module implements the DQN agent that learns to play Snake through
reinforcement learning. It includes experience replay, target networks,
and epsilon-greedy exploration.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
import os


class DQN(nn.Module):
    """
    Deep Q-Network for Snake game.
    
    A simple feedforward neural network that takes the game state as input
    and outputs Q-values for each possible action.
    
    Architecture:
        Input (11) -> Hidden Layer (256) -> Hidden Layer (128) -> Output (3)
    """
    
    def __init__(self, input_size=11, hidden_size1=256, hidden_size2=128, output_size=3):
        """
        Initialize the DQN network.
        
        Args:
            input_size (int): Size of input state vector (default: 11 for Snake)
            hidden_size1 (int): Size of first hidden layer
            hidden_size2 (int): Size of second hidden layer
            output_size (int): Size of output (number of actions, default: 3)
        """
        super(DQN, self).__init__()
        
        self.fc1 = nn.Linear(input_size, hidden_size1)
        self.fc2 = nn.Linear(hidden_size1, hidden_size2)
        self.fc3 = nn.Linear(hidden_size2, output_size)
        
        self.relu = nn.ReLU()
    
    def forward(self, x):
        """
        Forward pass through the network.
        
        Args:
            x (torch.Tensor): Input state tensor
            
        Returns:
            torch.Tensor: Q-values for each action
        """
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        return self.fc3(x)


class ReplayBuffer:
    """
    Experience Replay Buffer.
    
    Stores past experiences (state, action, reward, next_state, done) and
    samples random batches for training. This breaks temporal correlations
    in the data and stabilizes training.
    """
    
    def __init__(self, capacity=100000):
        """
        Initialize the replay buffer.
        
        Args:
            capacity (int): Maximum number of experiences to store
        """
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        """
        Add a new experience to the buffer.
        
        Args:
            state (np.ndarray): Current state
            action (int): Action taken
            reward (float): Reward received
            next_state (np.ndarray): Next state after action
            done (bool): Whether episode ended
        """
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size):
        """
        Sample a random batch of experiences.
        
        Args:
            batch_size (int): Number of experiences to sample
            
        Returns:
            tuple: Batch of states, actions, rewards, next_states, and dones
        """
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        return (
            np.array(states),
            np.array(actions),
            np.array(rewards),
            np.array(next_states),
            np.array(dones)
        )
    
    def __len__(self):
        """Return current size of the buffer."""
        return len(self.buffer)


class DQNAgent:
    """
    DQN Agent for learning to play Snake.
    
    This agent uses:
    - Experience Replay for stable training
    - Target Network for stable Q-value targets
    - Epsilon-Greedy exploration for balancing exploration/exploitation
    - Double DQN for reducing Q-value overestimation
    
    Attributes:
        state_size (int): Size of the state space
        action_size (int): Size of the action space
        learning_rate (float): Learning rate for the optimizer
        gamma (float): Discount factor for future rewards
        epsilon (float): Exploration rate
        epsilon_min (float): Minimum exploration rate
        epsilon_decay (float): Decay rate for epsilon
    """
    
    def __init__(
        self,
        state_size=11,
        action_size=3,
        learning_rate=0.001,
        gamma=0.95,
        epsilon=1.0,
        epsilon_min=0.01,
        epsilon_decay=0.995,
        batch_size=64,
        memory_size=100000,
        target_update=1000,
        device=None
    ):
        """
        Initialize the DQN agent.
        
        Args:
            state_size (int): Size of input state vector
            action_size (int): Number of possible actions
            learning_rate (float): Learning rate for optimizer
            gamma (float): Discount factor (how much to value future rewards)
            epsilon (float): Initial exploration rate
            epsilon_min (float): Minimum exploration rate
            epsilon_decay (float): How fast epsilon decays
            batch_size (int): Batch size for training
            memory_size (int): Replay buffer capacity
            target_update (int): Steps between target network updates
            device (str): Device to run on ('cuda' or 'cpu')
        """
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.target_update = target_update
        
        # Set device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        # Initialize networks
        self.policy_net = DQN(state_size, 256, 128, action_size).to(self.device)
        self.target_net = DQN(state_size, 256, 128, action_size).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        
        # Initialize optimizer and replay buffer
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=learning_rate)
        self.memory = ReplayBuffer(memory_size)
        
        self.steps = 0
    
    def select_action(self, state, training=True):
        """
        Select an action using epsilon-greedy policy.
        
        Args:
            state (np.ndarray): Current game state
            training (bool): Whether in training mode (use exploration)
            
        Returns:
            int: Selected action (0=straight, 1=right, 2=left)
        """
        if training and random.random() < self.epsilon:
            # Exploration: random action
            return random.randint(0, self.action_size - 1)
        
        # Exploitation: best action according to Q-network
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.policy_net(state_tensor)
            return q_values.argmax().item()
    
    def remember(self, state, action, reward, next_state, done):
        """
        Store experience in replay buffer.
        
        Args:
            state (np.ndarray): Current state
            action (int): Action taken
            reward (float): Reward received
            next_state (np.ndarray): Next state
            done (bool): Whether episode ended
        """
        self.memory.push(state, action, reward, next_state, done)
    
    def train(self):
        """
        Train the network on a batch of experiences.
        
        Uses Double DQN loss for more stable training.
        """
        if len(self.memory) < self.batch_size:
            return None
        
        # Sample batch from replay buffer
        states, actions, rewards, next_states, dones = self.memory.sample(self.batch_size)
        
        # Convert to tensors
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)
        
        # Compute current Q values
        current_q_values = self.policy_net(states).gather(1, actions.unsqueeze(1))
        
        # Compute target Q values using Double DQN
        with torch.no_grad():
            # Get best actions from policy network
            next_actions = self.policy_net(next_states).argmax(1, keepdim=True)
            # Get Q values for those actions from target network
            next_q_values = self.target_net(next_states).gather(1, next_actions)
            # Compute target: r + gamma * Q'(s', a*)
            target_q_values = rewards.unsqueeze(1) + (1 - dones.unsqueeze(1)) * self.gamma * next_q_values
        
        # Compute loss
        loss = nn.MSELoss()(current_q_values, target_q_values)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Update target network periodically
        self.steps += 1
        if self.steps % self.target_update == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        return loss.item()
    
    def save(self, path):
        """
        Save the agent's policy network and parameters.
        
        Args:
            path (str): Path to save the model
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        
        torch.save({
            'policy_net_state_dict': self.policy_net.state_dict(),
            'target_net_state_dict': self.target_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'steps': self.steps,
        }, path)
        print(f"Model saved to {path}")
    
    def load(self, path):
        """
        Load a saved agent.
        
        Args:
            path (str): Path to the saved model
        """
        checkpoint = torch.load(path, map_location=self.device)
        self.policy_net.load_state_dict(checkpoint['policy_net_state_dict'])
        self.target_net.load_state_dict(checkpoint['target_net_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        self.steps = checkpoint['steps']
        print(f"Model loaded from {path}")
    
    def get_epsilon(self):
        """Return current epsilon value."""
        return self.epsilon
    
    def set_epsilon(self, epsilon):
        """Set epsilon value."""
        self.epsilon = max(epsilon, self.epsilon_min)
