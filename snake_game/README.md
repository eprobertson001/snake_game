# Snake Game

A classic Snake game implementation in Python using pygame, recreating the nostalgic DOS-style gaming experience.

## Features

- Classic Snake gameplay mechanics
- Random food generation
- Real-time score tracking
- Collision detection (walls and self)
- Clean, retro-style graphics

## Requirements

- Python 3.7+
- pygame library

## Installation

1. Clone or download this repository
2. Install pygame:
   ```bash
   pip install pygame
   ```

## How to Play

1. Run the game:
   ```bash
   python snake_game.py
   ```

2. Controls:
   - **Arrow Keys** or **WASD**: Move the snake
   - **SPACE**: Pause/Resume game
   - **R**: Restart game (when game over)
   - **ESC**: Quit game

3. Objective:
   - Control the snake to eat food (red squares)
   - Each food eaten increases your score and snake length
   - Avoid hitting walls or the snake's own body
   - Try to achieve the highest score possible!

## Game Rules

- The snake moves continuously in the direction last pressed
- Eating food increases score by 10 points and snake length by 1
- Game ends when snake hits walls or itself
- Speed increases slightly as score increases

## Project Structure

```
snake_game/
│
├── snake_game.py          # Main game file
├── requirements.txt       # Python dependencies
├── README.md             # This file
```

## Development

This project is designed to be easily extensible. You can add features like:
- High score persistence
- Multiple difficulty levels
- Power-ups and special food types
- Sound effects and background music
- Different game modes
- Better graphics and animations

## License

This project is open source and available under the MIT License.
