# Project: My Adventure Game

## Tech Stack
- Language: Python 3
- Graphics/Game Engine: Pygame (pip install pygame)
- No other GUI libraries (no Tkinter, no PyQt, etc.)

## Project Structure
- src/main.py        → entry point and game loop
- src/player.py      → player class
- src/scenes.py      → game scenes/levels
- src/ui.py          → HUD and menus

## Conventions
- All drawing happens in Pygame surface objects
- 60 FPS target using pygame.time.Clock