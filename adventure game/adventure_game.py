"""Pygame adventure game with tile-based rooms, player movement, and item sprites."""

import json
import math
import sys
import pygame
import random
from pathlib import Path
from typing import Dict, List, Any

DATA_FOLDER = Path(__file__).parent
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
GAME_PANEL_WIDTH = 960
STATUS_PANEL_WIDTH = SCREEN_WIDTH - GAME_PANEL_WIDTH
TILE_SIZE = 64
PLAYER_SIZE = TILE_SIZE * 2
ITEM_SIZE = 56
MAP_X = (GAME_PANEL_WIDTH - 12 * TILE_SIZE) // 2
MAP_Y = (SCREEN_HEIGHT - 10 * TILE_SIZE) // 2

BACKGROUND_COLOR = (18, 24, 42)
HUD_BACKGROUND = (22, 28, 44)
TEXT_COLOR = (245, 245, 245)
ACCENT_COLOR = (255, 215, 130)
WARNING_COLOR = (255, 130, 95)
EXIT_COLOR = (255, 220, 80)
PLAYER_SKIN_COLOR = (248, 203, 173)
PLAYER_TUNIC_COLOR = (45, 90, 190)
PLAYER_BOOT_COLOR = (32, 40, 75)
HIGHLIGHT_COLOR = (118, 255, 148)
KEY_ITEM_COLOR = (255, 230, 90)
SHADOW_ALPHA = 110

ROOM_THEMES = {
    "Bedroom": {
        "floor": (232, 205, 163),
        "wall": (175, 135, 90),
        "panel": (246, 229, 201),
        "border": (193, 145, 92),
    },
    "Bathroom": {
        "floor": (188, 214, 237),
        "wall": (120, 160, 190),
        "panel": (216, 235, 249),
        "border": (97, 141, 175),
    },
    "Living Room": {
        "floor": (178, 132, 84),
        "wall": (118, 78, 42),
        "panel": (208, 160, 110),
        "border": (150, 96, 48),
    },
    "Kitchen": {
        "floor": (207, 211, 218),
        "wall": (140, 150, 162),
        "panel": (228, 231, 237),
        "border": (155, 165, 176),
    },
    "Dungeon": {
        "floor": (60, 60, 80),
        "wall": (40, 40, 50),
        "panel": (80, 80, 100),
        "border": (100, 100, 120),
    },
    "Treasure Room": {
        "floor": (255, 220, 100),
        "wall": (200, 170, 60),
        "panel": (255, 240, 150),
        "border": (220, 190, 80),
    },
}

ASSETS_PATH = DATA_FOLDER / "assets"
TILE_ASSET_FILES = {
    0: "floor.png",
    1: "wall.png",
    2: "door.png",
}
ITEM_ASSET_MAP = {
    "bed": "bed.png",
    "table": "table.png",
    "window": "window.png",
    "plant": "plant.png",
    "bathtub": "bathtub.png",
    "sink": "crate_small.png",
    "toilet": "barrel.png",
    "couch": "couch.png",
    "TV": "chest.png",
    "fridge": "fridge.png",
}

ITEM_COLORS = {
    "bed": (224, 120, 100),
    "table": (210, 160, 95),
    "window": (135, 200, 255),
    "plant": (120, 190, 120),
    "key": (255, 220, 80),
    "bathtub": (180, 220, 240),
    "sink": (160, 170, 190),
    "toilet": (200, 200, 205),
    "couch": (190, 110, 70),
    "TV": (50, 50, 50),
    "fridge": (180, 190, 205),
}


# Puzzle Game Classes
class HangmanGame:
    """Hangman word guessing game."""
    
    def __init__(self):
        self.words = ["ADVENTURE", "TREASURE", "MYSTERY", "PUZZLE", "DRAGON", "CASTLE", "QUEST", "MAGIC", "PHANTOM", "GOBLIN", "PHOENIX"]
        self.word = random.choice(self.words)
        self.guessed_letters = set()
        self.wrong_guesses = 0
        self.max_wrong = 6
        self.start_time = pygame.time.get_ticks()
        self.completed = False
        self.won = False
        self.games_played = 0
        self.feedback_message = ""
        self.feedback_timer = 0
        
    def get_display_word(self):
        return " ".join(letter if letter in self.guessed_letters else "_" for letter in self.word)
    
    def guess_letter(self, letter):
        letter = letter.upper()
        if letter in self.guessed_letters:
            self.feedback_message = f"{letter} already guessed!"
            self.feedback_timer = 60
            return False
        self.guessed_letters.add(letter)
        if letter not in self.word:
            self.wrong_guesses += 1
            self.feedback_message = f"{letter} is wrong!"
        else:
            self.feedback_message = f"Good! {letter} is in the word!"
        self.feedback_timer = 60
        self.check_completion()
        return True
    
    def check_completion(self):
        if all(letter in self.guessed_letters for letter in self.word):
            self.completed = True
            self.won = True
        elif self.wrong_guesses >= self.max_wrong:
            self.completed = True
            self.won = False
    
    def next_word(self):
        """Generate a new word and reset guesses."""
        self.word = random.choice(self.words)
        self.guessed_letters = set()  # Reset guesses for new word
        self.wrong_guesses = 0
        self.completed = False
        self.won = False
        self.games_played += 1
        self.feedback_message = f"New word! ({self.games_played} attempt)"
        self.feedback_timer = 120
    
    def get_guessed_letters(self):
        """Get letters that have been guessed."""
        correct = [letter for letter in self.guessed_letters if letter in self.word]
        wrong = [letter for letter in self.guessed_letters if letter not in self.word]
        return sorted(correct), sorted(wrong)
    
    def get_remaining_letters(self):
        return [chr(i) for i in range(ord('A'), ord('Z') + 1) if chr(i) not in self.guessed_letters]


class NumberGuessingGame:
    """Guess the number game."""
    
    def __init__(self):
        self.target_number = random.randint(1, 100)
        self.attempts = 0
        self.max_attempts = 7
        self.start_time = pygame.time.get_ticks()
        self.completed = False
        self.won = False
        self.feedback = "Guess a number between 1 and 100"
        self.guess_history = []
        self.guess_feedback = []  # Store feedback for each guess
        
    def guess(self, number):
        try:
            num = int(number)
            if num < 1 or num > 100:
                self.feedback = "Please enter a number between 1 and 100"
                return False
            self.attempts += 1
            self.guess_history.append(num)
            
            if num == self.target_number:
                self.completed = True
                self.won = True
                self.guess_feedback.append("Correct!")
                self.feedback = f"Correct! You got it in {self.attempts} tries!"
            elif num < self.target_number:
                feedback_msg = "Too low!"
                self.guess_feedback.append(feedback_msg)
                self.feedback = f"{feedback_msg} Attempts left: {self.max_attempts - self.attempts}"
            else:
                feedback_msg = "Too high!"
                self.guess_feedback.append(feedback_msg)
                self.feedback = f"{feedback_msg} Attempts left: {self.max_attempts - self.attempts}"
            
            if self.attempts >= self.max_attempts and not self.won:
                self.completed = True
                self.won = False
                self.guess_feedback.append("Game Over!")
                self.feedback = f"Game Over! The number was {self.target_number}"
            
            return True
        except ValueError:
            self.feedback = "Please enter a valid number"
            return False


class MemoryGame:
    """Memory game with letters and words."""
    
    def __init__(self):
        self.words = ["CAT", "DOG", "BIRD", "FISH", "TREE", "HOUSE", "CAR", "BOOK", "STAR", "MOON"]
        self.letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        self.sequence = []
        self.player_sequence = []
        self.current_beat = 0
        self.completed = False
        self.won = False
        self.feedback = "Memorize the sequence, then repeat it!"
        self.start_time = pygame.time.get_ticks()
        self.difficulty = 1
        self.game_type = "letters"  # "letters" or "words"
        self.generate_sequence()
        self.showing_sequence = True
        self.show_timer = 0
        self.sequence_timer = 0
        
    def generate_sequence(self):
        """Generate a sequence based on current difficulty and game type."""
        self.sequence = []
        
        if self.game_type == "letters":
            # Start with letters, switch to words at higher difficulty
            if self.difficulty >= 4:
                self.game_type = "words"
                self.feedback = "Now memorizing words!"
                self.show_timer = 120
            else:
                # Letters sequence
                for _ in range(self.difficulty + 2):  # 3, 4, 5, 6 letters
                    self.sequence.append(random.choice(self.letters))
        else:
            # Words sequence
            for _ in range(self.difficulty - 2):  # 2, 3, 4, 5 words
                self.sequence.append(random.choice(self.words))
    
    def key_pressed(self, key):
        if self.showing_sequence:
            return False
        
        # Convert key to expected format
        if self.game_type == "letters":
            key = key.upper()
            if key not in self.letters:
                return False
        else:  # words
            key = key.upper()
            # For words, we expect the full word to be typed
            return False  # Words need text input, not single keys
        
        self.player_sequence.append(key)
        
        # Check if player input matches sequence so far
        if self.player_sequence[-1] != self.sequence[len(self.player_sequence) - 1]:
            self.completed = True
            self.won = False
            self.feedback = "Wrong sequence! Game Over."
            return False
        
        # Check if player completed the sequence
        if len(self.player_sequence) == len(self.sequence):
            if self.difficulty < 6:  # Max 6 levels
                self.difficulty += 1
                self.generate_sequence()
                self.player_sequence = []
                self.showing_sequence = True
                self.show_timer = 180
                if self.game_type == "letters":
                    self.feedback = f"Great! Level {self.difficulty} - Memorize {len(self.sequence)} letters!"
                else:
                    self.feedback = f"Great! Level {self.difficulty} - Memorize {len(self.sequence)} words!"
            else:
                self.completed = True
                self.won = True
                self.feedback = "Excellent! You mastered all memory levels!"
        
        return True
    
    def update(self):
        """Update game state."""
        if self.showing_sequence:
            if self.show_timer > 0:
                self.show_timer -= 1
            else:
                self.showing_sequence = False
                self.feedback = "Your turn! Repeat the sequence."
    
    def get_display_sequence(self):
        """Get the sequence as a string for display."""
        if self.game_type == "letters":
            return " → ".join(self.sequence)
        else:
            return " → ".join(self.sequence)


