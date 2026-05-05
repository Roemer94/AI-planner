"""Room and item definitions for the Pygame adventure game."""

import json
from pathlib import Path

DATA_PATH = Path(__file__).parent / "rooms.json"

with open(DATA_PATH, "r", encoding="utf-8") as data_file:
    data = json.load(data_file)

rooms = data["rooms"]
starting_room = data["starting_room"]
win_room = data["win_room"]
