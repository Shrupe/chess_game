import chessEngine
import pygame
import sys

# Constants
WIDTH, HEIGHT = 512, 512
ROWS, COLS = 8, 8
SQ_SIZE = WIDTH // COLS
IMAGES = {}

# Initialize Pygame
pygame.init()

# Highlighting selected sq and piece
def highlight_sq(screen, GS, validMoves, selectedSq):
    if selectedSq != ():
        row, col = selectedSq
        # if GS.board[row][col][0] == ("w" if GS.whiteTurn else "b") can be used instead of below line
        if (GS.board[row][col][0] == "w" and GS.whiteTurn) or (GS.board[row][col][0] == "b" and not GS.whiteTurn):
            # highlight selected sq
            surface = pygame.Surface((SQ_SIZE, SQ_SIZE))
            surface.set_alpha(100) #0-255 (transparent-opaque)
            surface.fill(pygame.Color("darkgreen"))
            screen.blit(surface, (col*SQ_SIZE, row*SQ_SIZE))
            # highlight valid moves
            surface.fill(pygame.Color("green"))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(surface, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

# Load Images
def load_images():
    pieces = ["bP", "bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR", "wP", "wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load("assets/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

# Draw Chess Board
def draw_board(screen):
    colors = [pygame.Color("white"), pygame.Color("darkgray")]
    for row in range(ROWS):
        for col in range(COLS):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

# Draw Chess Pieces
def draw_pieces(screen, board):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece != "--": 
                screen.blit(IMAGES[piece], pygame.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def display_game_over_text(screen, textToDisplay):
    font = pygame.font.SysFont("arial", 36, bold=True, italic=False)
    text = font.render(textToDisplay, 0, pygame.Color("black"))
    location = pygame.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2)
    screen.blit(text, location)

def draw_game(screen, GS, validMoves, selectedSq):
    draw_board(screen)
    highlight_sq(screen, GS, validMoves, selectedSq)
    draw_pieces(screen, GS.board)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Board")
    clock = pygame.time.Clock()

    load_images()

    GS = chessEngine.GameState()
    MF = chessEngine.MoveFunctions()

    running = True
    selectedSq = () # keeps track of the last click of the user (tuple: (row, column))
    clicks = [] # keeps track of player clicks (selectedSq) for the move (two tuples: [(x1, y1), (x1, y2)])
    moveMade = False
    gameOver = False
    validMoves = GS.get_valid_moves(MF)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Mouse handlers
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not gameOver:
                    pos = pygame.mouse.get_pos() # x and y position of mouse
                    col = pos[0] // SQ_SIZE
                    row = pos[1] // SQ_SIZE
                    if selectedSq == (row, col): # if user clicks the same square
                        selectedSq = () # deselect 
                        clicks = [] # clear player clicks
                    else:
                        selectedSq = (row, col)
                        clicks.append(selectedSq)
                    if len(clicks) == 1 and GS.board[clicks[0][0]][clicks[0][1]] == "--": # for second click make the move
                        selectedSq = () # deselect 
                        clicks = [] # clear player clicks
                    elif len(clicks) == 2:
                        MI = chessEngine.MoveInfo(clicks[0], clicks[1], GS.board)
                        for i in range(len(validMoves)):
                            if MI == validMoves[i]:
                                MF.make_move(GS, validMoves[i])
                                MI.print_notation()
                                moveMade = True
                                selectedSq = () # reset user clicks
                                clicks = []
                        if not moveMade:
                            clicks = [selectedSq] # clear player clicks
            # key handlers
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u: # undo move when pressed u key
                    if gameOver:
                        gameOver = False
                    MF.undo_move(GS)
                    print("*last move undone*")
                    moveMade = True
                if event.type == pygame.K_r: # reset game when pressed r key
                    if gameOver:
                        gameOver = False
                    GS = chessEngine.GameState()
                    MF = chessEngine.MoveFunctions()
                    validMoves = GS.get_valid_moves(MF)
                    selectedSq = ()
                    clicks = []
                    moveMade = False
        if moveMade:
            moveMade = False
            validMoves = GS.get_valid_moves(MF)

        draw_game(screen, GS, validMoves, selectedSq)

        if GS.wCheckmated:
            gameOver = True
            textToDisplay = "Black Checkmated White"
        elif GS.bCheckmated:
            gameOver = True
            textToDisplay = "White Checkmated Black"
        elif GS.stalemate:
            gameOver = True
            textToDisplay = "Stalemate"
        if gameOver:
            display_game_over_text(screen, textToDisplay)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()