class TypingGame:
    """Speed typing challenge game."""

    DIFFICULTY_OPTIONS = ["Easy", "Normal", "Hard"]

    def __init__(self, difficulty_option: str = "Normal"):
        self.phrases = [
            "MAGIC KEY",
            "SECRET DOOR",
            "LOST MAP",
            "BRIGHT TORCH",
            "HIDDEN TREASURE",
            "DARK DUNGEON",
            "SHINING COIN",
            "RAPID TYPING",
            "BRAVE ADVENTURER",
            "ANCIENT CHEST",
        ]
        self.current_phrase = ""
        self.completed = False
        self.won = False
        self.feedback = "Memorize the phrase, then type it quickly."
        self.difficulty_option = difficulty_option if difficulty_option in self.DIFFICULTY_OPTIONS else "Normal"
        self.round = 1
        self.showing_phrase = True
        self.show_timer = 150
        self.time_limit = 0
        self.start_time = 0
        self.generate_phrase()

    def set_difficulty(self, difficulty_option: str) -> None:
        if difficulty_option in self.DIFFICULTY_OPTIONS:
            self.difficulty_option = difficulty_option
        self.round = 1
        self.generate_phrase()
        self.feedback = f"Difficulty set to {self.difficulty_option}. Memorize the phrase."

    def generate_phrase(self):
        allowed_length = 12 if self.difficulty_option == "Easy" else 16 if self.difficulty_option == "Normal" else 999
        pool = [phrase for phrase in self.phrases if len(phrase) <= allowed_length]
        self.current_phrase = random.choice(pool).upper()
        self.showing_phrase = True
        self.show_timer = 150
        self.feedback = f"Memorize the phrase ({self.difficulty_option})."

    def get_time_modifier(self) -> int:
        if self.difficulty_option == "Easy":
            return 280
        if self.difficulty_option == "Normal":
            return 220
        return 150

    def start_typing(self):
        self.showing_phrase = False
        self.start_time = pygame.time.get_ticks()
        base_time = len(self.current_phrase) * self.get_time_modifier()
        self.time_limit = max(2200, base_time - (self.round - 1) * 90)
        self.feedback = f"Type the phrase now! {self.time_limit // 1000}.{(self.time_limit % 1000) // 100}s left."

    def submit(self, text: str) -> bool:
        entered = text.upper().strip()
        if entered == self.current_phrase:
            if self.round < 6:
                self.round += 1
                self.generate_phrase()
                self.feedback = f"Correct! Round {self.round} - memorize the next phrase."
                return True
            self.completed = True
            self.won = True
            self.feedback = "Typing master! You completed the challenge!"
            return True

        self.completed = True
        self.won = False
        self.feedback = "Typed incorrectly! Speed typing failed."
        return False

    def update(self):
        if self.showing_phrase:
            if self.show_timer > 0:
                self.show_timer -= 1
            else:
                self.start_typing()
        elif not self.completed and self.start_time > 0:
            elapsed = pygame.time.get_ticks() - self.start_time
            if elapsed > self.time_limit:
                self.completed = True
                self.won = False
                self.feedback = "Time's up! You were too slow."

    def get_time_remaining(self) -> int:
        if self.start_time == 0:
            return self.time_limit
        return max(0, self.time_limit - (pygame.time.get_ticks() - self.start_time))


class RiddleGame:
    """Riddle guessing game."""
    
    def __init__(self):
        self.riddles = [
            {"question": "I have a head and a tail but no body. What am I?", "answer": "COIN"},
            {"question": "The more you take, the more you leave behind. What am I?", "answer": "FOOTSTEPS"},
            {"question": "I am taken from a mine and shut up in a wooden case, yet no one ever made me. What am I?", "answer": "PENCIL"},
            {"question": "What has keys but no locks, space but no room, and you can enter but can't go inside?", "answer": "KEYBOARD"},
            {"question": "What can travel around the world while staying in a corner?", "answer": "STAMP"},
        ]
        self.current_riddle_index = 0
        self.correct_answers = 0
        self.attempts = 0
        self.start_time = pygame.time.get_ticks()
        self.completed = False
        self.won = False
        self.feedback = ""
        self.update_feedback()
        
    def get_current_riddle(self):
        return self.riddles[self.current_riddle_index]["question"]
    
    def answer(self, user_answer):
        user_answer = user_answer.upper().strip()
        correct_answer = self.riddles[self.current_riddle_index]["answer"]
        self.attempts += 1
        
        if user_answer == correct_answer:
            self.correct_answers += 1
            self.feedback = f"Correct! That's right!"
            self.current_riddle_index += 1
            
            if self.current_riddle_index >= len(self.riddles):
                self.completed = True
                self.won = True
                self.feedback = f"Amazing! You solved all riddles!"
            else:
                self.update_feedback()
        else:
            if self.attempts >= 3:
                self.feedback = f"Wrong! The answer was: {correct_answer}"
                self.current_riddle_index += 1
                self.attempts = 0
                
                if self.current_riddle_index >= len(self.riddles):
                    self.completed = True
                    if self.correct_answers >= 3:
                        self.won = True
                        self.feedback = f"You solved {self.correct_answers}/{len(self.riddles)} riddles!"
                    else:
                        self.won = False
                        self.feedback = f"Game Over! You only solved {self.correct_answers}/{len(self.riddles)}"
                else:
                    self.update_feedback()
            else:
                self.feedback = f"Wrong! Try again. Attempts left: {3 - self.attempts}"
    
    def update_feedback(self):
        if self.current_riddle_index < len(self.riddles):
            self.feedback = f"Riddle {self.current_riddle_index + 1}/{len(self.riddles)}"


def load_image(image_path: Path, size: tuple[int, int]) -> pygame.Surface | None:
    try:
        image = pygame.image.load(image_path).convert_alpha()
        return pygame.transform.smoothscale(image, size)
    except (FileNotFoundError, pygame.error):
        return None


def tile_rect(tile: List[int]) -> pygame.Rect:
    x = MAP_X + tile[0] * TILE_SIZE
    y = MAP_Y + tile[1] * TILE_SIZE
    return pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)


def get_room_theme(room_name: str) -> Dict[str, tuple[int, int, int]]:
    return ROOM_THEMES.get(room_name, ROOM_THEMES["Bedroom"])

pygame.init()
pygame.display.set_caption("Adventure Game")
BODY_FONT = pygame.font.SysFont("arial", 16)
SECTION_FONT = pygame.font.SysFont("arial", 22, bold=True)
TITLE_FONT = pygame.font.SysFont("arial", 36, bold=True)

ROOMS_PATH = DATA_FOLDER / "rooms.json"
with open(ROOMS_PATH, "r", encoding="utf-8") as file:
    game_data = json.load(file)

rooms: Dict[str, Dict[str, Any]] = game_data["rooms"]
starting_room: str = game_data["starting_room"]
win_room: str = game_data["win_room"]


def tile_center(tile: List[int]) -> pygame.Vector2:
    rect = tile_rect(tile)
    return pygame.Vector2(rect.centerx - PLAYER_SIZE / 2, rect.centery - PLAYER_SIZE / 2)


