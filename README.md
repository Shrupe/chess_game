

# ♟️ Python Chess Game with Engine Logic and GUI

A fully playable chess game implemented in **Python** using **Pygame** for the GUI and a custom-built **chess engine** that handles piece movement, game rules, and advanced mechanics like **en passant**, **castling**, **check**, **checkmate**, and **stalemate** detection.

---

## 📂 Project Structure

.
├── assets/ # Contains chess piece images (.png) named like bP.png, wK.png, etc.
├── chessEngine.py # Core game logic (board, rules, movement validation)
├── chessMain.py # Pygame-based GUI and game loop
└── README.md


---

## ▶️ How to Run

1. **Install Dependencies**
   ```bash
   pip install pygame numpy

    Ensure Assets Are Present

        The assets/ folder must contain images for all pieces (e.g., wP.png, bK.png, etc.).

        Each image should be a square and named in the format [color][piece].png.

    Run the Game

    python chessMain.py

🎮 Controls & Features

    Mouse Left Click: Select and move pieces.

    U Key: Undo the last move.

    R Key: Reset the game.

    Highlights:

        Selected piece and its valid moves.

    Game states:

        Check

        Checkmate

        Stalemate

    Special rules:

        Castling (both long and short)

        En Passant

        Pawn Promotion (to Queen by default)

🧠 Chess Engine Details (chessEngine.py)

The chess engine is implemented via multiple classes:
GameState

    Stores the current state of the board and player turn.

    Detects check, checkmate, and stalemate.

    Calculates all legal moves for the current turn.

MoveInfo

    Represents a move: starting and ending squares, captured piece, promotion, etc.

    Can return chess notation (e.g., e2e4).

MoveFunctions

    Handles make_move() and undo_move() logic.

    Updates board, en passant, castling rights, and king positions.

CastlingInfo

    Tracks the current castling rights for both sides.

🖼️ GUI Details (chessMain.py)

    Built with Pygame.

    Handles rendering board and pieces.

    Processes mouse clicks and key presses.

    Draws:

        The chessboard

        Piece images

        Valid move highlights

        Game-over messages

✅ TODO / Possible Improvements

    Support for move timers or multiplayer over network.

    AI opponent using Minimax or Neural Networks.
