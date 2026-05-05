# Adventure Game

A small Pygame text-adventure-style demo with four rooms, room items, and a simple inventory.

## How to Run

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the game:
   ```bash
   python adventure_game.py
   ```

## Notes

- The game window now opens at 1280×768 to support a larger top-down room layout.
- The left panel is rendered from room tile data, and item sprites are placed from `rooms.json` positions.
- A Kenney top-down asset pack is used for floor, wall, door, player, and item sprites.

## Controls

- ← / → or A / D : move between rooms
- 1-9 : select an item in the current room
- P : pick up the selected item if it is pickupable
- I : check inventory
- R : restart the game
- Esc : quit

## Rooms

- Bedroom: bed, table, window, plant
- Bathroom: bathtub, sink, toilet
- Living Room: couch, TV
- Kitchen: fridge, sink

## Assets

The game loads tile and item sprites from the `assets/` folder. A Kenney mini-dungeon asset pack was downloaded and extracted into `assets/`, and the relevant preview images were copied and renamed for use in the game.
