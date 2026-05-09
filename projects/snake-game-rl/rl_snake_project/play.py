"""
Play/Inference Script for Snake RL Agent

This script allows you to:
1. Watch a trained agent play Snake
2. Play the game manually
3. Compare agent vs human performance
4. Watch via web browser (for VSCode remote environments)
"""

import argparse
import pygame
import sys
from env import SnakeGame, Direction, Point
from agent import DQNAgent


def watch_agent(model_path, speed=50):
    """
    Watch a trained agent play Snake.
    
    Args:
        model_path (str): Path to the trained model
        speed (int): Game speed in milliseconds per frame
    """
    # Initialize environment with rendering
    env = SnakeGame(speed=speed)
    
    # Get state size from environment
    state_size = env._get_state().shape[0]
    
    # Initialize agent and load model
    agent = DQNAgent(state_size=state_size, action_size=3)
    agent.load(model_path)
    
    # Set epsilon to 0 for pure exploitation (no random actions)
    agent.set_epsilon(0)
    
    print("Watching trained agent play...")
    print("Press ESC or close window to exit")
    
    total_games = 0
    total_score = 0
    best_score = 0
    
    while True:
        state = env.reset()
        done = False
        episode_score = 0
        
        while not done:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    env.close()
                    print(f"\nStatistics:")
                    print(f"Games watched: {total_games}")
                    print(f"Average score: {total_score / total_games:.2f}")
                    print(f"Best score: {best_score}")
                    return
            
            # Render
            env.render()
            
            # Agent selects action
            action = agent.select_action(state, training=False)
            
            # Take action
            state, reward, done, info = env.step(action)
            episode_score = info['score']
        
        total_games += 1
        total_score += episode_score
        
        if episode_score > best_score:
            best_score = episode_score
            print(f"New best score: {best_score}")
        
        print(f"Game {total_games}: Score = {episode_score}, "
              f"Avg = {total_score/total_games:.2f}, Best = {best_score})


def play_human(speed=100):
    """
    Play Snake manually using keyboard controls.
    
    Controls:
        Arrow keys or WASD to change direction
        ESC to quit
        R to restart
    
    Args:
        speed (int): Game speed in milliseconds per frame
    """
    env = SnakeGame(speed=speed)
    
    print("Playing Snake manually!")
    print("Controls: Arrow keys or WASD to move, ESC to quit, R to restart")
    
    running = True
    
    while running:
        state = env.reset()
        done = False
        
        while not done:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    done = True
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        done = True
                    
                    elif event.key == pygame.K_r:
                        done = True  # Restart
                    
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        if env.direction != Direction.DOWN:
                            env.direction = Direction.UP
                    
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        if env.direction != Direction.UP:
                            env.direction = Direction.DOWN
                    
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        if env.direction != Direction.RIGHT:
                            env.direction = Direction.LEFT
                    
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        if env.direction != Direction.LEFT:
                            env.direction = Direction.RIGHT
            
            # Render
            env.render()
            
            # Move snake automatically based on current direction
            head = env.snake[0]
            x, y = head.x, head.y
            
            if env.direction == Direction.RIGHT:
                x += 1
            elif env.direction == Direction.LEFT:
                x -= 1
            elif env.direction == Direction.UP:
                y -= 1
            elif env.direction == Direction.DOWN:
                y += 1
            
            new_head = Point(x, y)
            
            if env._is_collision(new_head):
                done = True
            else:
                env.snake.insert(0, new_head)
                
                if new_head == env.food:
                    env.score += 1
                    env._place_food()
                else:
                    env.snake.pop()
        
        if running:
            print(f"Game Over! Score: {env.score}")
    
    env.close()
    print("Thanks for playing!")


def compare(model_path, speed=50):
    """
    Compare agent performance with manual play.
    
    Args:
        model_path (str): Path to the trained model
        speed (int): Game speed in milliseconds per frame
    """
    print("=" * 60)
    print("COMPARISON MODE")
    print("=" * 60)
    
    # First, watch the agent
    print("\n>>> Watching AI Agent (3 games)")
    print("-" * 40)
    watch_agent_n_stats(model_path, speed, num_games=3)
    
    input("\nPress Enter to start playing manually...")
    
    # Then, play manually
    print("\n>>> Your Turn! Play 3 games")
    print("-" * 40)
    play_human_n_games(speed, num_games=3)


def watch_agent_n_stats(model_path, speed, num_games=3):
    """Watch agent play N games and show statistics."""
    env = SnakeGame(speed=speed)
    state_size = env._get_state().shape[0]
    agent = DQNAgent(state_size=state_size, action_size=3)
    agent.load(model_path)
    agent.set_epsilon(0)
    
    scores = []
    
    for game in range(num_games):
        state = env.reset()
        done = False
        
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    env.close()
                    return
            env.render()
            action = agent.select_action(state, training=False)
            state, _, done, info = env.step(action)
        
        scores.append(info['score'])
        print(f"Game {game + 1}: Score = {info['score']}")
    
    env.close()
    print(f"\nAgent Statistics:")
    print(f"  Average: {sum(scores)/len(scores):.2f}")
    print(f"  Best: {max(scores)}")
    print(f"  Total: {sum(scores)}")


def play_human_n_games(speed, num_games=3):
    """Play N games manually and show statistics."""
    env = SnakeGame(speed=speed)
    
    scores = []
    
    for game in range(num_games):
        state = env.reset()
        done = False
        
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    env.close()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        env.close()
                        return
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        if env.direction != Direction.DOWN:
                            env.direction = Direction.UP
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        if env.direction != Direction.UP:
                            env.direction = Direction.DOWN
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        if env.direction != Direction.RIGHT:
                            env.direction = Direction.LEFT
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        if env.direction != Direction.LEFT:
                            env.direction = Direction.RIGHT
            
            env.render()
            
            head = env.snake[0]
            x, y = head.x, head.y
            
            if env.direction == Direction.RIGHT:
                x += 1
            elif env.direction == Direction.LEFT:
                x -= 1
            elif env.direction == Direction.UP:
                y -= 1
            elif env.direction == Direction.DOWN:
                y += 1
            
            new_head = Point(x, y)
            
            if env._is_collision(new_head):
                done = True
            else:
                env.snake.insert(0, new_head)
                if new_head == env.food:
                    env.score += 1
                    env._place_food()
                else:
                    env.snake.pop()
        
        scores.append(env.score)
        print(f"Game {game + 1}: Score = {env.score}")
    
    env.close()
    print(f"\nYour Statistics:")
    print(f"  Average: {sum(scores)/len(scores):.2f}")
    print(f"  Best: {max(scores)}")
    print(f"  Total: {sum(scores)}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Play Snake RL Game')
    parser.add_argument('--mode', type=str, default='watch',
                        choices=['watch', 'play', 'compare'],
                        help='Mode: watch (AI), play (human), or compare')
    parser.add_argument('--model', type=str, default='./models/best_model.pth',
                        help='Path to trained model (default: ./models/best_model.pth)')
    parser.add_argument('--speed', type=int, default=50,
                        help='Game speed in ms (lower = faster, default: 50)')
    
    args = parser.parse_args()
    
    if args.mode == 'watch':
        watch_agent(args.model, args.speed)
    elif args.mode == 'play':
        play_human(args.speed)
    elif args.mode == 'compare':
        compare(args.model, args.speed)


if __name__ == '__main__':
    main()
