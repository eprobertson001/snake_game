#!/usr/bin/env python3
"""
Classic Snake Game
A Python implementation of the classic Snake game using pygame.
"""

import pygame
import random
import sys
from enum import Enum
from typing import List, Tuple

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 650  # Increased height to accommodate header
HEADER_HEIGHT = 50   # Height of the header area
GAME_AREA_Y = HEADER_HEIGHT  # Y offset for game area
GAME_HEIGHT = WINDOW_HEIGHT - HEADER_HEIGHT  # Actual game area height
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = GAME_HEIGHT // GRID_SIZE

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 180, 0)
LIGHT_GREEN = (50, 205, 50)
SNAKE_OUTLINE = (0, 100, 0)
RED = (255, 0, 0)
DARK_RED = (139, 0, 0)
APPLE_GREEN = (34, 139, 34)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)

# Game settings
INITIAL_SPEED = 10
SPEED_INCREMENT = 0.5
MAX_SPEED = 20
FRAME_WIDTH = 3
APPLES_PER_LEVEL = 10
PORTAL_WIDTH = GRID_SIZE*2  # Same width as an apple

class Direction(Enum):
    """Enumeration for snake movement directions."""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class GameState(Enum):
    """Enumeration for different game states."""
    SCREENSAVER = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    LEVEL_TRANSITION = 5
    LEVEL_PREVIEW = 6

