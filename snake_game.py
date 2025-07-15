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
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

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
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    LEVEL_TRANSITION = 5

class Snake:
    """Snake class to handle snake logic and rendering."""
    
    def __init__(self):
        """Initialize the snake at the center of the screen."""
        self.reset()
    
    def reset(self):
        """Reset snake to initial state."""
        center_x = GRID_WIDTH // 2
        center_y = GRID_HEIGHT // 2
        self.body = [(center_x, center_y), (center_x - 1, center_y), (center_x - 2, center_y)]
        self.direction = Direction.RIGHT
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
            center_x = x * GRID_SIZE + GRID_SIZE // 2 + FRAME_WIDTH
            center_y = y * GRID_SIZE + GRID_SIZE // 2 + FRAME_WIDTH
            
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
                segment_rect = pygame.Rect(x * GRID_SIZE + 2 + FRAME_WIDTH, y * GRID_SIZE + 2 + FRAME_WIDTH, 
                                         GRID_SIZE - 4, GRID_SIZE - 4)
                
                # Main body color
                pygame.draw.rect(screen, DARK_GREEN, segment_rect, border_radius=6)
                
                # Add texture with lighter inner rectangle
                inner_rect = pygame.Rect(x * GRID_SIZE + 4 + FRAME_WIDTH, y * GRID_SIZE + 4 + FRAME_WIDTH, 
                                       GRID_SIZE - 8, GRID_SIZE - 8)
                pygame.draw.rect(screen, LIGHT_GREEN, inner_rect, border_radius=4)
                
                # Add outline
                pygame.draw.rect(screen, SNAKE_OUTLINE, segment_rect, 2, border_radius=6)
        
        # Draw connections between segments to make it look continuous
        for i in range(len(self.body) - 1):
            x1, y1 = self.body[i]
            x2, y2 = self.body[i + 1]
            
            center_x1 = x1 * GRID_SIZE + GRID_SIZE // 2 + FRAME_WIDTH
            center_y1 = y1 * GRID_SIZE + GRID_SIZE // 2 + FRAME_WIDTH
            center_x2 = x2 * GRID_SIZE + GRID_SIZE // 2 + FRAME_WIDTH
            center_y2 = y2 * GRID_SIZE + GRID_SIZE // 2 + FRAME_WIDTH
            
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
        center_y = y * GRID_SIZE + GRID_SIZE // 2 + FRAME_WIDTH
        
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
            rect = pygame.Rect(x * GRID_SIZE + FRAME_WIDTH, y * GRID_SIZE + FRAME_WIDTH, 
                             GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, BLUE, rect)
            pygame.draw.rect(screen, WHITE, rect, 1)
    
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
    
    def generate_obstacles(self):
        """Generate obstacles for current level."""
        self.obstacles = []
        
        if self.current_level == 1:
            # No obstacles in level 1
            pass
        elif self.current_level == 2:
            # Simple horizontal line in middle
            obstacles = [(x, GRID_HEIGHT // 2) for x in range(GRID_WIDTH // 3, 2 * GRID_WIDTH // 3)]
            self.obstacles.append(Obstacle(obstacles))
        elif self.current_level == 3:
            # Vertical lines on sides
            left_line = [(5, y) for y in range(5, GRID_HEIGHT - 5)]
            right_line = [(GRID_WIDTH - 6, y) for y in range(5, GRID_HEIGHT - 5)]
            self.obstacles.append(Obstacle(left_line))
            self.obstacles.append(Obstacle(right_line))
        elif self.current_level == 4:
            # Cross pattern
            horizontal = [(x, GRID_HEIGHT // 2) for x in range(8, GRID_WIDTH - 8)]
            vertical = [(GRID_WIDTH // 2, y) for y in range(8, GRID_HEIGHT - 8)]
            self.obstacles.append(Obstacle(horizontal + vertical))
        elif self.current_level == 5:
            # Maze-like pattern
            obstacles = []
            # Top and bottom barriers with gaps
            obstacles.extend([(x, 8) for x in range(5, 15)])
            obstacles.extend([(x, 8) for x in range(20, 30)])
            obstacles.extend([(x, GRID_HEIGHT - 9) for x in range(10, 20)])
            obstacles.extend([(x, GRID_HEIGHT - 9) for x in range(25, 35)])
            # Side barriers
            obstacles.extend([(8, y) for y in range(12, 18)])
            obstacles.extend([(GRID_WIDTH - 9, y) for y in range(12, 18)])
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
                            if 3 < x < GRID_WIDTH - 3 and 3 < y < GRID_HEIGHT - 3:
                                obstacles.append((x, y))
            
            # Add some guaranteed linear obstacles for higher levels
            if self.current_level >= 8:
                # Add random horizontal and vertical lines
                for _ in range(self.current_level // 4):
                    if random.choice([True, False]):  # Horizontal line
                        y_pos = random.randint(5, GRID_HEIGHT - 6)
                        x_start = random.randint(5, GRID_WIDTH // 3)
                        x_end = random.randint(2 * GRID_WIDTH // 3, GRID_WIDTH - 5)
                        obstacles.extend([(x, y_pos) for x in range(x_start, x_end)])
                    else:  # Vertical line
                        x_pos = random.randint(5, GRID_WIDTH - 6)
                        y_start = random.randint(5, GRID_HEIGHT // 3)
                        y_end = random.randint(2 * GRID_HEIGHT // 3, GRID_HEIGHT - 5)
                        obstacles.extend([(x_pos, y) for y in range(y_start, y_end)])
            
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
    
    def reset_game(self):
        """Reset the game to initial state."""
        self.snake = Snake()
        self.food = Food()
        self.level_manager = LevelManager()
        self.score = 0
        self.apples_eaten = 0
        self.speed = INITIAL_SPEED
        self.state = GameState.MENU
        self.portal_open = False
        self.transition_timer = 0
        
        # Ensure food doesn't spawn on snake or obstacles
        self.respawn_food_safely()
    
    def respawn_food_safely(self):
        """Respawn food in a safe location away from snake and obstacles."""
        while True:
            self.food.position = self.food.generate_position()
            if (self.food.position not in self.snake.body and 
                not self.level_manager.check_collision(self.food.position)):
                break
    
    def handle_input(self):
        """Handle keyboard input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
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
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.PLAYING
                        self.transition_timer = 0
                
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_m:
                        self.reset_game()
                        self.state = GameState.MENU
                
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
        
        # Check if all snake segments are above the top border
        for x, y in self.snake.body:
            if y >= 0:  # Still in play area
                return False
        return True
    
    def update(self):
        """Update game logic."""
        if self.state == GameState.LEVEL_TRANSITION:
            self.transition_timer += 1
            if self.transition_timer > 180:  # 3 seconds at 60 FPS
                self.level_manager.next_level()
                self.portal_open = False
                self.apples_eaten = 0
                self.state = GameState.PLAYING
                self.transition_timer = 0
            return
        
        if self.state != GameState.PLAYING:
            return
        
        # Check if portal should open
        if self.apples_eaten >= APPLES_PER_LEVEL and not self.portal_open:
            self.portal_open = True
        
        # Move snake
        self.snake.move()
        
        # Check portal collision and level progression
        if self.portal_open and self.check_portal_collision():
            # Allow snake to move through portal
            pass
        elif self.portal_open and self.snake_fully_through_portal():
            # Transition to next level
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
            portal_left = portal_center - (PORTAL_WIDTH // (2 * GRID_SIZE))
            portal_right = portal_center + (PORTAL_WIDTH // (2 * GRID_SIZE))
            
            # If snake is in portal area, allow movement beyond normal boundaries
            if portal_left <= head_x <= portal_right and head_y <= -1:
                pass  # Allow portal movement
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
    
    def draw_menu(self):
        """Draw the main menu."""
        self.screen.fill(BLACK)
        
        self.draw_text("SNAKE GAME", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100, self.big_font, GREEN)
        self.draw_text("Press SPACE to Start", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.draw_text("Use Arrow Keys or WASD to Move", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40)
        self.draw_text("Press ESC to Quit", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80)
    
    def draw_game(self):
        """Draw the game screen."""
        self.screen.fill(BLACK)
        
        # Draw blue frame around the arena
        frame_rect = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, BLUE, frame_rect, FRAME_WIDTH)
        
        # Draw portal opening if active
        if self.portal_open:
            portal_center = WINDOW_WIDTH // 2
            portal_left = portal_center - PORTAL_WIDTH // 2
            portal_rect = pygame.Rect(portal_left, 0, PORTAL_WIDTH, FRAME_WIDTH)
            pygame.draw.rect(self.screen, BLACK, portal_rect)
            # Add glowing effect around portal
            glow_rect = pygame.Rect(portal_left - 5, 0, PORTAL_WIDTH + 10, FRAME_WIDTH + 5)
            pygame.draw.rect(self.screen, (100, 200, 255), glow_rect, 2)
        
        # Draw level obstacles
        self.level_manager.draw(self.screen)
        
        # Draw game objects
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        
        # Draw score and level info
        level_text = f"Level: {self.level_manager.current_level}"
        self.draw_text(level_text, 70, 30)
        
        score_text = f"Score: {self.score}"
        self.draw_text(score_text, WINDOW_WIDTH - 70, 30)
        
        apples_text = f"Apples: {self.apples_eaten}/{APPLES_PER_LEVEL}"
        self.draw_text(apples_text, WINDOW_WIDTH // 2, 30)
    
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
        """Draw the level transition screen."""
        self.screen.fill(BLACK)
        
        self.draw_text(f"LEVEL {self.level_manager.current_level} COMPLETE!", 
                      WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60, self.big_font, GREEN)
        self.draw_text(f"Entering Level {self.level_manager.current_level + 1}...", 
                      WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)
        
        # Show countdown
        countdown = 3 - (self.transition_timer // 60)
        if countdown > 0:
            self.draw_text(f"{countdown}", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60, 
                          self.big_font, WHITE)

    def draw(self):
        """Draw the current game state."""
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.PAUSED:
            self.draw_paused()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.state == GameState.LEVEL_TRANSITION:
            self.draw_level_transition()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        running = True
        
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(self.speed)
        
        pygame.quit()
        sys.exit()

def main():
    """Main function to start the game."""
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