class Player:
    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.facing = "down"
        self.animation_frame = 0
        self.animation_timer = 0
        self.is_picking_up = False
        self.pickup_animation_timer = 0
        self.walk_animation_offset = 0
    
    def update_animations(self) -> None:
        """Update player animations."""
        self.animation_timer += 1
        
        # Walking animation
        if self.walk_animation_offset != 0:
            self.animation_frame = (self.animation_timer // 10) % 4
            self.walk_animation_offset *= 0.9  # Decay
            if abs(self.walk_animation_offset) < 0.1:
                self.walk_animation_offset = 0
        
        # Pickup animation
        if self.is_picking_up:
            self.pickup_animation_timer += 1
            if self.pickup_animation_timer > 30:  # 30 frames for pickup animation
                self.is_picking_up = False
                self.pickup_animation_timer = 0
    
    def start_pickup_animation(self) -> None:
        """Start the pickup animation."""
        self.is_picking_up = True
        self.pickup_animation_timer = 0
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the player character."""
        # Calculate animation offsets
        walk_offset = self.walk_animation_offset
        pickup_offset = 0
        if self.is_picking_up:
            # Simple pickup animation: arms raise
            progress = min(self.pickup_animation_timer / 15, 1)
            pickup_offset = -10 * progress
        
        body = self.rect.inflate(-40, -28)
        body.bottom = self.rect.bottom - 12 + walk_offset
        pygame.draw.rect(screen, PLAYER_TUNIC_COLOR, body, border_radius=18)
        
        head_center = (self.rect.centerx, self.rect.top + 34 + walk_offset)
        pygame.draw.circle(screen, PLAYER_SKIN_COLOR, head_center, 24)
        
        # Eyes
        eye_y = head_center[1] - 5
        left_eye = (head_center[0] - 8, eye_y)
        right_eye = (head_center[0] + 8, eye_y)
        pygame.draw.circle(screen, (0, 0, 0), left_eye, 2)
        pygame.draw.circle(screen, (0, 0, 0), right_eye, 2)
        
        # Legs with animation
        leg_offset = math.sin(self.animation_frame * math.pi / 2) * 2
        left_leg = pygame.Rect(body.left + 10, body.bottom - 6 + leg_offset, 16, 24)
        right_leg = pygame.Rect(body.right - 26, body.bottom - 6 - leg_offset, 16, 24)
        pygame.draw.rect(screen, PLAYER_BOOT_COLOR, left_leg, border_radius=8)
        pygame.draw.rect(screen, PLAYER_BOOT_COLOR, right_leg, border_radius=8)
        
        # Arms with pickup animation
        if self.facing == "left":
            arm = pygame.Rect(body.left - 14, body.y + 16 + pickup_offset, 16, 8)
            pygame.draw.rect(screen, PLAYER_TUNIC_COLOR, arm, border_radius=8)
        elif self.facing == "right":
            arm = pygame.Rect(body.right - 2, body.y + 16 + pickup_offset, 16, 8)
            pygame.draw.rect(screen, PLAYER_TUNIC_COLOR, arm, border_radius=8)
        elif self.facing == "up":
            pygame.draw.polygon(screen, PLAYER_TUNIC_COLOR, [
                (body.centerx - 16, body.y + 4 + pickup_offset),
                (body.centerx + 16, body.y + 4 + pickup_offset),
                (body.centerx, body.y - 10 + pickup_offset),
            ])
        else:  # down
            pygame.draw.polygon(screen, PLAYER_TUNIC_COLOR, [
                (body.centerx - 16, body.bottom - 4 + pickup_offset),
                (body.centerx + 16, body.bottom - 4 + pickup_offset),
                (body.centerx, body.bottom + 16 + pickup_offset),
            ])


class Game:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.current_room = starting_room
        self.inventory: List[str] = []
        self.selected_item_index: int | None = None
        self.message = "Use arrow keys or A/D to move, P to pick up, I to open inventory."
        self.message_color = TEXT_COLOR
        self.message_timer = 0
        self.running = True
        self.velocity = pygame.Vector2(0, 0)
        self.player = Player(0, 0)
        self.player_sprite = None
        self.tile_sprites: Dict[int, pygame.Surface | None] = {}
        self.item_sprites: Dict[str, pygame.Surface | None] = {}
        self.generic_item_sprite = None
        self.pickup_feedback_timer = 0
        self.pickup_feedback_text = ""
        self.floating_text = ""
        self.floating_text_y = 0
        self.start_screen = True
        self.quest_stage = 0
        self.stage_message_timer = 0
        self.stage_message_text = ""
        self.pending_room: str | None = None
        self.pending_exit_info: dict | None = None
        self.door_open_timer = 0
        self.transition_timer = 0
        self.transition_room_name: str | None = None
        self.win_screen = False
        
        # Puzzle game states
        self.puzzle_active = False
        self.current_puzzle = None
        self.puzzle_input = ""
        self.hangman_game: HangmanGame | None = None
        self.number_game: NumberGuessingGame | None = None
        self.typing_game: TypingGame | None = None
        self.riddle_game: RiddleGame | None = None
        self.puzzle_completed_stages = {}  # Track which rooms had puzzles completed
        self.typing_difficulty_option = "Normal"

        self.load_assets()
        self.reset_room_position()
        
        self.load_assets()
        self.reset_room_position()

    def reset_room_position(self) -> None:
        room = rooms[self.current_room]
        start_tile = room.get("player_start", [1, 5])
        self.player.rect.topleft = tile_center(start_tile)
        self.velocity = pygame.Vector2(0, 0)
        self.player.facing = "down"
        self.selected_item_index = None

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.puzzle_active:
                    self.handle_puzzle_input(event)
                    continue
                if self.start_screen:
                    if event.key == pygame.K_SPACE:
                        self.start_screen = False
                        self.quest_stage = 1
                        self.stage_message_text = "Stage 1: Leave the Bedroom to begin."
                        self.stage_message_timer = 240
                    continue
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.velocity.x = 1
                    self.player.facing = "right"
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.velocity.x = -1
                    self.player.facing = "left"
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.velocity.y = 1
                    self.player.facing = "down"
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.velocity.y = -1
                    self.player.facing = "up"
                elif event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_e:
                    self.interact()
                elif event.key == pygame.K_p:
                    self.pick_up_selected_item()
                elif event.key == pygame.K_i:
                    self.show_inventory_message()
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    self.select_item(event.key - pygame.K_0)
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_RIGHT, pygame.K_d) and self.velocity.x > 0:
                    self.velocity.x = 0
                elif event.key in (pygame.K_LEFT, pygame.K_a) and self.velocity.x < 0:
                    self.velocity.x = 0
                elif event.key in (pygame.K_DOWN, pygame.K_s) and self.velocity.y > 0:
                    self.velocity.y = 0
                elif event.key in (pygame.K_UP, pygame.K_w) and self.velocity.y < 0:
                    self.velocity.y = 0

    def reset_game(self) -> None:
        self.current_room = starting_room
        self.inventory = []
        self.selected_item_index = None
        self.set_message("The game has been reset.")
        self.reset_room_position()
        self.puzzle_completed_stages = {}
        self.quest_stage = 1
        self.win_screen = False

    def handle_puzzle_input(self, event: pygame.event.Event) -> None:
        """Handle input for active puzzle games."""
        if self.current_puzzle == "hangman" and self.hangman_game:
            if pygame.K_a <= event.key <= pygame.K_z:
                letter = chr(event.key - pygame.K_a + ord('A'))
                self.hangman_game.guess_letter(letter)
                if self.hangman_game.completed:
                    if self.hangman_game.won:
                        self.puzzle_active = False
                        self.complete_puzzle("Hangman")
                    else:
                        # Word was lost - generate new word but keep guesses
                        self.hangman_game.next_word()
                        # Game continues with new word
        
        elif self.current_puzzle == "number" and self.number_game:
            if event.key == pygame.K_RETURN:
                self.number_game.guess(self.puzzle_input)
                self.puzzle_input = ""
                if self.number_game.completed:
                    self.puzzle_active = False
                    if self.number_game.won:
                        self.complete_puzzle("Number Guessing")
                    else:
                        self.set_message(self.number_game.feedback, WARNING_COLOR)
            elif event.key == pygame.K_BACKSPACE:
                self.puzzle_input = self.puzzle_input[:-1]
            elif event.unicode.isdigit():
                if len(self.puzzle_input) < 3:
                    self.puzzle_input += event.unicode
        
        elif self.current_puzzle == "typing" and self.typing_game:
            if self.typing_game.showing_phrase:
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    difficulty_map = {
                        pygame.K_1: "Easy",
                        pygame.K_2: "Normal",
                        pygame.K_3: "Hard",
                    }
                    selected = difficulty_map[event.key]
                    self.typing_difficulty_option = selected
                    self.typing_game.set_difficulty(selected)
                    self.set_message(f"Difficulty set to {selected}.")
            else:
                if event.key == pygame.K_RETURN:
                    self.typing_game.submit(self.puzzle_input)
                    self.puzzle_input = ""
                    if self.typing_game.completed:
                        self.puzzle_active = False
                        if self.typing_game.won:
                            self.complete_puzzle("Typing Game")
                        else:
                            self.set_message(self.typing_game.feedback, WARNING_COLOR)
                elif event.key == pygame.K_BACKSPACE:
                    self.puzzle_input = self.puzzle_input[:-1]
                elif event.unicode.isprintable():
                    if len(self.puzzle_input) < 80:
                        self.puzzle_input += event.unicode
        
        elif self.current_puzzle == "riddle" and self.riddle_game:
            if event.key == pygame.K_RETURN:
                self.riddle_game.answer(self.puzzle_input)
                self.puzzle_input = ""
                if self.riddle_game.completed:
                    self.puzzle_active = False
                    if self.riddle_game.won:
                        self.complete_puzzle("Riddle Game")
                    else:
                        self.set_message(self.riddle_game.feedback, WARNING_COLOR)
            elif event.key == pygame.K_BACKSPACE:
                self.puzzle_input = self.puzzle_input[:-1]
            elif event.unicode.isalpha() or event.unicode == ' ':
                if len(self.puzzle_input) < 50:
                    self.puzzle_input += event.unicode

    def load_assets(self) -> None:
        self.tile_sprites = {
            tile_id: load_image(ASSETS_PATH / filename, (TILE_SIZE, TILE_SIZE))
            for tile_id, filename in TILE_ASSET_FILES.items()
        }
        self.item_sprites = {
            name: load_image(ASSETS_PATH / filename, (ITEM_SIZE, ITEM_SIZE))
            for name, filename in ITEM_ASSET_MAP.items()
        }
        self.generic_item_sprite = load_image(ASSETS_PATH / "barrel.png", (ITEM_SIZE, ITEM_SIZE))
        self.player_sprite = load_image(ASSETS_PATH / "player.png", (PLAYER_SIZE, PLAYER_SIZE))

    def get_item_sprite(self, item: Dict[str, Any]) -> pygame.Surface | None:
        return self.item_sprites.get(item["name"], self.generic_item_sprite)

    def get_item_rect(self, item_position: List[int], size: List[int] | None = None) -> pygame.Rect:
        size = size or [1, 1]
        x = MAP_X + item_position[0] * TILE_SIZE
        y = MAP_Y + item_position[1] * TILE_SIZE
        return pygame.Rect(x, y, TILE_SIZE * size[0], TILE_SIZE * size[1])

    def update(self) -> None:
        if self.transition_timer > 0:
            self.transition_timer -= 1
        
        # Update active puzzles
        if self.puzzle_active:
            if self.current_puzzle == "typing" and self.typing_game:
                self.typing_game.update()
        
        # Check if player reached the Treasure Room
        if self.current_room == "Treasure Room" and not self.win_screen:
            self.win_screen = True
            self.set_message("You have found the treasure! Press R to play again or Esc to quit.")

        if self.door_open_timer > 0:
            self.door_open_timer -= 1
            if self.door_open_timer == 0 and self.pending_room:
                self.current_room = self.pending_room
                self.reset_room_position()
                self.transition_timer = 90
                self.transition_room_name = self.current_room
                self.set_message(f"You enter the {self.current_room}.")
                self.pending_room = None
                self.pending_exit_info = None
            return

        self.move_player()
        self.check_room_change()

        # Update animations
        self.player.update_animations()

        if self.stage_message_timer > 0:
            self.stage_message_timer -= 1
            if self.stage_message_timer == 0:
                self.stage_message_text = ""
        if self.transition_timer > 0:
            self.transition_timer -= 1

    def move_player(self) -> None:
        if self.start_screen or self.door_open_timer > 0 or self.win_screen:
            return
        if self.velocity.length_squared() == 0:
            return

        speed = 3
        movement = self.velocity.normalize() * speed

        new_rect = self.player.rect.copy()
        new_rect.x += int(movement.x)
        push_index = self.get_pushable_item_at_rect(new_rect)
        if push_index is not None:
            dx = int(math.copysign(1, movement.x)) if movement.x != 0 else 0
            if self.push_item(push_index, dx, 0):
                self.player.rect.x = new_rect.x
                self.player.walk_animation_offset = 2  # Add walk bob
        elif not self.collides_with_walls(new_rect):
            self.player.rect.x = new_rect.x
            self.player.walk_animation_offset = 2

        new_rect = self.player.rect.copy()
        new_rect.y += int(movement.y)
        push_index = self.get_pushable_item_at_rect(new_rect)
        if push_index is not None:
            dy = int(math.copysign(1, movement.y)) if movement.y != 0 else 0
            if self.push_item(push_index, 0, dy):
                self.player.rect.y = new_rect.y
                self.player.walk_animation_offset = 2
        elif not self.collides_with_walls(new_rect):
            self.player.rect.y = new_rect.y
            self.player.walk_animation_offset = 2

    def collides_with_walls(self, rect: pygame.Rect) -> bool:
        room = rooms[self.current_room]
        for y, row in enumerate(room["tiles"]):
            for x, tile in enumerate(row):
                if tile == 1:
                    if rect.colliderect(tile_rect([x, y])):
                        return True
        return False

    def get_item_at_player(self) -> int | None:
        room = rooms[self.current_room]
        for index, item in enumerate(room["items"]):
            item_rect = self.get_item_rect(item["position"], item.get("size", [1, 1]))
            if self.player.rect.colliderect(item_rect):
                return index
        return None

    def get_item_at_rect(self, rect: pygame.Rect) -> int | None:
        room = rooms[self.current_room]
        for index, item in enumerate(room["items"]):
            item_rect = self.get_item_rect(item["position"], item.get("size", [1, 1]))
            if rect.colliderect(item_rect):
                return index
        return None

    def get_pushable_item_at_rect(self, rect: pygame.Rect) -> int | None:
        room = rooms[self.current_room]
        for index, item in enumerate(room["items"]):
            if item.get("pushable", False):
                item_rect = self.get_item_rect(item["position"], item.get("size", [1, 1]))
                if rect.colliderect(item_rect):
                    return index
        return None

    def can_move_rect(self, rect: pygame.Rect, ignore_index: int | None = None) -> bool:
        if self.collides_with_walls(rect):
            return False
        room = rooms[self.current_room]
        for index, item in enumerate(room["items"]):
            if index == ignore_index:
                continue
            item_rect = self.get_item_rect(item["position"], item.get("size", [1, 1]))
            if rect.colliderect(item_rect):
                return False
        return True

    def get_item_index_by_name(self, name: str) -> int | None:
        room = rooms[self.current_room]
        for index, item in enumerate(room["items"]):
            if item["name"] == name:
                return index
        return None

    def is_item_interactable(self, item: Dict[str, Any]) -> bool:
        return item.get("pickupable", False) or item["name"] in {"plant", "chest", "stove", "key", "puzzle_gate"}

    def complete_puzzle(self, puzzle_name: str) -> None:
        """Handle puzzle completion and unlock the exit."""
        self.puzzle_completed_stages[self.current_room] = True
        room = rooms[self.current_room]
        
        # Unlock the east exit
        if "east" in room["exits"]:
            room["exits"]["east"]["locked"] = False
            self.set_message(f"{puzzle_name} completed! The door opens.")
        
        self.pending_room = room["exits"]["east"]["room"]
        self.pending_exit_info = room["exits"]["east"]
        self.door_open_timer = 30
        self.quest_stage += 1

    def interact(self) -> None:
        room = rooms[self.current_room]
        
        # Check if there's a puzzle gate to interact with
        for index, item in enumerate(room["items"]):
            if item["name"] == "puzzle_gate":
                item_rect = self.get_item_rect(item["position"], item.get("size", [1, 1]))
                if self.player.rect.colliderect(item_rect.inflate(24, 24)):
                    if self.current_room not in self.puzzle_completed_stages:
                        self.start_puzzle()
                    else:
                        self.set_message("You have already completed the puzzle in this room.")
                    return
        
        if self.quest_stage == 1:
            plant_index = self.get_item_index_by_name("plant")
            if plant_index is not None:
                plant_rect = self.get_item_rect(room["items"][plant_index]["position"], room["items"][plant_index].get("size", [1, 1]))
                if self.player.rect.colliderect(plant_rect.inflate(24, 24)):
                    if self.get_item_index_by_name("key") is None:
                        room["items"].append({
                            "name": "key",
                            "description": "A brass key hidden under the plant.",
                            "pickupable": True,
                            "position": [5, 6],
                            "size": [1, 1],
                        })
                        self.set_message("You found a key hidden beneath the plant!")
                        self.floating_text = "+KEY"
                        self.floating_text_y = self.player.rect.top
                        self.pickup_feedback_timer = 90
                        return
                    self.set_message("The key is already revealed.")
                    return
        
        self.set_message("Nothing special happens.")
    
    def start_puzzle(self) -> None:
        """Initialize puzzle based on current room."""
        self.puzzle_active = True
        
        if self.current_room == "Bathroom":
            self.current_puzzle = "hangman"
            if self.hangman_game is None:
                self.hangman_game = HangmanGame()
            # Don't reset the game if it was already started
            self.set_message("Hangman puzzle started! Guess letters to find the word.")
        
        elif self.current_room == "Living Room":
            self.current_puzzle = "number"
            self.number_game = NumberGuessingGame()
            self.set_message("Number Guessing puzzle! Type a number and press Enter.")
        
        elif self.current_room == "Kitchen":
            self.current_puzzle = "typing"
            self.typing_game = TypingGame(self.typing_difficulty_option)
            self.set_message("Speed typing challenge! Press 1=Easy, 2=Normal, 3=Hard while the phrase is shown.")
        
        elif self.current_room == "Dungeon":
            self.current_puzzle = "riddle"
            self.riddle_game = RiddleGame()
            self.set_message("Riddle puzzle! Type your answer and press Enter.")

    def push_item(self, index: int, dx: int, dy: int) -> bool:
        room = rooms[self.current_room]
        item = room["items"][index]
        new_position = [item["position"][0] + dx, item["position"][1] + dy]
        new_rect = self.get_item_rect(new_position, item.get("size", [1, 1]))
        if not self.can_move_rect(new_rect, ignore_index=index):
            return False
        item["position"] = new_position
        if item["name"] == "box" and self.quest_stage == 2:
            plate_pos = room.get("plate_position")
            if plate_pos and item["position"] == plate_pos:
                room["plate_activated"] = True
                self.set_message("The pressure plate clicks into place! The chest is now unlocked.")
        return True

    def is_exit_locked(self, exit_info: Dict[str, Any]) -> bool:
        return exit_info.get("locked", False)

    def can_unlock_exit(self, exit_info: Dict[str, Any]) -> bool:
        required_item = exit_info.get("required_item")
        return required_item is not None and required_item in self.inventory

    def check_room_change(self) -> None:
        if self.pending_room is not None:
            return
        room = rooms[self.current_room]
        for exit_info in room["exits"].values():
            exit_rect = tile_rect(exit_info["position"])
            if self.player.rect.colliderect(exit_rect):
                if self.is_exit_locked(exit_info):
                    if self.can_unlock_exit(exit_info):
                        required_item = exit_info.get("required_item")
                        exit_info["locked"] = False
                        self.set_message(f"You use the {required_item} to unlock the way.")
                        self.pending_room = exit_info["room"]
                        self.pending_exit_info = exit_info
                        self.door_open_timer = 30
                        if self.quest_stage == 1:
                            self.complete_stage("Stage 1 complete! The bedroom door swings open.")
                        return
                    else:
                        required_item = exit_info.get("required_item")
                        locked_message = exit_info.get("locked_message", "The way is blocked.")
                        if required_item:
                            locked_message += f" You need a {required_item}."
                        self.set_message(locked_message, WARNING_COLOR)
                        return
                self.current_room = exit_info["room"]
                self.reset_room_position()
                self.transition_timer = 90
                self.transition_room_name = self.current_room
                self.set_message(f"You enter the {self.current_room}.")
                return

    def select_item(self, item_index: int) -> None:
        room = rooms[self.current_room]
        if 1 <= item_index <= len(room["items"]):
            self.selected_item_index = item_index - 1
            item = room["items"][self.selected_item_index]
            message = item["description"]
            if item.get("pickupable", False):
                message += " Walk closer and press P to pick it up."
            self.set_message(message)
        else:
            self.selected_item_index = None
            self.set_message("There is no item with that number here.", WARNING_COLOR)

    def pick_up_selected_item(self) -> None:
        room = rooms[self.current_room]
        index = self.selected_item_index if self.selected_item_index is not None else self.get_item_at_player()
        if index is None or index >= len(room["items"]):
            self.set_message("No item is close enough to pick up.", WARNING_COLOR)
            return

        item = room["items"][index]
        if not item.get("pickupable", False):
            self.set_message(f"You can't pick up the {item['name']}.", WARNING_COLOR)
            return

        item_rect = self.get_item_rect(item["position"], item.get("size", [1, 1]))
        if not self.player.rect.colliderect(item_rect):
            self.set_message("Walk closer to the item before picking it up.", WARNING_COLOR)
            return

        self.inventory.append(item["name"])
        del room["items"][index]
        self.selected_item_index = None
        self.set_message(f"You picked up the {item['name']}.")
        if item["name"] == "key":
            self.pickup_feedback_timer = 120
            self.pickup_feedback_text = "✓ Key acquired"
            self.floating_text = "+KEY"
            self.floating_text_y = self.player.rect.top
        self.player.start_pickup_animation()

    def show_inventory_message(self) -> None:
        if self.inventory:
            self.set_message("Inventory: " + ", ".join(self.inventory))
        else:
            self.set_message("Your inventory is empty.")

    def set_message(self, text: str, color: tuple[int, int, int] = TEXT_COLOR) -> None:
        self.message = text
        self.message_color = color
        self.message_timer = 180

    def draw_text_block(self, lines: List[str], x: int, y: int, font: pygame.font.Font, color: tuple[int, int, int]) -> int:
        for line in lines:
            rendered = font.render(line, True, color)
            self.screen.blit(rendered, (x, y))
            y += rendered.get_height() + 4
        return y

    def draw_tile_map(self) -> None:
        room = rooms[self.current_room]
        theme = get_room_theme(self.current_room)

        rows = len(room["tiles"])
        cols = len(room["tiles"][0])
        floor_alt = tuple(max(0, c - 14) for c in theme["floor"])

        for y, row in enumerate(room["tiles"]):
            for x, tile in enumerate(row):
                rect = tile_rect([x, y])
                if tile == 1:
                    color = theme["wall"]
                else:
                    color = floor_alt if (x + y * cols) % 4 == 0 else theme["floor"]
                pygame.draw.rect(self.screen, color, rect)
                if tile == 1:
                    pygame.draw.rect(self.screen, tuple(max(0, c - 30) for c in theme["wall"]), rect, 2)
                elif tile == 2:
                    pygame.draw.rect(self.screen, theme["floor"], rect)

        # Thick inner wall effect and rounded corners
        interior = pygame.Rect(
            MAP_X + TILE_SIZE,
            MAP_Y + TILE_SIZE,
            TILE_SIZE * (cols - 2),
            TILE_SIZE * (rows - 2),
        )
        shadow_surface = pygame.Surface((interior.width, interior.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 50), shadow_surface.get_rect(), 14, border_radius=20)
        self.screen.blit(shadow_surface, interior.topleft)
        pygame.draw.rect(self.screen, theme["border"], interior, 3, border_radius=20)

        for exit_info in room["exits"].values():
            self.draw_exit(exit_info)

    def draw_exit(self, exit_info: Dict[str, Any]) -> None:
        exit_rect = tile_rect(exit_info["position"])
        locked = self.is_exit_locked(exit_info)
        glow_color = WARNING_COLOR if locked else (100, 255, 140)
        pygame.draw.rect(self.screen, get_room_theme(self.current_room)["floor"], exit_rect)
        for border_width in (6, 4, 2):
            alpha = 80 if border_width == 2 else 40
            glow = pygame.Surface((exit_rect.width + border_width * 2, exit_rect.height + border_width * 2), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*glow_color, alpha), glow.get_rect(), border_width, border_radius=12)
            self.screen.blit(glow, (exit_rect.x - border_width, exit_rect.y - border_width))

        door_body = exit_rect.inflate(-16, -16)
        if locked:
            pygame.draw.rect(self.screen, (180, 60, 60), door_body, border_radius=12)
            padlock = pygame.Rect(door_body.centerx - 10, door_body.centery - 6, 20, 20)
            pygame.draw.rect(self.screen, (220, 220, 80), padlock, border_radius=6)
            pygame.draw.arc(self.screen, (120, 120, 120), padlock.inflate(4, 16), math.pi, 2 * math.pi, 3)
        elif self.pending_exit_info is exit_info and self.door_open_timer > 0:
            progress = 1 - self.door_open_timer / 30
            open_width = int(door_body.width * (1 - progress * 0.9))
            door_panel = pygame.Rect(door_body.left, door_body.top, open_width, door_body.height)
            pygame.draw.rect(self.screen, (160, 120, 60), door_panel, border_radius=12)
        else:
            pygame.draw.rect(self.screen, (160, 120, 60), door_body, border_radius=12)
            pygame.draw.line(self.screen, (0, 0, 0), door_body.midleft, door_body.midright, 4)

    def draw_items(self) -> None:
        room = rooms[self.current_room]
        for item in room["items"]:
            item_rect = self.get_item_rect(item["position"], item.get("size", [1, 1]))
            self.draw_item_highlight(item, item_rect)
            self.draw_item(item, item_rect)

    def draw_speech_bubble(self, rect: pygame.Rect, text: str) -> None:
        bubble = pygame.Rect(0, 0, rect.width, 24)
        bubble.midbottom = (rect.centerx, rect.top - 8)
        bubble.inflate_ip(14, 8)
        pygame.draw.rect(self.screen, (250, 250, 250), bubble, border_radius=14)
        pygame.draw.polygon(self.screen, (250, 250, 250), [
            (bubble.centerx - 8, bubble.bottom),
            (bubble.centerx + 8, bubble.bottom),
            (bubble.centerx, bubble.bottom + 10),
        ])
        text_surface = BODY_FONT.render(text, True, (20, 20, 20))
        text_rect = text_surface.get_rect(center=bubble.center)
        self.screen.blit(text_surface, text_rect)

    def draw_item_shadow(self, rect: pygame.Rect) -> None:
        shadow = pygame.Surface((rect.width + 8, rect.height // 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, SHADOW_ALPHA), shadow.get_rect())
        self.screen.blit(shadow, (rect.x - 4, rect.bottom - rect.height // 4))

    def draw_item_highlight(self, item: Dict[str, Any], rect: pygame.Rect) -> None:
        proximity_rect = rect.inflate(32, 32)
        if self.player.rect.colliderect(proximity_rect):
            pulse = int((math.sin(pygame.time.get_ticks() / 220) + 1) * 50 + 120)
            highlight = pygame.Surface((rect.width + 22, rect.height + 22), pygame.SRCALPHA)
            pygame.draw.rect(highlight, (*HIGHLIGHT_COLOR, pulse), highlight.get_rect(), 4, border_radius=16)
            self.screen.blit(highlight, (rect.x - 11, rect.y - 11))
            if self.is_item_interactable(item):
                self.draw_speech_bubble(rect, "Press E to interact")

    def draw_item(self, item: Dict[str, Any], rect: pygame.Rect) -> None:
        room = rooms[self.current_room]
        self.draw_item_shadow(rect)
        name = item["name"]
        if name == "bed":
            base = rect.inflate(-8, -14)
            pygame.draw.rect(self.screen, (180, 85, 95), base, border_radius=16)
            pillow = pygame.Rect(base.x + 6, base.y + 8, base.width - 12, 16)
            pygame.draw.rect(self.screen, (245, 235, 220), pillow, border_radius=8)
            blanket = pygame.Rect(base.x + 6, base.y + base.height // 2, base.width - 12, base.height // 2 - 6)
            pygame.draw.rect(self.screen, (220, 135, 105), blanket, border_radius=12)
        elif name == "table":
            top = pygame.Rect(rect.x + 8, rect.y + 10, rect.width - 16, 16)
            pygame.draw.rect(self.screen, (165, 105, 65), top, border_radius=8)
            leg_w = 8
            for leg_x in (rect.x + 10, rect.right - 18):
                pygame.draw.rect(self.screen, (130, 75, 40), (leg_x, rect.y + 26, leg_w, rect.height - 30), border_radius=3)
        elif name == "box":
            pygame.draw.rect(self.screen, (165, 120, 70), rect.inflate(-10, -10), border_radius=12)
            pygame.draw.rect(self.screen, (130, 90, 50), rect.inflate(-10, -10), 3, border_radius=12)
        elif name == "pressure_plate":
            plate = rect.inflate(-20, -20)
            pygame.draw.rect(self.screen, (100, 100, 110), plate, border_radius=8)
            pygame.draw.rect(self.screen, (170, 170, 90), plate.inflate(-8, -8), border_radius=6)
        elif name == "chest":
            chest = rect.inflate(-12, -14)
            pygame.draw.rect(self.screen, (125, 80, 50), chest, border_radius=12)
            if room.get("chest_open", False):
                lid = pygame.Rect(chest.x, chest.y, chest.width, chest.height // 2)
                pygame.draw.rect(self.screen, (180, 140, 100), lid, border_radius=10)
                pygame.draw.rect(self.screen, (60, 40, 20), chest.inflate(-10, -10), border_radius=8)
            else:
                pygame.draw.rect(self.screen, (110, 65, 40), chest, border_radius=12)
                lock = pygame.Rect(chest.centerx - 8, chest.centery - 8, 16, 16)
                pygame.draw.rect(self.screen, (220, 215, 120), lock, border_radius=4)
                pygame.draw.arc(self.screen, (140, 120, 80), lock.inflate(4, 10), math.pi, 2 * math.pi, 3)
        elif name == "stove":
            stove = rect.inflate(-14, -14)
            pygame.draw.rect(self.screen, (80, 80, 80), stove, border_radius=10)
            for burner_x in (stove.x + 12, stove.x + stove.width - 24):
                pygame.draw.circle(self.screen, (200, 100, 60), (burner_x, stove.y + 16), 8)
            pygame.draw.rect(self.screen, (130, 130, 130), (stove.x + 12, stove.bottom - 14, stove.width - 24, 10), border_radius=5)
        elif name == "window":
            frame = rect.inflate(-12, -18)
            pygame.draw.rect(self.screen, (220, 220, 255), frame, border_radius=8)
            pygame.draw.rect(self.screen, (100, 120, 170), frame, 3, border_radius=8)
            pygame.draw.line(self.screen, (100, 120, 170), frame.midtop, frame.midbottom, 2)
            pygame.draw.line(self.screen, (100, 120, 170), frame.midleft, frame.midright, 2)
        elif name == "plant":
            pot = pygame.Rect(rect.centerx - 12, rect.bottom - 20, 24, 16)
            pygame.draw.rect(self.screen, (135, 80, 50), pot, border_radius=6)
            for offset in (-14, 0, 14):
                pygame.draw.circle(self.screen, (100, 185, 110), (rect.centerx + offset, rect.y + 18), 12)
        elif name == "bathtub":
            tub = rect.inflate(-10, -16)
            pygame.draw.rect(self.screen, (220, 235, 245), tub, border_radius=18)
            inner = tub.inflate(-10, -10)
            pygame.draw.rect(self.screen, (180, 210, 225), inner, border_radius=14)
        elif name == "sink":
            basin = rect.inflate(-14, -20)
            pygame.draw.ellipse(self.screen, (210, 220, 230), basin)
            faucet = pygame.Rect(rect.centerx - 6, rect.y + 8, 12, 18)
            pygame.draw.rect(self.screen, (180, 180, 190), faucet, border_radius=4)
        elif name == "toilet":
            bowl = pygame.Rect(rect.centerx - 14, rect.y + 10, 28, 20)
            pygame.draw.rect(self.screen, (235, 235, 235), bowl, border_radius=10)
            tank = pygame.Rect(rect.centerx - 12, rect.y + 0, 24, 18)
            pygame.draw.rect(self.screen, (230, 230, 230), tank, border_radius=6)
        elif name == "couch":
            couch = rect.inflate(-10, -18)
            pygame.draw.rect(self.screen, (155, 95, 70), couch, border_radius=16)
            pygame.draw.rect(self.screen, (185, 130, 95), (couch.x + 6, couch.y + 6, couch.width - 12, couch.height - 12), border_radius=14)
        elif name == "TV":
            screen_body = pygame.Rect(rect.x + 6, rect.y + 8, rect.width - 12, rect.height - 18)
            pygame.draw.rect(self.screen, (35, 40, 50), screen_body, border_radius=8)
            pygame.draw.rect(self.screen, (85, 115, 160), screen_body.inflate(-10, -12), border_radius=6)
        elif name == "fridge":
            fridge = rect.inflate(-10, -10)
            pygame.draw.rect(self.screen, (225, 235, 240), fridge, border_radius=10)
            pygame.draw.line(self.screen, (180, 190, 200), fridge.midleft, fridge.midright, 4)
            pygame.draw.circle(self.screen, (160, 170, 180), (fridge.right - 12, fridge.y + 14), 4)
        elif name == "key":
            key_rect = pygame.Rect(rect.x + 10, rect.y + 18, rect.width - 20, 14)
            pygame.draw.rect(self.screen, KEY_ITEM_COLOR, key_rect, border_radius=7)
            pygame.draw.circle(self.screen, KEY_ITEM_COLOR, (key_rect.left + 8, key_rect.centery), 7)
            pygame.draw.rect(self.screen, KEY_ITEM_COLOR, (key_rect.right - 8, key_rect.centery - 4, 12, 8), border_radius=3)
        elif name == "puzzle_gate":
            gate = rect.inflate(-8, -8)
            pygame.draw.rect(self.screen, (100, 80, 200), gate, border_radius=12)
            pygame.draw.rect(self.screen, (150, 120, 255), gate, 3, border_radius=12)
            # Draw magical symbols
            pygame.draw.circle(self.screen, (200, 150, 255), gate.center, 8)
            pygame.draw.circle(self.screen, (150, 120, 255), gate.center, 6)
        elif name == "treasure_chest":
            chest = rect.inflate(-12, -14)
            pygame.draw.rect(self.screen, (184, 134, 11), chest, border_radius=12)
            pygame.draw.rect(self.screen, (218, 165, 32), chest.inflate(-6, -6), border_radius=10)
            # Gold accents
            pygame.draw.line(self.screen, (255, 215, 0), chest.topleft, chest.topright, 3)
            pygame.draw.circle(self.screen, (255, 215, 0), chest.center, 8, 3)
        elif name == "gold_pile":
            # Draw stack of gold coins
            for i in range(3):
                coin_rect = pygame.Rect(rect.x + 10 + i * 8, rect.y + 20 - i * 8, 30, 8)
                pygame.draw.ellipse(self.screen, (255, 215, 0), coin_rect)
                pygame.draw.ellipse(self.screen, (184, 134, 11), coin_rect, 2)
        elif name == "jewels":
            # Draw sparkling jewels
            colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 215, 0), (255, 0, 255)]
            for i in range(5):
                x = rect.x + 15 + (i % 3) * 18
                y = rect.y + 15 + (i // 3) * 18
                pygame.draw.polygon(self.screen, colors[i % len(colors)], [
                    (x, y - 12), (x + 12, y), (x, y + 12), (x - 12, y)
                ])
                pygame.draw.polygon(self.screen, (255, 255, 255), [
                    (x, y - 12), (x + 12, y), (x, y + 12), (x - 12, y)
                ], 1)
        else:
            pygame.draw.rect(self.screen, ITEM_COLORS.get(name, ACCENT_COLOR), rect, border_radius=12)
            pygame.draw.rect(self.screen, (50, 50, 50), rect, 2, border_radius=12)

    def draw_hud(self) -> None:
        panel_x = GAME_PANEL_WIDTH + 16
        panel_width = STATUS_PANEL_WIDTH - 32
        panel_height = SCREEN_HEIGHT - 32
        panel_rect = pygame.Rect(panel_x, 16, panel_width, panel_height)
        pygame.draw.rect(self.screen, HUD_BACKGROUND, panel_rect, border_radius=18)
        pygame.draw.rect(self.screen, ACCENT_COLOR, panel_rect, 2, border_radius=18)

        panel_title = TITLE_FONT.render("Room Status", True, ACCENT_COLOR)
        self.screen.blit(panel_title, (panel_x + 20, 28))

        quest_stages = ["Leave Bedroom", "Hangman Puzzle", "Number Puzzle", "Typing Puzzle", "Riddle Puzzle", "Treasure!"]
        quest_name = quest_stages[min(self.quest_stage, len(quest_stages) - 1)]
        stage_label = SECTION_FONT.render(f"Stage {self.quest_stage}/{len(quest_stages)}: {quest_name}", True, TEXT_COLOR)
        self.screen.blit(stage_label, (panel_x + 20, 76))

        progress_width = int((panel_width - 40) * self.quest_stage / len(quest_stages))
        progress_bg = pygame.Rect(panel_x + 20, 120, panel_width - 40, 16)
        pygame.draw.rect(self.screen, (60, 60, 80), progress_bg, border_radius=8)
        pygame.draw.rect(self.screen, ACCENT_COLOR, (progress_bg.x, progress_bg.y, progress_width, progress_bg.height), border_radius=8)

        goal_text = BODY_FONT.render("Goal: Reach the Treasure Room.", True, TEXT_COLOR)
        self.screen.blit(goal_text, (panel_x + 20, 150))

        inventory_y = 170
        inventory_title = SECTION_FONT.render("Inventory", True, ACCENT_COLOR)
        self.screen.blit(inventory_title, (panel_x + 20, inventory_y))
        inventory_y += 40

        if self.inventory:
            for item in self.inventory:
                item_text = BODY_FONT.render(f"- {item}", True, TEXT_COLOR)
                self.screen.blit(item_text, (panel_x + 24, inventory_y))
                inventory_y += 28
        else:
            empty_text = BODY_FONT.render("(empty)", True, TEXT_COLOR)
            self.screen.blit(empty_text, (panel_x + 24, inventory_y))
            inventory_y += 28

        selection_y = inventory_y + 10
        selected_title = SECTION_FONT.render("Selected Item", True, ACCENT_COLOR)
        self.screen.blit(selected_title, (panel_x + 20, selection_y))
        selection_y += 40

        if self.selected_item_index is not None and self.selected_item_index < len(rooms[self.current_room]["items"]):
            selected_item = rooms[self.current_room]["items"][self.selected_item_index]["name"]
            selected_text = BODY_FONT.render(selected_item, True, TEXT_COLOR)
        else:
            selected_text = BODY_FONT.render("(none)", True, TEXT_COLOR)
        self.screen.blit(selected_text, (panel_x + 24, selection_y))

        controls_y = selection_y + 50
        controls_title = SECTION_FONT.render("Controls", True, ACCENT_COLOR)
        self.screen.blit(controls_title, (panel_x + 20, controls_y))
        controls_y += 36
        controls = [
            "←/→ or A/D : move",
            "1-9 : inspect item",
            "P : pick up item",
            "I : inventory",
            "R : restart",
            "Esc : quit",
        ]
        for line in controls:
            control_text = BODY_FONT.render(line, True, TEXT_COLOR)
            self.screen.blit(control_text, (panel_x + 24, controls_y))
            controls_y += 26

    def draw_win_screen(self) -> None:
        """Draw the victory screen with treasure display."""
        self.draw_tile_map()
        self.draw_items()
        
        # Draw win overlay
        win_panel = pygame.Rect(50, 80, GAME_PANEL_WIDTH - 100, 500)
        overlay = pygame.Surface((win_panel.width, win_panel.height), pygame.SRCALPHA)
        overlay.fill((20, 20, 40, 220))
        self.screen.blit(overlay, win_panel.topleft)
        
        pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, win_panel, 4, border_radius=20)
        
        y_offset = win_panel.top + 40
        
        # Title
        title = TITLE_FONT.render("VICTORY!", True, HIGHLIGHT_COLOR)
        self.screen.blit(title, (win_panel.centerx - title.get_width() // 2, y_offset))
        y_offset += 70
        
        # Congratulations message
        congrats = SECTION_FONT.render("You Found The Treasure!", True, ACCENT_COLOR)
        self.screen.blit(congrats, (win_panel.centerx - congrats.get_width() // 2, y_offset))
        y_offset += 60
        
        # Treasure details
        messages = [
            "Immense riches of gold coins",
            "Glittering jewels and gems",
            "Ancient treasure chest",
            f"All puzzles completed: 5/5"
        ]
        
        for msg in messages:
            msg_surface = BODY_FONT.render(msg, True, TEXT_COLOR)
            self.screen.blit(msg_surface, (win_panel.centerx - msg_surface.get_width() // 2, y_offset))
            y_offset += 35
        
        y_offset += 20
        
        # Instructions
        instructions = [
            "Press R to play again",
            "Press Esc to quit"
        ]
        
        for instruction in instructions:
            instr_surface = BODY_FONT.render(instruction, True, ACCENT_COLOR)
            self.screen.blit(instr_surface, (win_panel.centerx - instr_surface.get_width() // 2, y_offset))
            y_offset += 35

    def draw_stickman(self, x: int, y: int, wrong_count: int) -> None:
        """Draw a stickman figure based on wrong guess count."""
        # Stickman building stages:
        # 0: nothing, 1: head, 2: body, 3: left arm, 4: right arm, 5: left leg, 6: right leg (dead)
        
        # Gallows (always drawn)
        pygame.draw.line(self.screen, (180, 140, 100), (x - 40, y + 100), (x + 40, y + 100), 4)  # base
        pygame.draw.line(self.screen, (180, 140, 100), (x - 30, y + 100), (x - 30, y - 40), 4)  # vertical pole
        pygame.draw.line(self.screen, (180, 140, 100), (x - 30, y - 40), (x + 20, y - 40), 3)  # horizontal beam
        pygame.draw.line(self.screen, (200, 50, 50), (x + 20, y - 40), (x + 20, y - 20), 2)  # rope
        
        # Head (stage 1+)
        if wrong_count >= 1:
            pygame.draw.circle(self.screen, (220, 180, 150), (x + 20, y - 10), 12)
        
        # Body (stage 2+)
        if wrong_count >= 2:
            pygame.draw.line(self.screen, (220, 180, 150), (x + 20, y + 2), (x + 20, y + 25), 2)
        
        # Left arm (stage 3+)
        if wrong_count >= 3:
            pygame.draw.line(self.screen, (220, 180, 150), (x + 20, y + 8), (x + 5, y + 15), 2)
        
        # Right arm (stage 4+)
        if wrong_count >= 4:
            pygame.draw.line(self.screen, (220, 180, 150), (x + 20, y + 8), (x + 35, y + 15), 2)
        
        # Left leg (stage 5+)
        if wrong_count >= 5:
            pygame.draw.line(self.screen, (220, 180, 150), (x + 20, y + 25), (x + 10, y + 40), 2)
        
        # Right leg / Death (stage 6+)
        if wrong_count >= 6:
            pygame.draw.line(self.screen, (220, 180, 150), (x + 20, y + 25), (x + 30, y + 40), 2)
            # X eyes for death
            pygame.draw.line(self.screen, (200, 50, 50), (x + 16, y - 14), (x + 12, y - 10), 2)
            pygame.draw.line(self.screen, (200, 50, 50), (x + 12, y - 14), (x + 16, y - 10), 2)
            pygame.draw.line(self.screen, (200, 50, 50), (x + 28, y - 14), (x + 24, y - 10), 2)
            pygame.draw.line(self.screen, (200, 50, 50), (x + 24, y - 14), (x + 28, y - 10), 2)

    def draw_puzzle_screen(self) -> None:
        """Draw the puzzle interface overlay."""
        puzzle_panel = pygame.Rect(20, 80, GAME_PANEL_WIDTH - 40, 500)
        pygame.draw.rect(self.screen, (40, 40, 60), puzzle_panel, border_radius=20)
        pygame.draw.rect(self.screen, ACCENT_COLOR, puzzle_panel, 3, border_radius=20)
        
        y_offset = puzzle_panel.top + 20
        
        if self.current_puzzle == "hangman" and self.hangman_game:
            title = TITLE_FONT.render("HANGMAN", True, ACCENT_COLOR)
            self.screen.blit(title, (puzzle_panel.centerx - title.get_width() // 2, y_offset))
            y_offset += 50
            
            # Draw stickman on the left side
            stickman_x = puzzle_panel.left + 60
            stickman_y = puzzle_panel.top + 80
            self.draw_stickman(stickman_x, stickman_y, self.hangman_game.wrong_guesses)
            
            # Display word in the center/right
            word_display = SECTION_FONT.render(self.hangman_game.get_display_word(), True, HIGHLIGHT_COLOR)
            self.screen.blit(word_display, (puzzle_panel.centerx + 60, y_offset + 40))
            
            # Display wrong counter
            wrong_text = BODY_FONT.render(f"Wrong: {self.hangman_game.wrong_guesses}/{self.hangman_game.max_wrong}", True, WARNING_COLOR)
            self.screen.blit(wrong_text, (puzzle_panel.centerx + 60, y_offset + 90))
            
            y_offset += 160
            
            # Display guessed letters with visual distinction
            correct, wrong = self.hangman_game.get_guessed_letters()
            
            # Show correct letters in green
            if correct:
                correct_text = BODY_FONT.render("Correct: ", True, TEXT_COLOR)
                correct_letters = BODY_FONT.render(" ".join(correct), True, HIGHLIGHT_COLOR)
                self.screen.blit(correct_text, (puzzle_panel.left + 30, y_offset))
                self.screen.blit(correct_letters, (puzzle_panel.left + 110, y_offset))
                y_offset += 30
            
            # Show wrong letters in red
            if wrong:
                wrong_label = BODY_FONT.render("Wrong: ", True, TEXT_COLOR)
                wrong_letters = BODY_FONT.render(" ".join(wrong), True, WARNING_COLOR)
                self.screen.blit(wrong_label, (puzzle_panel.left + 30, y_offset))
                self.screen.blit(wrong_letters, (puzzle_panel.left + 90, y_offset))
                y_offset += 30
            
            y_offset += 10
            
            # Display available letters (not yet guessed)
            remaining = self.hangman_game.get_remaining_letters()
            available_title = BODY_FONT.render("Available:", True, TEXT_COLOR)
            self.screen.blit(available_title, (puzzle_panel.left + 30, y_offset))
            y_offset += 28
            
            # Show available letters in multiple rows
            for i in range(0, len(remaining), 13):
                row = remaining[i:i+13]
                letters_text = BODY_FONT.render(" ".join(row), True, (150, 150, 200))
                self.screen.blit(letters_text, (puzzle_panel.left + 40, y_offset))
                y_offset += 25
            
            # Feedback message
            if self.hangman_game.feedback_timer > 0:
                feedback_surface = BODY_FONT.render(self.hangman_game.feedback_message, True, ACCENT_COLOR)
                self.screen.blit(feedback_surface, (puzzle_panel.centerx - feedback_surface.get_width() // 2, y_offset + 20))
                self.hangman_game.feedback_timer -= 1
        
        elif self.current_puzzle == "number" and self.number_game:
            title = TITLE_FONT.render("GUESS THE NUMBER", True, ACCENT_COLOR)
            self.screen.blit(title, (puzzle_panel.centerx - title.get_width() // 2, y_offset))
            y_offset += 60
            
            feedback = SECTION_FONT.render(self.number_game.feedback, True, TEXT_COLOR)
            self.screen.blit(feedback, (puzzle_panel.centerx - feedback.get_width() // 2, y_offset))
            y_offset += 50
            
            input_text = SECTION_FONT.render(self.puzzle_input if self.puzzle_input else "_", True, ACCENT_COLOR)
            self.screen.blit(input_text, (puzzle_panel.centerx - input_text.get_width() // 2, y_offset))
            y_offset += 50
            
            # Draw timeline of guesses
            if self.number_game.guess_history:
                timeline_title = BODY_FONT.render("Timeline:", True, TEXT_COLOR)
                self.screen.blit(timeline_title, (puzzle_panel.left + 30, y_offset))
                y_offset += 30
                
                for i, (guess, feedback_msg) in enumerate(zip(self.number_game.guess_history, self.number_game.guess_feedback)):
                    # Draw guess number and value
                    guess_text = BODY_FONT.render(f"{i+1}. {guess}", True, ACCENT_COLOR)
                    self.screen.blit(guess_text, (puzzle_panel.left + 50, y_offset))
                    
                    # Draw arrow based on feedback
                    arrow_color = TEXT_COLOR
                    if "Too low" in feedback_msg:
                        arrow_text = BODY_FONT.render(" ↑", True, arrow_color)
                    elif "Too high" in feedback_msg:
                        arrow_text = BODY_FONT.render(" ↓", True, arrow_color)
                    elif "Correct" in feedback_msg:
                        arrow_text = BODY_FONT.render(" ✓", True, SUCCESS_COLOR)
                    else:
                        arrow_text = BODY_FONT.render(" ✗", True, WARNING_COLOR)
                    
                    self.screen.blit(arrow_text, (puzzle_panel.left + 120, y_offset))
                    
                    # Draw feedback text
                    feedback_color = TEXT_COLOR
                    if "Correct" in feedback_msg:
                        feedback_color = SUCCESS_COLOR
                    elif "Game Over" in feedback_msg:
                        feedback_color = WARNING_COLOR
                    
                    feedback_display = BODY_FONT.render(feedback_msg, True, feedback_color)
                    self.screen.blit(feedback_display, (puzzle_panel.left + 150, y_offset))
                    
                    y_offset += 25
                    
                    # Prevent timeline from going off screen
                    if y_offset > puzzle_panel.bottom - 50:
                        break
        
        elif self.current_puzzle == "typing" and self.typing_game:
            title = TITLE_FONT.render("SPEED TYPING", True, ACCENT_COLOR)
            self.screen.blit(title, (puzzle_panel.centerx - title.get_width() // 2, y_offset))
            y_offset += 60
            
            level_text = SECTION_FONT.render(f"Round {self.typing_game.round}", True, TEXT_COLOR)
            self.screen.blit(level_text, (puzzle_panel.centerx - level_text.get_width() // 2, y_offset))
            y_offset += 40
            difficulty_text = BODY_FONT.render(f"Difficulty: {self.typing_game.difficulty_option}", True, TEXT_COLOR)
            self.screen.blit(difficulty_text, (puzzle_panel.left + 30, y_offset))
            y_offset += 30
            
            if self.typing_game.showing_phrase:
                showing_text = BODY_FONT.render("Memorize this phrase:", True, ACCENT_COLOR)
                self.screen.blit(showing_text, (puzzle_panel.left + 30, y_offset))
                y_offset += 40
                
                phrase_text = SECTION_FONT.render(self.typing_game.current_phrase, True, HIGHLIGHT_COLOR)
                self.screen.blit(phrase_text, (puzzle_panel.centerx - phrase_text.get_width() // 2, y_offset))
                y_offset += 60
                
                timer_text = BODY_FONT.render("Press 1=Easy, 2=Normal, 3=Hard to change difficulty.", True, TEXT_COLOR)
                self.screen.blit(timer_text, (puzzle_panel.left + 30, y_offset))
            else:
                showing_text = BODY_FONT.render("Type the phrase now and press Enter:", True, ACCENT_COLOR)
                self.screen.blit(showing_text, (puzzle_panel.left + 30, y_offset))
                y_offset += 40
                
                phrase_text = SECTION_FONT.render(self.typing_game.current_phrase, True, HIGHLIGHT_COLOR)
                self.screen.blit(phrase_text, (puzzle_panel.centerx - phrase_text.get_width() // 2, y_offset))
                y_offset += 50
                
                time_left = self.typing_game.get_time_remaining() / 1000
                timer_text = BODY_FONT.render(f"Time left: {time_left:.1f}s", True, WARNING_COLOR)
                self.screen.blit(timer_text, (puzzle_panel.left + 30, y_offset))
                y_offset += 40
                
                input_text = SECTION_FONT.render(self.puzzle_input if self.puzzle_input else "_", True, ACCENT_COLOR)
                self.screen.blit(input_text, (puzzle_panel.left + 30, y_offset))
                y_offset += 40
                
                progress = BODY_FONT.render(f"Round {self.typing_game.round}/6", True, TEXT_COLOR)
                self.screen.blit(progress, (puzzle_panel.left + 30, y_offset))
        
        elif self.current_puzzle == "riddle" and self.riddle_game:
            title = TITLE_FONT.render("RIDDLE", True, ACCENT_COLOR)
            self.screen.blit(title, (puzzle_panel.centerx - title.get_width() // 2, y_offset))
            y_offset += 60
            
            riddle_text = self.riddle_game.get_current_riddle()
            # Wrap text
            lines = []
            current_line = ""
            for word in riddle_text.split():
                test_line = current_line + (" " if current_line else "") + word
                if len(test_line) > 40:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
                else:
                    current_line = test_line
            if current_line:
                lines.append(current_line)
            
            for line in lines[:3]:
                line_surface = BODY_FONT.render(line, True, TEXT_COLOR)
                self.screen.blit(line_surface, (puzzle_panel.left + 30, y_offset))
                y_offset += 30
            
            y_offset += 20
            input_text = SECTION_FONT.render(self.puzzle_input if self.puzzle_input else "_", True, ACCENT_COLOR)
            self.screen.blit(input_text, (puzzle_panel.centerx - input_text.get_width() // 2, y_offset))
            y_offset += 50
            
            progress_text = BODY_FONT.render(f"Riddle {self.riddle_game.current_riddle_index + 1}/5", True, TEXT_COLOR)
            self.screen.blit(progress_text, (puzzle_panel.left + 30, y_offset))

    def draw(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        panel_rect = pygame.Rect(8, 8, GAME_PANEL_WIDTH - 16, SCREEN_HEIGHT - 16)
        pygame.draw.rect(self.screen, HUD_BACKGROUND, panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, ACCENT_COLOR, panel_rect, 3, border_radius=20)

        if self.win_screen:
            self.draw_win_screen()
        elif self.puzzle_active:
            self.draw_puzzle_screen()
        else:
            self.draw_tile_map()
            self.draw_items()
            self.player.draw(self.screen)

        if self.message_timer > 0:
            message_surface = BODY_FONT.render(self.message, True, self.message_color)
            self.screen.blit(message_surface, (24, SCREEN_HEIGHT - 54))
            self.message_timer -= 1

        if self.floating_text and self.pickup_feedback_timer > 0:
            floating_surface = SECTION_FONT.render(self.floating_text, True, KEY_ITEM_COLOR)
            floating_rect = floating_surface.get_rect(center=(self.player.rect.centerx, self.floating_text_y))
            self.screen.blit(floating_surface, floating_rect)
            self.floating_text_y -= 0.8

        if self.pickup_feedback_timer > 0:
            overlay = pygame.Surface((GAME_PANEL_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 10, 20, 120))
            self.screen.blit(overlay, (0, 0))
            feedback = TITLE_FONT.render(self.pickup_feedback_text, True, KEY_ITEM_COLOR)
            feedback_rect = feedback.get_rect(center=(GAME_PANEL_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(feedback, feedback_rect)
            self.pickup_feedback_timer -= 1
            if self.pickup_feedback_timer == 0:
                self.floating_text = ""

        if self.start_screen:
            overlay = pygame.Surface((GAME_PANEL_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 10, 20, 200))
            self.screen.blit(overlay, (0, 0))
            title_text = TITLE_FONT.render("You wake up in your bedroom.", True, TEXT_COLOR)
            prompt_text = BODY_FONT.render("Something feels wrong. Find your way to the kitchen...", True, TEXT_COLOR)
            continue_text = BODY_FONT.render("Press SPACE to continue", True, ACCENT_COLOR)
            self.screen.blit(title_text, title_text.get_rect(center=(GAME_PANEL_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)))
            self.screen.blit(prompt_text, prompt_text.get_rect(center=(GAME_PANEL_WIDTH // 2, SCREEN_HEIGHT // 2)))
            self.screen.blit(continue_text, continue_text.get_rect(center=(GAME_PANEL_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)))

        if self.stage_message_text and self.stage_message_timer > 0:
            overlay = pygame.Surface((GAME_PANEL_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 10, 20, 180))
            self.screen.blit(overlay, (0, 0))
            stage_text = TITLE_FONT.render(self.stage_message_text, True, ACCENT_COLOR)
            self.screen.blit(stage_text, stage_text.get_rect(center=(GAME_PANEL_WIDTH // 2, SCREEN_HEIGHT // 2)))

        if self.transition_timer > 0 and self.transition_room_name:
            overlay = pygame.Surface((GAME_PANEL_WIDTH - 32, SCREEN_HEIGHT - 32), pygame.SRCALPHA)
            overlay.fill((20, 20, 30, 180))
            self.screen.blit(overlay, (16, 16))
            title_text = TITLE_FONT.render(self.transition_room_name, True, TEXT_COLOR)
            desc_text = BODY_FONT.render("Entering new room...", True, ACCENT_COLOR)
            title_rect = title_text.get_rect(center=(GAME_PANEL_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            desc_rect = desc_text.get_rect(center=(GAME_PANEL_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            self.screen.blit(title_text, title_rect)
            self.screen.blit(desc_text, desc_rect)

        self.draw_hud()
        pygame.display.flip()



def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