class Snake:
    """Snake class to handle snake logic and rendering."""
    
    def __init__(self):
        """Initialize the snake at the center of the screen."""
        self.reset()
    
    def reset(self):
        """Reset snake to initial state."""
        center_x = GRID_WIDTH // 2
        bottom_y = GRID_HEIGHT - 1  # Start at bottom
        self.body = [(center_x, bottom_y), (center_x, bottom_y + 1), (center_x, bottom_y + 2)]
        self.direction = Direction.UP  # Travel north
        self.grow_pending = 0
    
    def move(self):
        """Move the snake in the current direction."""
        head_x, head_y = self.body[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        
        self.body.insert(0, new_head)
        
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()
    
    def change_direction(self, new_direction: Direction):
        """Change snake direction if it's not opposite to current direction."""
        current_dx, current_dy = self.direction.value
        new_dx, new_dy = new_direction.value
        
        # Prevent moving in opposite direction
        if (current_dx, current_dy) != (-new_dx, -new_dy):
            self.direction = new_direction
    
    def grow(self):
        """Make the snake grow by one segment."""
        self.grow_pending += 1
    
    def check_wall_collision(self) -> bool:
        """Check if snake has hit the walls (accounting for frame)."""
        head_x, head_y = self.body[0]
        return head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT
    
    def check_self_collision(self) -> bool:
        """Check if snake has hit itself."""
        head = self.body[0]
        return head in self.body[1:]
    
    def draw(self, screen):
        """Draw the snake on the screen with smooth, rounded segments and texture."""
        if len(self.body) == 0:
            return
            
        # Draw snake body segments as continuous rounded rectangles
        for i, (x, y) in enumerate(self.body):
            # Only draw segments that are within the game area (not in header or beyond)
            if y < 0 or y >= GRID_HEIGHT:
                continue
                
            center_x = x * GRID_SIZE + GRID_SIZE // 2 + FRAME_WIDTH
            center_y = y * GRID_SIZE + GRID_SIZE // 2 + FRAME_WIDTH + GAME_AREA_Y
            
            if i == 0:  # Head
                # Draw head as a circle with gradient effect
                pygame.draw.circle(screen, GREEN, (center_x, center_y), GRID_SIZE // 2)
                pygame.draw.circle(screen, LIGHT_GREEN, (center_x, center_y), GRID_SIZE // 2 - 2)
                pygame.draw.circle(screen, SNAKE_OUTLINE, (center_x, center_y), GRID_SIZE // 2, 2)
                
                # Draw eyes
                eye_offset = GRID_SIZE // 4
                pygame.draw.circle(screen, BLACK, (center_x - eye_offset//2, center_y - eye_offset//2), 2)
                pygame.draw.circle(screen, BLACK, (center_x + eye_offset//2, center_y - eye_offset//2), 2)
            else:  # Body
                # Draw body segment as rounded rectangle
                segment_rect = pygame.Rect(x * GRID_SIZE + 2 + FRAME_WIDTH, y * GRID_SIZE + 2 + FRAME_WIDTH + GAME_AREA_Y, 
                                         GRID_SIZE - 4, GRID_SIZE - 4)
                
                # Main body color
                pygame.draw.rect(screen, DARK_GREEN, segment_rect, border_radius=6)
                
                # Add texture with lighter inner rectangle
                inner_rect = pygame.Rect(x * GRID_SIZE + 4 + FRAME_WIDTH, y * GRID_SIZE + 4 + FRAME_WIDTH + GAME_AREA_Y, 
                                       GRID_SIZE - 8, GRID_SIZE - 8)
                pygame.draw.rect(screen, LIGHT_GREEN, inner_rect, border_radius=4)
                
                # Add outline
                pygame.draw.rect(screen, SNAKE_OUTLINE, segment_rect, 2, border_radius=6)
        
        # Draw connections between segments to make it look continuous
        for i in range(len(self.body) - 1):
            x1, y1 = self.body[i]
            x2, y2 = self.body[i + 1]
            
            # Only draw connections if both segments are visible in game area
            if (y1 < 0 or y1 >= GRID_HEIGHT) or (y2 < 0 or y2 >= GRID_HEIGHT):
                continue
            
            center_x1 = x1 * GRID_SIZE + GRID_SIZE // 2 + FRAME_WIDTH
            center_y1 = y1 * GRID_SIZE + GRID_SIZE // 2 + FRAME_WIDTH + GAME_AREA_Y
            center_x2 = x2 * GRID_SIZE + GRID_SIZE // 2 + FRAME_WIDTH
            center_y2 = y2 * GRID_SIZE + GRID_SIZE // 2 + FRAME_WIDTH + GAME_AREA_Y
            
            # Draw thick line between segments
            pygame.draw.line(screen, DARK_GREEN, (center_x1, center_y1), (center_x2, center_y2), GRID_SIZE - 4)
            pygame.draw.line(screen, LIGHT_GREEN, (center_x1, center_y1), (center_x2, center_y2), GRID_SIZE - 8)

class Food:
    """Food class to handle food logic and rendering."""
    
    def __init__(self):
        """Initialize food at a random position."""
        self.position = self.generate_position()
    
    def generate_position(self) -> Tuple[int, int]:
        """Generate a random position for the food."""
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        return (x, y)
    
    def respawn(self, snake_body: List[Tuple[int, int]]):
        """Respawn food at a position not occupied by the snake."""
        while True:
            self.position = self.generate_position()
            if self.position not in snake_body:
                break
    
    def draw(self, screen):
        """Draw the food as an apple on the screen."""
        x, y = self.position
        center_x = x * GRID_SIZE + GRID_SIZE // 2 + FRAME_WIDTH
        center_y = y * GRID_SIZE + GRID_SIZE // 2 + FRAME_WIDTH + GAME_AREA_Y
        
        # Draw apple body (main red circle)
        apple_radius = GRID_SIZE // 2 - 2
        pygame.draw.circle(screen, RED, (center_x, center_y), apple_radius)
        
        # Add highlight to make it look more 3D
        highlight_offset = apple_radius // 3
        pygame.draw.circle(screen, (255, 100, 100), 
                         (center_x - highlight_offset, center_y - highlight_offset), 
                         apple_radius // 2)
        
        # Add shadow/depth
        pygame.draw.circle(screen, DARK_RED, (center_x, center_y), apple_radius, 2)
        
        # Draw apple stem (small brown rectangle)
        stem_width = 3
        stem_height = 6
        stem_rect = pygame.Rect(center_x - stem_width//2, center_y - apple_radius - 2, 
                               stem_width, stem_height)
        pygame.draw.rect(screen, (101, 67, 33), stem_rect)  # Brown color
        
        # Draw small leaf
        leaf_points = [
            (center_x + 2, center_y - apple_radius),
            (center_x + 6, center_y - apple_radius - 3),
            (center_x + 4, center_y - apple_radius + 1)
        ]
        pygame.draw.polygon(screen, APPLE_GREEN, leaf_points)

class Obstacle:
    """Obstacle class to handle level obstacles."""
    
    def __init__(self, positions: List[Tuple[int, int]]):
        """Initialize obstacle with list of grid positions."""
        self.positions = positions
    
    def draw(self, screen):
        """Draw obstacle blocks on the screen."""
        for x, y in self.positions:
            rect = pygame.Rect(x * GRID_SIZE + FRAME_WIDTH, y * GRID_SIZE + FRAME_WIDTH + GAME_AREA_Y, 
                             GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, BLUE, rect)
            pygame.draw.rect(screen, BLUE, rect, 1)
    
    def check_collision(self, position: Tuple[int, int]) -> bool:
        """Check if position collides with any obstacle."""
        return position in self.positions

class LevelManager:
    """Manages game levels and obstacles."""
    
    def __init__(self):
        """Initialize level manager."""
        self.current_level = 1
        self.obstacles = []
        self.generate_obstacles()
    
    def is_in_snake_start_path(self, x: int, y: int) -> bool:
        """Check if position is in the snake's initial path (5 grid squares from start)."""
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT - 1
        
        # Check if position is in the snake's initial northward path
        # Keep 5 grid squares clear in front of snake's starting direction
        if x == start_x and start_y - 5 <= y <= start_y:
            return True
        return False
    
    def generate_obstacles(self):
        """Generate obstacles for current level."""
        self.obstacles = []
        
        if self.current_level == 1:
            # No obstacles in level 1
            pass
        elif self.current_level == 2:
            # Simple horizontal line in middle, but avoid snake start path
            obstacles = []
            for x in range(GRID_WIDTH // 3, 2 * GRID_WIDTH // 3):
                y = GRID_HEIGHT // 2
                if not self.is_in_snake_start_path(x, y):
                    obstacles.append((x, y))
            if obstacles:
                self.obstacles.append(Obstacle(obstacles))
        elif self.current_level == 3:
            # Vertical lines on sides, avoid snake start path
            obstacles = []
            for y in range(5, GRID_HEIGHT - 5):
                if not self.is_in_snake_start_path(5, y):
                    obstacles.append((5, y))
                if not self.is_in_snake_start_path(GRID_WIDTH - 6, y):
                    obstacles.append((GRID_WIDTH - 6, y))
            if obstacles:
                self.obstacles.append(Obstacle(obstacles))
        elif self.current_level == 4:
            # Cross pattern, avoid snake start path
            obstacles = []
            # Horizontal line
            for x in range(8, GRID_WIDTH - 8):
                y = GRID_HEIGHT // 2
                if not self.is_in_snake_start_path(x, y):
                    obstacles.append((x, y))
            # Vertical line
            for y in range(8, GRID_HEIGHT - 8):
                x = GRID_WIDTH // 2
                if not self.is_in_snake_start_path(x, y):
                    obstacles.append((x, y))
            if obstacles:
                self.obstacles.append(Obstacle(obstacles))
        elif self.current_level == 5:
            # Maze-like pattern, avoid snake start path
            obstacles = []
            # Top and bottom barriers with gaps, avoid snake start path
            for x in range(5, 15):
                if not self.is_in_snake_start_path(x, 8):
                    obstacles.append((x, 8))
            for x in range(20, 30):
                if not self.is_in_snake_start_path(x, 8):
                    obstacles.append((x, 8))
            for x in range(10, 20):
                if not self.is_in_snake_start_path(x, GRID_HEIGHT - 9):
                    obstacles.append((x, GRID_HEIGHT - 9))
            for x in range(25, 35):
                if not self.is_in_snake_start_path(x, GRID_HEIGHT - 9):
                    obstacles.append((x, GRID_HEIGHT - 9))
            # Side barriers, avoid snake start path
            for y in range(12, 18):
                if not self.is_in_snake_start_path(8, y):
                    obstacles.append((8, y))
                if not self.is_in_snake_start_path(GRID_WIDTH - 9, y):
                    obstacles.append((GRID_WIDTH - 9, y))
            if obstacles:
                self.obstacles.append(Obstacle(obstacles))
        else:
            # Advanced levels - always have obstacles with increasing complexity
            obstacles = []
            level_complexity = max(2, min(self.current_level - 3, 15))  # Ensure at least 2 clusters, max 15
            
            # Create multiple random obstacle clusters
            for cluster in range(level_complexity):
                center_x = random.randint(8, GRID_WIDTH - 8)
                center_y = random.randint(8, GRID_HEIGHT - 8)
                cluster_size = random.randint(3, 7)  # Slightly larger clusters for higher levels
                
                for i in range(cluster_size):
                    for j in range(cluster_size):
                        if random.random() < 0.7:  # 70% chance for each block (increased density)
                            x, y = center_x + i - cluster_size//2, center_y + j - cluster_size//2
                            if (3 < x < GRID_WIDTH - 3 and 3 < y < GRID_HEIGHT - 3 and
                                not self.is_in_snake_start_path(x, y)):
                                obstacles.append((x, y))
            
            # Add some guaranteed linear obstacles for higher levels
            if self.current_level >= 8:
                # Add random horizontal and vertical lines, avoid snake start path
                for _ in range(self.current_level // 4):
                    if random.choice([True, False]):  # Horizontal line
                        y_pos = random.randint(5, GRID_HEIGHT - 6)
                        x_start = random.randint(5, GRID_WIDTH // 3)
                        x_end = random.randint(2 * GRID_WIDTH // 3, GRID_WIDTH - 5)
                        for x in range(x_start, x_end):
                            if not self.is_in_snake_start_path(x, y_pos):
                                obstacles.append((x, y_pos))
                    else:  # Vertical line
                        x_pos = random.randint(5, GRID_WIDTH - 6)
                        y_start = random.randint(5, GRID_HEIGHT // 3)
                        y_end = random.randint(2 * GRID_HEIGHT // 3, GRID_HEIGHT - 5)
                        for y in range(y_start, y_end):
                            if not self.is_in_snake_start_path(x_pos, y):
                                obstacles.append((x_pos, y))
            
            if obstacles:  # Only create obstacle if we have positions
                self.obstacles.append(Obstacle(obstacles))
    
    def next_level(self):
        """Advance to next level."""
        self.current_level += 1
        self.generate_obstacles()
    
    def check_collision(self, position: Tuple[int, int]) -> bool:
        """Check if position collides with any obstacle in current level."""
        for obstacle in self.obstacles:
            if obstacle.check_collision(position):
                return True
        return False
    
    def draw(self, screen):
        """Draw all obstacles for current level."""
        for obstacle in self.obstacles:
            obstacle.draw(screen)

class Game:
    """Main game class to handle game logic and rendering."""
    
    def __init__(self):
        """Initialize the game."""
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
        self.reset_game()
        self.state = GameState.SCREENSAVER  # Set initial state after reset
    
    def reset_game(self):
        """Reset the game to initial state."""
        self.snake = Snake()
        self.food = Food()
        self.level_manager = LevelManager()
        self.score = 0
        self.apples_eaten = 0
        self.speed = INITIAL_SPEED
        self.portal_open = False
        self.transition_timer = 0
        self.preview_timer = 0  # Timer for level preview countdown
        
        # Screensaver properties - reset these too
        self.auto_direction_timer = 0
        self.auto_direction_change_interval = 60  # Change direction every 1 second at 60 FPS
        
        # Ensure food doesn't spawn on snake or obstacles
        self.respawn_food_safely()
    
    def respawn_food_safely(self):
        """Respawn food in a safe location away from snake and obstacles."""
        while True:
            self.food.position = self.food.generate_position()
            if (self.food.position not in self.snake.body and 
                not self.level_manager.check_collision(self.food.position)):
                break
    
    def reset_snake_safely(self):
        """Reset snake to a safe position that doesn't conflict with obstacles."""
        # Start at bottom center, traveling north
        center_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT - 1  # Bottom of game area
        
        # Check if the initial bottom-center position is safe
        initial_positions = [
            (center_x, start_y),      # Head
            (center_x, start_y + 1),  # Body (will be outside game area initially)
            (center_x, start_y + 2)   # Tail (will be outside game area initially)
        ]
        
        # Check if head position is clear of obstacles
        if not self.level_manager.check_collision((center_x, start_y)):
            # Position is safe, use it
            self.snake.body = initial_positions
            self.snake.direction = Direction.UP
            self.snake.grow_pending = 0
            print(f"Snake reset to bottom center position ({center_x}, {start_y}) for level {self.level_manager.current_level}")
            return
        
        # If bottom center is blocked, try positions near the bottom
        safe_positions = []
        
        # Try positions in the bottom few rows
        for y in range(GRID_HEIGHT - 1, max(GRID_HEIGHT - 5, 0), -1):
            for x_offset in range(-5, 6):  # Try positions around center
                x = center_x + x_offset
                if (0 <= x < GRID_WIDTH and 
                    not self.level_manager.check_collision((x, y))):
                    safe_positions.append((x, y))
        
        if safe_positions:
            # Use the first safe position found (closest to bottom center)
            start_x, start_y = safe_positions[0]
            self.snake.body = [
                (start_x, start_y), 
                (start_x, start_y + 1), 
                (start_x, start_y + 2)
            ]
            self.snake.direction = Direction.UP
            self.snake.grow_pending = 0
            print(f"Snake safely reset to position ({start_x}, {start_y}) for level {self.level_manager.current_level}")
        else:
            # Fallback: use default reset but change direction to UP
            print(f"Warning: No safe position found for level {self.level_manager.current_level}, using default")
            self.snake.reset()
    
    def handle_input(self):
        """Handle keyboard and mouse input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == GameState.SCREENSAVER:
                    # Check if "New Game" button was clicked
                    mouse_x, mouse_y = event.pos
                    button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, GAME_AREA_Y + GAME_HEIGHT // 2 - 25, 200, 50)
                    if button_rect.collidepoint(mouse_x, mouse_y):
                        self.reset_game()
                        self.state = GameState.PLAYING
                
                elif self.state == GameState.LEVEL_TRANSITION:
                    # Check if "Continue" button was clicked
                    mouse_x, mouse_y = event.pos
                    button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 40, 200, 50)
                    if button_rect.collidepoint(mouse_x, mouse_y):
                        # Start level preview
                        self.state = GameState.LEVEL_PREVIEW
                        self.preview_timer = 0
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.SCREENSAVER:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                        self.state = GameState.PLAYING
                
                elif self.state == GameState.PLAYING:
                    # Movement controls
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        self.snake.change_direction(Direction.UP)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.snake.change_direction(Direction.DOWN)
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:
                        self.snake.change_direction(Direction.LEFT)
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        self.snake.change_direction(Direction.RIGHT)
                    elif event.key == pygame.K_SPACE:
                        self.state = GameState.PAUSED
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.PLAYING
                
                elif self.state == GameState.LEVEL_TRANSITION:
                    if event.key == pygame.K_RETURN:
                        # Start level preview
                        self.state = GameState.LEVEL_PREVIEW
                        self.preview_timer = 0
                
                elif self.state == GameState.LEVEL_PREVIEW:
                    # Skip preview countdown if user presses any key
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.PLAYING
                        self.preview_timer = 0
                
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_m:
                        self.reset_game()
                        self.state = GameState.SCREENSAVER
                
                # Global controls
                if event.key == pygame.K_ESCAPE:
                    return False
        
        return True
    
    def check_portal_collision(self) -> bool:
        """Check if snake head is at the portal opening."""
        if not self.portal_open:
            return False
        
        head_x, head_y = self.snake.body[0]
        portal_center = GRID_WIDTH // 2
        portal_left = portal_center - (PORTAL_WIDTH // (2 * GRID_SIZE))
        portal_right = portal_center + (PORTAL_WIDTH // (2 * GRID_SIZE))
        
        return head_y <= -1 and portal_left <= head_x <= portal_right
    
    def snake_fully_through_portal(self) -> bool:
        """Check if entire snake has passed through the portal."""
        if not self.portal_open:
            return False
        
        if len(self.snake.body) == 0:
            return False
        
        # Portal area is in the center of the screen
        portal_center = GRID_WIDTH // 2
        portal_width_in_grids = 3  # Make portal 3 grid units wide (more generous)
        portal_left = portal_center - portal_width_in_grids // 2
        portal_right = portal_center + portal_width_in_grids // 2
        
        # Check if all snake segments are above the visible play area (y < 0)
        all_segments_through = all(y < 0 for x, y in self.snake.body)
        
        # At least one segment should have been in the portal area
        any_segment_in_portal = any(portal_left <= x <= portal_right for x, y in self.snake.body)
        
        return all_segments_through and any_segment_in_portal
    
    def update(self):
        """Update game logic."""
        if self.state == GameState.SCREENSAVER:
            # Auto-pilot the snake for screensaver
            self.auto_direction_timer += 1
            
            # Move snake
            self.snake.move()
            
            # Check if snake needs to turn to avoid walls or obstacles
            head_x, head_y = self.snake.body[0]
            current_direction = self.snake.direction
            
            # Look ahead to see if we need to turn
            dx, dy = current_direction.value
            next_x, next_y = head_x + dx, head_y + dy
            
            # Check if next position would cause collision
            will_hit_wall = (next_x < 0 or next_x >= GRID_WIDTH or 
                           next_y < 0 or next_y >= GRID_HEIGHT)
            will_hit_self = (next_x, next_y) in self.snake.body
            will_hit_obstacle = self.level_manager.check_collision((next_x, next_y))
            
            if (will_hit_wall or will_hit_self or will_hit_obstacle or 
                self.auto_direction_timer >= self.auto_direction_change_interval):
                # Find a safe direction
                safe_directions = []
                for direction in Direction:
                    test_dx, test_dy = direction.value
                    test_x, test_y = head_x + test_dx, head_y + test_dy
                    
                    # Don't go backwards
                    if direction.value == (-dx, -dy):
                        continue
                    
                    # Check if this direction is safe
                    if (0 <= test_x < GRID_WIDTH and 0 <= test_y < GRID_HEIGHT and
                        (test_x, test_y) not in self.snake.body and
                        not self.level_manager.check_collision((test_x, test_y))):
                        safe_directions.append(direction)
                
                if safe_directions:
                    self.snake.direction = random.choice(safe_directions)
                    self.auto_direction_timer = 0
            
            # Check food collision
            if self.snake.body[0] == self.food.position:
                self.snake.grow()
                self.respawn_food_safely()
            
            # If snake gets too long, reset it
            if len(self.snake.body) > 100:
                self.snake.reset()
            
            return
        
        if self.state == GameState.LEVEL_TRANSITION:
            # Stay in transition state until user clicks Continue or presses Enter
            return
        
        if self.state == GameState.LEVEL_PREVIEW:
            self.preview_timer += 1
            if self.preview_timer > 180:  # 3 seconds at 60 FPS
                # Start the new level
                self.state = GameState.PLAYING
                self.preview_timer = 0
            return
        
        if self.state != GameState.PLAYING:
            return
        
        # Check if portal should open
        if self.apples_eaten >= APPLES_PER_LEVEL and not self.portal_open:
            self.portal_open = True
        
        # Move snake
        self.snake.move()
        
        # Check if snake has fully exited through portal first (before other collision checks)
        if self.portal_open and self.snake_fully_through_portal():
            # Prepare for next level
            self.level_manager.next_level()
            self.portal_open = False
            self.apples_eaten = 0
            self.speed = INITIAL_SPEED  # Reset speed for each level
            
            # Reset snake to a safe starting position for new level
            self.reset_snake_safely()
            self.respawn_food_safely()
            
            # Transition to level complete screen
            self.state = GameState.LEVEL_TRANSITION
            self.transition_timer = 0
            return
        
        # Check food collision
        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.score += 10
            self.apples_eaten += 1
            self.respawn_food_safely()
            
            # Increase speed slightly
            self.speed = min(MAX_SPEED, self.speed + SPEED_INCREMENT)
        
        # Check collisions (walls, self, obstacles)
        head_x, head_y = self.snake.body[0]
        
        # Check wall collision (but allow portal exit)
        if self.portal_open:
            # Allow movement through portal area
            portal_center = GRID_WIDTH // 2
            portal_width_in_grids = 3  # Same as in snake_fully_through_portal
            portal_left = portal_center - portal_width_in_grids // 2
            portal_right = portal_center + portal_width_in_grids // 2
            
            # If snake head is in portal area or has passed through, allow movement
            if portal_left <= head_x <= portal_right and head_y <= -1:
                pass  # Allow portal movement
            # Also allow if any part of snake is still going through portal
            elif any(portal_left <= x <= portal_right and y < 0 for x, y in self.snake.body):
                pass  # Snake is in process of exiting
            elif self.snake.check_wall_collision():
                self.state = GameState.GAME_OVER
                return
        else:
            # Normal wall collision check
            if self.snake.check_wall_collision():
                self.state = GameState.GAME_OVER
                return
        
        # Check self collision
        if self.snake.check_self_collision():
            self.state = GameState.GAME_OVER
            return
        
        # Check obstacle collision
        if self.level_manager.check_collision(self.snake.body[0]):
            self.state = GameState.GAME_OVER
            return
    
    def draw_text(self, text: str, x: int, y: int, font=None, color=WHITE):
        """Draw text on the screen."""
        if font is None:
            font = self.font
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)
    
    def draw_game(self):
        """Draw the game screen."""
        self.screen.fill(BLACK)
        
        # Draw header area
        header_rect = pygame.Rect(0, 0, WINDOW_WIDTH, HEADER_HEIGHT)
        pygame.draw.rect(self.screen, DARK_GRAY, header_rect)
        pygame.draw.rect(self.screen, LIGHT_GRAY, header_rect, 2)  # Border
        
        # Draw game area background and frame
        game_rect = pygame.Rect(0, GAME_AREA_Y, WINDOW_WIDTH, GAME_HEIGHT)
        pygame.draw.rect(self.screen, BLACK, game_rect)
        pygame.draw.rect(self.screen, BLUE, game_rect, FRAME_WIDTH)
        
        # Draw portal opening if active
        if self.portal_open:
            portal_center = WINDOW_WIDTH // 2
            portal_left = portal_center - PORTAL_WIDTH // 2
            portal_rect = pygame.Rect(portal_left, GAME_AREA_Y, PORTAL_WIDTH, FRAME_WIDTH)
            pygame.draw.rect(self.screen, BLACK, portal_rect)
            # Add glowing effect around portal
            glow_rect = pygame.Rect(portal_left - 5, GAME_AREA_Y, PORTAL_WIDTH + 10, FRAME_WIDTH + 5)
            pygame.draw.rect(self.screen, (100, 200, 255), glow_rect, 2)
        
        # Draw level obstacles
        self.level_manager.draw(self.screen)
        
        # Draw game objects
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        
        # Draw header info with better contrast
        level_text = f"Level: {self.level_manager.current_level}"
        self.draw_text(level_text, 80, HEADER_HEIGHT // 2, color=WHITE)
        
        score_text = f"Score: {self.score}"
        self.draw_text(score_text, WINDOW_WIDTH - 80, HEADER_HEIGHT // 2, color=WHITE)
        
        apples_text = f"Apples: {self.apples_eaten}/{APPLES_PER_LEVEL}"
        self.draw_text(apples_text, WINDOW_WIDTH // 2, HEADER_HEIGHT // 2, color=WHITE)
    
    def draw_paused(self):
        """Draw the pause screen."""
        self.draw_game()  # Draw game behind pause menu
        
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        self.draw_text("PAUSED", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40, self.big_font)
        self.draw_text("Press SPACE to Resume", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)
    
    def draw_game_over(self):
        """Draw the game over screen."""
        self.screen.fill(BLACK)
        
        self.draw_text("GAME OVER", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100, self.big_font, RED)
        self.draw_text(f"Final Score: {self.score}", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40)
        self.draw_text("Press R to Restart", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)
        self.draw_text("Press M for Menu", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60)
        self.draw_text("Press ESC to Quit", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100)
    
    def draw_level_transition(self):
        """Draw the level completion screen with continue button."""
        self.screen.fill(BLACK)
        
        self.draw_text(f"LEVEL {self.level_manager.current_level - 1} COMPLETE!", 
                      WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80, self.big_font, GREEN)
        self.draw_text(f"Level {self.level_manager.current_level} Next...", 
                      WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20)
        
        # Draw "Continue" button
        button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 40, 200, 50)
        
        # Check if mouse is hovering over button
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = button_rect.collidepoint(mouse_pos)
        
        # Button colors
        button_color = (0, 150, 0) if is_hovering else (0, 100, 0)
        border_color = (0, 255, 0) if is_hovering else (0, 200, 0)
        
        # Draw button
        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=10)
        pygame.draw.rect(self.screen, border_color, button_rect, 3, border_radius=10)
        
        # Draw button text
        button_font = pygame.font.Font(None, 48)
        self.draw_text("Continue", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 65, button_font, WHITE)
        
        # Show keyboard shortcut
        self.draw_text("Press ENTER to continue", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 120)

    def draw_level_preview(self):
        """Draw the level preview with countdown."""
        # Draw the game background with new level obstacles
        self.screen.fill(BLACK)
        
        # Draw header area
        header_rect = pygame.Rect(0, 0, WINDOW_WIDTH, HEADER_HEIGHT)
        pygame.draw.rect(self.screen, DARK_GRAY, header_rect)
        pygame.draw.rect(self.screen, LIGHT_GRAY, header_rect, 2)  # Border
        
        # Draw game area background and frame
        game_rect = pygame.Rect(0, GAME_AREA_Y, WINDOW_WIDTH, GAME_HEIGHT)
        pygame.draw.rect(self.screen, BLACK, game_rect)
        pygame.draw.rect(self.screen, BLUE, game_rect, FRAME_WIDTH)
        
        # Draw level obstacles
        self.level_manager.draw(self.screen)
        
        # Draw game objects (snake and food in their new positions)
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        
        # Draw semi-transparent overlay over game area only
        overlay = pygame.Surface((WINDOW_WIDTH, GAME_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, GAME_AREA_Y))
        
        # Draw level info
        self.draw_text(f"LEVEL {self.level_manager.current_level}", 
                      WINDOW_WIDTH // 2, GAME_AREA_Y + GAME_HEIGHT // 2 - 60, self.big_font, GREEN)
        
        # Show countdown
        countdown = 3 - (self.preview_timer // 60)
        if countdown > 0:
            self.draw_text(f"Starting in {countdown}...", WINDOW_WIDTH // 2, GAME_AREA_Y + GAME_HEIGHT // 2, 
                          self.big_font, WHITE)
        else:
            self.draw_text("GO!", WINDOW_WIDTH // 2, GAME_AREA_Y + GAME_HEIGHT // 2, 
                          self.big_font, GREEN)

    def draw_screensaver(self):
        """Draw the screensaver with autonomous snake and New Game button."""
        # Draw the same game background
        self.screen.fill(BLACK)
        
        # Draw header area
        header_rect = pygame.Rect(0, 0, WINDOW_WIDTH, HEADER_HEIGHT)
        pygame.draw.rect(self.screen, DARK_GRAY, header_rect)
        pygame.draw.rect(self.screen, LIGHT_GRAY, header_rect, 2)  # Border
        
        # Draw game area background and frame
        game_rect = pygame.Rect(0, GAME_AREA_Y, WINDOW_WIDTH, GAME_HEIGHT)
        pygame.draw.rect(self.screen, BLACK, game_rect)
        pygame.draw.rect(self.screen, BLUE, game_rect, FRAME_WIDTH)
        
        # Draw level obstacles (screensaver uses level 1 - no obstacles)
        self.level_manager.draw(self.screen)
        
        # Draw game objects
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        
        # Draw semi-transparent overlay over game area only
        overlay = pygame.Surface((WINDOW_WIDTH, GAME_HEIGHT))
        overlay.set_alpha(100)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, GAME_AREA_Y))
        
        # Draw "New Game" button
        button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, GAME_AREA_Y + GAME_HEIGHT // 2 - 25, 200, 50)
        
        # Check if mouse is hovering over button
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = button_rect.collidepoint(mouse_pos)
        
        # Button colors
        button_color = (0, 150, 0) if is_hovering else (0, 100, 0)
        border_color = (0, 255, 0) if is_hovering else (0, 200, 0)
        
        # Draw button
        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=10)
        pygame.draw.rect(self.screen, border_color, button_rect, 3, border_radius=10)
        
        # Draw button text
        button_font = pygame.font.Font(None, 48)
        self.draw_text("New Game", WINDOW_WIDTH // 2, GAME_AREA_Y + GAME_HEIGHT // 2, button_font, WHITE)

    def draw(self):
        """Draw the current game state."""
        if self.state == GameState.SCREENSAVER:
            self.draw_screensaver()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.PAUSED:
            self.draw_paused()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.state == GameState.LEVEL_TRANSITION:
            self.draw_level_transition()
        elif self.state == GameState.LEVEL_PREVIEW:
            self.draw_level_preview()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        running = True
        
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            
            # Use different frame rates for different states
            if self.state == GameState.LEVEL_TRANSITION:
                self.clock.tick(60)  # Fixed 60 FPS for consistent countdown timing
            else:
                self.clock.tick(self.speed)  # Variable speed for gameplay
        
        pygame.quit()
        sys.exit()

def main():
    """Main function to start the game."""
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
