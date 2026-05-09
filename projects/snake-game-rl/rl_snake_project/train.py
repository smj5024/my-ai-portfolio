"""
Training Script for Snake RL Agent

This script trains a DQN agent to play the Snake game using reinforcement learning.
It includes progress tracking, model saving, and training visualization.
"""

import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

from env import SnakeGameNoRender
from agent import DQNAgent


def train(
    num_episodes=1000,
    max_steps_per_episode=10000,
    batch_size=64,
    save_interval=100,
    save_dir='./models',
    render_interval=0,
    device='cpu'
):
    """
    Train the DQN agent on the Snake game.
    
    Args:
        num_episodes (int): Number of training episodes
        max_steps_per_episode (int): Maximum steps per episode (prevents infinite loops)
        batch_size (int): Batch size for training
        save_interval (int): Save model every N episodes
        save_dir (str): Directory to save models
        render_interval (int): Render game every N episodes (0 = never render)
        device (str): Device to run on ('cuda' or 'cpu')
    
    Returns:
        dict: Training statistics including scores and losses
    """
    # Initialize environment and agent
    env = SnakeGameNoRender()
    state_size = env._get_state().shape[0]
    
    agent = DQNAgent(
        state_size=state_size,
        action_size=3,
        batch_size=batch_size,
        device=device
    )
    
    # Training statistics
    scores = []
    avg_scores = []
    losses = []
    avg_losses = []
    
    # For tracking best model
    best_score = 0
    best_score_episode = 0
    
    # Moving average window
    avg_window = 100
    
    print(f"Starting training for {num_episodes} episodes...")
    print(f"Device: {agent.device}")
    print(f"State size: {state_size}, Action size: 3")
    print("-" * 60)
    
    for episode in range(1, num_episodes + 1):
        state = env.reset()
        total_reward = 0
        episode_loss = []
        steps = 0
        
        for step in range(max_steps_per_episode):
            # Select action
            action = agent.select_action(state, training=True)
            
            # Take action in environment
            next_state, reward, done, info = env.step(action)
            
            # Store experience
            agent.remember(state, action, reward, next_state, done)
            
            # Train agent
            loss = agent.train()
            if loss is not None:
                episode_loss.append(loss)
            
            state = next_state
            total_reward += reward
            steps += 1
            
            if done:
                break
        
        # Record statistics
        score = env.score
        scores.append(score)
        
        if episode_loss:
            avg_loss = np.mean(episode_loss)
            losses.append(avg_loss)
        
        # Calculate moving averages
        if len(scores) >= avg_window:
            avg_score = np.mean(scores[-avg_window:])
        else:
            avg_score = np.mean(scores)
        avg_scores.append(avg_score)
        
        if len(losses) >= avg_window:
            avg_loss = np.mean(losses[-avg_window:])
        else:
            avg_loss = np.mean(losses) if losses else 0
        avg_losses.append(avg_loss)
        
        # Track best score
        if score > best_score:
            best_score = score
            best_score_episode = episode
            # Save best model
            agent.save(os.path.join(save_dir, 'best_model.pth'))
        
        # Print progress
        if episode % 10 == 0 or episode == 1:
            print(f"Episode {episode:4d} | Score: {score:3d} | "
                  f"Avg Score ({avg_window}): {avg_score:.2f} | "
                  f"Epsilon: {agent.epsilon:.4f} | "
                  f"Loss: {avg_loss:.4f}" if episode_loss else f"Loss: N/A")
        
        # Save model periodically
        if episode % save_interval == 0:
            agent.save(os.path.join(save_dir, f'model_episode_{episode}.pth'))
        
        # Optional rendering
        if render_interval > 0 and episode % render_interval == 0:
            render_episode(env, agent, episodes=1, delay=50)
    
    env.close()
    
    # Save final model
    agent.save(os.path.join(save_dir, 'final_model.pth'))
    
    # Plot training curves
    plot_training_curves(scores, avg_scores, losses, avg_losses, save_dir)
    
    print("-" * 60)
    print(f"Training completed!")
    print(f"Best score: {best_score} (Episode {best_score_episode})")
    print(f"Final average score ({avg_window} episodes): {avg_scores[-1]:.2f}")
    print(f"Models saved to: {save_dir}")
    
    return {
        'scores': scores,
        'avg_scores': avg_scores,
        'losses': losses,
        'avg_losses': avg_losses,
        'best_score': best_score,
        'best_score_episode': best_score_episode
    }


def render_episode(env, agent, episodes=1, delay=50):
    """
    Render an episode for visualization.
    
    Args:
        env: Game environment with rendering
        agent: Trained agent
        episodes (int): Number of episodes to render
        delay (int): Delay between frames in milliseconds
    """
    from env import SnakeGame
    
    render_env = SnakeGame(speed=delay)
    
    for _ in range(episodes):
        state = render_env.reset()
        done = False
        
        while not done:
            render_env.render()
            action = agent.select_action(state, training=False)
            state, _, done, _ = render_env.step(action)
        
        render_env.reset()
    
    render_env.close()


def plot_training_curves(scores, avg_scores, losses, avg_losses, save_dir):
    """
    Plot training curves for scores and losses.
    
    Args:
        scores (list): Episode scores
        avg_scores (list): Moving average scores
        losses (list): Episode losses
        avg_losses (list): Moving average losses
        save_dir (str): Directory to save plots
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Score plot
    axes[0].plot(scores, alpha=0.3, label='Episode Score', color='blue')
    axes[0].plot(avg_scores, label=f'Moving Avg ({len(scores)//10 if len(scores) >= 100 else 100})', 
                 color='red', linewidth=2)
    axes[0].set_xlabel('Episode')
    axes[0].set_ylabel('Score')
    axes[0].set_title('Training Scores')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Loss plot
    if losses:
        axes[1].plot(losses, alpha=0.3, label='Episode Loss', color='blue')
        axes[1].plot(avg_losses, label=f'Moving Avg ({len(losses)//10 if len(losses) >= 100 else 100})', 
                     color='red', linewidth=2)
        axes[1].set_xlabel('Episode')
        axes[1].set_ylabel('Loss')
        axes[1].set_title('Training Loss')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'training_curves.png'), dpi=150)
    plt.close()
    print(f"Training curves saved to: {os.path.join(save_dir, 'training_curves.png')}")


def main():
    """Main entry point for training."""
    parser = argparse.ArgumentParser(description='Train Snake RL Agent')
    parser.add_argument('--episodes', type=int, default=1000,
                        help='Number of training episodes (default: 1000)')
    parser.add_argument('--batch-size', type=int, default=64,
                        help='Batch size for training (default: 64)')
    parser.add_argument('--save-interval', type=int, default=100,
                        help='Save model every N episodes (default: 100)')
    parser.add_argument('--save-dir', type=str, default='./models',
                        help='Directory to save models (default: ./models)')
    parser.add_argument('--device', type=str, default='cpu',
                        help='Device to run on: cuda or cpu (default: cpu)')
    parser.add_argument('--render-interval', type=int, default=0,
                        help='Render game every N episodes, 0 to disable (default: 0)')
    
    args = parser.parse_args()
    
    # Create save directory
    os.makedirs(args.save_dir, exist_ok=True)
    
    # Start training
    stats = train(
        num_episodes=args.episodes,
        batch_size=args.batch_size,
        save_interval=args.save_interval,
        save_dir=args.save_dir,
        render_interval=args.render_interval,
        device=args.device
    )
    
    return stats


if __name__ == '__main__':
    main()
