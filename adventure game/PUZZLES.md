# Adventure Game - Puzzle System

## Overview
Your adventure game now features an enhanced puzzle-based progression system with 5 distinct puzzle types across 6 rooms. Each puzzle must be completed to unlock the door to the next room.

## Game Progression

### Stage 1: Bedroom (No Puzzle)
- **Description**: Starting area
- **Task**: Leave the bedroom to begin your adventure
- **Exit**: East door to Bathroom (unlocked)

### Stage 2: Bathroom - HANGMAN PUZZLE
- **Description**: A mysterious puzzle gate blocks the eastern exit
- **How to Play**:
  1. Approach the puzzle gate and press **E** to interact
  2. A Hangman word-guessing game begins
  3. Guess letters by pressing **A-Z** keys
  4. Available letters are displayed on screen
  5. You have 6 wrong guesses allowed
  6. Guess the word correctly to unlock the door

- **Controls**:
  - **A-Z**: Guess a letter
  - **Press E**: Interact with puzzle gate to start

### Stage 3: Living Room - NUMBER GUESSING PUZZLE
- **Description**: Unlock the secret by guessing the number
- **How to Play**:
  1. Approach the puzzle gate and press **E**
  2. A number between 1-100 is hidden
  3. Type your guess (numbers only)
  4. Press **Enter** to submit your guess
  5. You have 7 attempts to find the number
  6. Get feedback: "Too high" or "Too low"
  7. Guess correctly within the attempts to proceed

- **Controls**:
  - **0-9**: Type your guess
  - **Backspace**: Delete a number
  - **Enter**: Submit your guess
  - **Press E**: Interact with puzzle gate to start

### Stage 4: Kitchen - RHYTHM GAME (Timing Puzzle)
- **Description**: A rhythmic puzzle that tests your timing
- **How to Play**:
  1. Approach the puzzle gate and press **E**
  2. Watch the pattern of keys displayed
  3. After the sequence shows, you must repeat it
  4. Press the keys in the correct order: **Q, W, E, R**
  5. Complete 5 levels successfully to unlock the door
  6. Each level adds one more key to remember

- **Controls**:
  - **Q, W, E, R**: Repeat the sequence
  - The game shows you the pattern first, then you repeat it
  - Progress increases with each successfully completed level

### Stage 5: Dungeon - RIDDLE PUZZLE
- **Description**: Ancient riddles guard the treasure
- **How to Play**:
  1. Approach the puzzle gate and press **E**
  2. A riddle is displayed on screen
  3. Type your answer and press **Enter**
  4. You have 3 attempts per riddle
  5. There are 5 riddles total
  6. Solve at least 3 out of 5 riddles to unlock the treasure

- **Sample Riddles**:
  - "I have a head and a tail but no body. What am I?" → COIN
  - "The more you take, the more you leave behind. What am I?" → FOOTSTEPS
  - "I am taken from a mine and shut up in a wooden case, yet no one ever made me. What am I?" → PENCIL

- **Controls**:
  - **Type**: Enter your answer (A-Z, spaces allowed)
  - **Backspace**: Delete characters
  - **Enter**: Submit your answer
  - **Press E**: Interact with puzzle gate to start

### Stage 6: Treasure Room - VICTORY!
- **Description**: The final room containing the treasure
- **Features**:
  - Massive treasure chest overflowing with gold and jewels
  - Piles of shimmering gold coins
  - Glittering precious gems of every color
  - Golden floor and walls (special treasure room theme)

## Game Controls

### Navigation
- **←/→ or A/D**: Move left/right
- **↑/↓ or W/S**: Move up/down

### General
- **E**: Interact (activate puzzle gates, examine items)
- **P**: Pick up item
- **I**: Open inventory
- **R**: Restart game
- **Esc**: Quit game

### During Puzzles
Different controls apply based on the active puzzle:
- **Hangman**: A-Z keys to guess letters
- **Number Game**: 0-9 and Enter to submit
- **Rhythm Game**: Q, W, E, R to repeat sequences
- **Riddle**: Type answers and press Enter

## Game Features

### Puzzle System
- Each room has a unique puzzle gate (glowing magical object)
- Puzzles automatically unlock the exit door when completed successfully
- Visual feedback shows puzzle status and progress
- Hints provided for each puzzle type

### Room Themes
Each room has a unique visual theme:
- **Bedroom**: Warm wood tones
- **Bathroom**: Cool blue tones
- **Living Room**: Brown earth tones
- **Kitchen**: Gray/silver tones
- **Dungeon**: Dark cool tones
- **Treasure Room**: Golden tones (treasure theme)

### HUD (Head-Up Display)
- **Room Status Panel** (right side):
  - Current stage progress (e.g., "Stage 3/6")
  - Progress bar showing completion percentage
  - Current quest objective
  - Inventory display
  - Controls reference

## Tips for Solving Puzzles

### Hangman Tips
- Common words are used (9 letters or less)
- Start with common vowels (A, E) and consonants (R, S, T, N)
- Watch the available letters to plan your strategy

### Number Guessing Tips
- Use binary search logic (guess middle value)
- Pay attention to "too high" and "too low" feedback
- 7 attempts should be enough with logical guessing

### Rhythm Game Tips
- Watch the pattern carefully before repeating
- The pattern grows by one key with each level
- Press keys in exact order shown
- Take your time - there's no time limit

### Riddle Tips
- Read each riddle carefully
- Think of literal and metaphorical meanings
- You have 3 attempts per riddle
- Use common riddle logic (wordplay, metaphors)

## Game Flow Summary

```
Bedroom (No puzzle) 
    → Bathroom (Hangman)
        → Living Room (Number Guessing)
            → Kitchen (Rhythm Game)
                → Dungeon (Riddle)
                    → Treasure Room (Victory!)
```

Each completed puzzle automatically opens the door to the next room.

## Technical Details

### Save State
Game progress is tracked during play:
- Current room
- Inventory items collected
- Completed puzzle stages
- All game state resets when pressing **R** to restart

### Win Condition
Game is won when the player reaches the **Treasure Room** successfully.

### Restart
Press **R** at any time to restart the entire game from the Bedroom with all progress reset.

Enjoy the adventure and good luck solving the puzzles!
