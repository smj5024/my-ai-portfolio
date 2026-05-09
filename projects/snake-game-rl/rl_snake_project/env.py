"""
Snake Game Environment for Reinforcement Learning

This module implements the Snake game environment compatible with RL algorithms.
It provides the state space, action space, and reward system for training agents.
"""

import numpy as np
import pygame
from enum import Enum
from collections import namedtuple
import random

# Direction enumeration for snake movement
class Direction(Enum):
    RIGHT = 0
    LEFT = 1
    UP = 2
    DOWN = 3

# Named tuple for representing points on the grid
Point = namedtuple('Point', 'x, y')

# RGB color constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
GRAY = (40, 40, 40)


class SnakeGame:
    """
    Snake Game Environment for Reinforcement Learning.
    
    This class implements a grid-based Snake game where an agent controls
    a snake to eat food and grow longer while avoiding collisions.
    
    Attributes:
        width (int): Width of the game grid in pixels
        height (int): Height of the game grid in pixels
        block_size (int): Size of each grid block in pixels
        speed (int): Game speed in milliseconds per frame
    """
    
    def __init__(self, width=640, height=480, block_size=20, speed=100):
        """
        Initialize the Snake game environment.
        
        Args:
            width (int): Game window width in pixels
            height (int): Game window height in pixels
            block_size (int): Size of each grid block (snake/food size)
            speed (int): Game update speed in milliseconds
        """
        self.width = width
        self.height = height
        self.block_size = block_size
        self.speed = speed
        
        # Calculate grid dimensions
        self.grid_width = width // block_size
        self.grid_height = height // block_size
        
        # Maximum steps per episode (prevent infinite games)
        self.max_steps_per_episode = self.grid_width * self.grid_height * 2  # 2x grid size
        
        # Initialize pygame display
        pygame.init()
        self.display = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Snake RL - Enhanced Graphics')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 25)
        
        # Reset game state
        self.reset()
    
    def reset(self):
        """
        Reset the game to initial state.
        
        Returns:
            np.ndarray: Initial state representation
        """
        # Initialize snake in the center of the grid
        center_x = self.grid_width // 2
        center_y = self.grid_height // 2
        
        self.snake = [
            Point(center_x, center_y),
            Point(center_x - 1, center_y),
            Point(center_x - 2, center_y)
        ]
        
        self.direction = Direction.RIGHT
        self.score = 0
        self.food = None  # Single food (back to original)
        self.steps = 0
        self.steps_without_food = 0
        self.max_steps_without_food = self.grid_width * self.grid_height
        self.game_over = False
        
        # Place initial food
        self._place_food()
        
        return self._get_state()
    
    def _place_food(self):
        """Place food at a random location not occupied by the snake."""
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            self.food = Point(x, y)
            if self.food not in self.snake:
                break
    
    def _get_state(self):
        """
        Get the current state representation for the RL agent.
        
        The state includes:
        - Danger detection in straight, right, and left directions
        - Current direction (one-hot encoded)
        - Food position relative to snake head
        
        Returns:
            np.ndarray: State vector of shape (11,)
        """
        head = self.snake[0]
        
        # Calculate points in all directions from head
        point_l = Point(head.x - 1, head.y)
        point_r = Point(head.x + 1, head.y)
        point_u = Point(head.x, head.y - 1)
        point_d = Point(head.x, head.y + 1)
        
        # Current direction one-hot encoding
        dir_l = self.direction == Direction.LEFT
        dir_r = self.direction == Direction.RIGHT
        dir_u = self.direction == Direction.UP
        dir_d = self.direction == Direction.DOWN
        
        # Build state vector
        state = [
            # Danger straight (3 values based on current direction)
            self._is_collision(point_r) if dir_r else
            self._is_collision(point_l) if dir_l else
            self._is_collision(point_u) if dir_u else
            self._is_collision(point_d),
            
            # Danger right (relative to current direction)
            self._is_collision(point_d) if dir_r else
            self._is_collision(point_u) if dir_l else
            self._is_collision(point_l) if dir_u else
            self._is_collision(point_r),
            
            # Danger left (relative to current direction)
            self._is_collision(point_u) if dir_r else
            self._is_collision(point_d) if dir_l else
            self._is_collision(point_r) if dir_u else
            self._is_collision(point_l),
            
            # Current direction (4 values, one-hot)
            dir_l, dir_r, dir_u, dir_d,
            
            # Food location relative to head (4 values)
            self.food.y < head.y if self.food else False,  # Food is up
            self.food.y > head.y if self.food else False,  # Food is down
            self.food.x < head.x if self.food else False,  # Food is left
            self.food.x > head.x if self.food else False   # Food is right
        ]
        
        return np.array(state, dtype=np.float32)
    
    def _is_collision(self, point):
        """
        Check if a point results in collision.
        
        Args:
            point (Point): Point to check for collision
            
        Returns:
            bool: True if collision would occur
        """
        # Check boundary collision
        if (point.x < 0 or point.x >= self.grid_width or
            point.y < 0 or point.y >= self.grid_height):
            return True
        
        # Check self-collision
        if point in self.snake:
            return True
        
        return False
    
    def step(self, action):
        """
        Execute one step in the environment.
        
        Args:
            action (int): Action to take (0=straight, 1=turn right, 2=turn left)
            
        Returns:
            tuple: (state, reward, done, info)
                - state: New state after action
                - reward: Reward received (float)
                - done: Whether episode ended (bool)
                - info: Additional information (dict)
        """
        self.steps += 1
        self.steps_without_food += 1
        
        # Check for starvation (prevent infinite loops)
        if self.steps_without_food >= self.max_steps_without_food:
            print(f"⚠️  Starvation! Steps without food: {self.steps_without_food}")
            self.game_over = True
            return self._get_state(), -10, True, {'score': self.score}
        
        # Check for maximum steps per episode (force end long games)
        if self.steps >= self.max_steps_per_episode:
            print(f"⏰ Max steps reached! Total steps: {self.steps}, Score: {self.score}")
            self.game_over = True
            return self._get_state(), 0, True, {'score': self.score}
        
        # Process user input for rendering
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit("Game closed by user")
        
        # Update direction based on action
        # Action: 0 = continue straight, 1 = turn right, 2 = turn left
        clockwise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        current_idx = clockwise.index(self.direction)
        
        if action == 1:  # Turn right
            self.direction = clockwise[(current_idx + 1) % 4]
        elif action == 2:  # Turn left
            self.direction = clockwise[(current_idx - 1) % 4]
        # action == 0: continue straight
        
        # Move snake
        head = self.snake[0]
        x, y = head.x, head.y
        
        if self.direction == Direction.RIGHT:
            x += 1
        elif self.direction == Direction.LEFT:
            x -= 1
        elif self.direction == Direction.UP:
            y -= 1
        elif self.direction == Direction.DOWN:
            y += 1
        
        new_head = Point(x, y)
        
        # Check for collision
        if self._is_collision(new_head):
            self.game_over = True
            return self._get_state(), -10, True, {'score': self.score}
        
        # Insert new head
        self.snake.insert(0, new_head)
        
        reward = 0
        if new_head == self.food:
            self.score += 1
            self.steps_without_food = 0
            reward = 10
            self._place_food()
        else:
            self.snake.pop()
            reward = -0.1
        
        return self._get_state(), reward, self.game_over, {'score': self.score}
    
    def render(self):
        """Render the game state to the display with enhanced graphics."""
        # Draw gradient background
        for y in range(0, self.height, 2):
            color_value = int(20 + (y / self.height) * 30)
            pygame.draw.line(self.display, (color_value, color_value, color_value + 10), 
                           (0, y), (self.width, y))
        
        # Draw grid lines (subtle)
        for x in range(0, self.width, self.block_size):
            pygame.draw.line(self.display, (30, 30, 40), (x, 0), (x, self.height), 1)
        for y in range(0, self.height, self.block_size):
            pygame.draw.line(self.display, (30, 30, 40), (0, y), (self.width, y), 1)
        
        # Draw snake with gradient and glow effect
        for idx, pt in enumerate(self.snake):
            x = pt.x * self.block_size
            y = pt.y * self.block_size
            
            if idx == 0:
                # Head - bright green with glow
                # Outer glow
                glow_rect = pygame.Rect(x - 2, y - 2, self.block_size + 4, self.block_size + 4)
                pygame.draw.ellipse(self.display, (0, 100, 0, 50), glow_rect, 3)
                
                # Main head
                head_color = (0, 255, 100)
                head_rect = pygame.Rect(x + 1, y + 1, self.block_size - 2, self.block_size - 2)
                pygame.draw.rect(self.display, head_color, head_rect, border_radius=8)
                
                # Eyes
                eye_size = 4
                if self.direction == Direction.RIGHT:
                    eye1_pos = (x + self.block_size - 6, y + 5)
                    eye2_pos = (x + self.block_size - 6, y + self.block_size - 9)
                elif self.direction == Direction.LEFT:
                    eye1_pos = (x + 4, y + 5)
                    eye2_pos = (x + 4, y + self.block_size - 9)
                elif self.direction == Direction.UP:
                    eye1_pos = (x + 5, y + 4)
                    eye2_pos = (x + self.block_size - 9, y + 4)
                else:  # DOWN
                    eye1_pos = (x + 5, y + self.block_size - 8)
                    eye2_pos = (x + self.block_size - 9, y + self.block_size - 8)
                
                pygame.draw.circle(self.display, WHITE, eye1_pos, eye_size)
                pygame.draw.circle(self.display, WHITE, eye2_pos, eye_size)
                pygame.draw.circle(self.display, BLACK, eye1_pos, 2)
                pygame.draw.circle(self.display, BLACK, eye2_pos, 2)
            else:
                # Body - gradient from light to dark green
                progress = idx / len(self.snake)
                green_value = int(200 - progress * 100)
                body_color = (0, green_value, 50)
                
                body_rect = pygame.Rect(x + 2, y + 2, self.block_size - 4, self.block_size - 4)
                pygame.draw.rect(self.display, body_color, body_rect, border_radius=6)
                
                # Highlight
                highlight_rect = pygame.Rect(x + 3, y + 3, self.block_size - 8, self.block_size // 3)
                pygame.draw.rect(self.display, (min(green_value + 50, 255), min(green_value + 50, 255), 100), 
                               highlight_rect, border_radius=3)
        
        # Draw food with beautiful effects (single food)
        if self.food:
            x = self.food.x * self.block_size
            y = self.food.y * self.block_size
            center_x = x + self.block_size // 2
            center_y = y + self.block_size // 2
            
            color = (255, 50, 50)  # Red color
            
            # Pulsing effect
            pulse = int(5 * np.sin(pygame.time.get_ticks() / 200))
            
            # Outer glow
            glow_radius = self.block_size // 2 + 3 + pulse
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*color, 80), (glow_radius, glow_radius), glow_radius)
            self.display.blit(glow_surface, (center_x - glow_radius, center_y - glow_radius))
            
            # Main food circle
            pygame.draw.circle(self.display, color, (center_x, center_y), self.block_size // 2 - 2)
            
            # Inner highlight
            pygame.draw.circle(self.display, (min(color[0] + 50, 255), min(color[1] + 50, 255), min(color[2] + 50, 255)), 
                             (center_x - 2, center_y - 2), self.block_size // 4)
            
            # Shine effect
            pygame.draw.circle(self.display, WHITE, (center_x - 3, center_y - 3), 3)
        
        # Draw score
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        self.display.blit(score_text, [10, 10])
        
        pygame.display.flip()
    
    def close(self):
        """Close the pygame display."""
        pygame.quit()


class SnakeGameNoRender:
    """
    Snake Game Environment without visual rendering.
    
    This is a faster version for training without pygame visualization.
    Uses the same logic but without graphical display.
    """
    
    def __init__(self, width=640, height=480, block_size=20, speed=100):
        """
        Initialize the Snake game environment without rendering.
        
        Args:
            width (int): Game grid width in pixels (used for grid calculation)
            height (int): Game grid height in pixels (used for grid calculation)
            block_size (int): Size of each grid block
            speed (int): Ignored in no-render version
        """
        self.width = width
        self.height = height
        self.block_size = block_size
        self.speed = speed
        
        # Calculate grid dimensions
        self.grid_width = width // block_size
        self.grid_height = height // block_size
        
        # Maximum steps per episode (prevent infinite games)
        self.max_steps_per_episode = self.grid_width * self.grid_height * 2  # 2x grid size
        
        # Reset game state
        self.reset()
    
    def reset(self):
        """
        Reset the game to initial state.
        
        Returns:
            np.ndarray: Initial state representation
        """
        # Initialize snake in the center of the grid
        center_x = self.grid_width // 2
        center_y = self.grid_height // 2
        
        self.snake = [
            Point(center_x, center_y),
            Point(center_x - 1, center_y),
            Point(center_x - 2, center_y)
        ]
        
        self.direction = Direction.RIGHT
        self.score = 0
        self.food = None
        self.steps = 0
        self.steps_without_food = 0
        self.max_steps_without_food = self.grid_width * self.grid_height
        self.game_over = False
        
        # Place initial food
        self._place_food()
        
        return self._get_state()
    
    def _place_food(self):
        """Place a single food item at a random location not occupied by the snake."""
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            self.food = Point(x, y)
            if self.food not in self.snake:
                break
    
    def _get_state(self):
        """
        Get the current state representation for the RL agent.
        
        Returns:
            np.ndarray: State vector of shape (11,)
        """
        head = self.snake[0]
        
        point_l = Point(head.x - 1, head.y)
        point_r = Point(head.x + 1, head.y)
        point_u = Point(head.x, head.y - 1)
        point_d = Point(head.x, head.y + 1)
        
        dir_l = self.direction == Direction.LEFT
        dir_r = self.direction == Direction.RIGHT
        dir_u = self.direction == Direction.UP
        dir_d = self.direction == Direction.DOWN
        
        state = [
            # Danger straight
            self._is_collision(point_r) if dir_r else
            self._is_collision(point_l) if dir_l else
            self._is_collision(point_u) if dir_u else
            self._is_collision(point_d),
            
            # Danger right
            self._is_collision(point_d) if dir_r else
            self._is_collision(point_u) if dir_l else
            self._is_collision(point_l) if dir_u else
            self._is_collision(point_r),
            
            # Danger left
            self._is_collision(point_u) if dir_r else
            self._is_collision(point_d) if dir_l else
            self._is_collision(point_r) if dir_u else
            self._is_collision(point_l),
            
            # Current direction
            dir_l, dir_r, dir_u, dir_d,
            
            # Food location
            self.food.y < head.y if self.food else False,
            self.food.y > head.y if self.food else False,
            self.food.x < head.x if self.food else False,
            self.food.x > head.x if self.food else False
        ]
        
        return np.array(state, dtype=np.float32)
    
    def _is_collision(self, point):
        """Check if a point results in collision."""
        if (point.x < 0 or point.x >= self.grid_width or
            point.y < 0 or point.y >= self.grid_height):
            return True
        if point in self.snake:
            return True
        return False
    
    def step(self, action):
        """
        Execute one step in the environment.
        
        Args:
            action (int): Action to take (0=straight, 1=turn right, 2=turn left)
            
        Returns:
            tuple: (state, reward, done, info)
        """
        self.steps += 1
        self.steps_without_food += 1
        
        if self.steps_without_food >= self.max_steps_without_food:
            print(f"⚠️  Starvation! Steps without food: {self.steps_without_food}")
            self.game_over = True
            return self._get_state(), -10, True, {'score': self.score}
        
        # Check for maximum steps per episode (force end long games)
        if self.steps >= self.max_steps_per_episode:
            print(f"⏰ Max steps reached! Total steps: {self.steps}, Score: {self.score}")
            self.game_over = True
            return self._get_state(), 0, True, {'score': self.score}
        
        # Update direction based on action
        clockwise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        current_idx = clockwise.index(self.direction)
        
        if action == 1:
            self.direction = clockwise[(current_idx + 1) % 4]
        elif action == 2:
            self.direction = clockwise[(current_idx - 1) % 4]
        
        # Move snake
        head = self.snake[0]
        x, y = head.x, head.y
        
        if self.direction == Direction.RIGHT:
            x += 1
        elif self.direction == Direction.LEFT:
            x -= 1
        elif self.direction == Direction.UP:
            y -= 1
        elif self.direction == Direction.DOWN:
            y += 1
        
        new_head = Point(x, y)
        
        if self._is_collision(new_head):
            self.game_over = True
            return self._get_state(), -10, True, {'score': self.score}
        
        self.snake.insert(0, new_head)
        
        reward = 0
        if new_head == self.food:
            self.score += 1
            self.steps_without_food = 0
            reward = 10
            self._place_food()
        else:
            self.snake.pop()
            reward = -0.1
        
        return self._get_state(), reward, self.game_over, {'score': self.score}
    
    def render(self):
        """No-op for no-render version."""
        pass
    
    def close(self):
        """No-op for no-render version."""
        pass
