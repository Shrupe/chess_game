import numpy as np
ROWS, COLS = 8, 8

class GameState():
    def __init__(self):
        self.board = np.array([
                                ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
                                ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
                                ["--", "--", "--", "--", "--", "--", "--", "--"],
                                ["--", "--", "--", "--", "--", "--", "--", "--"],
                                ["--", "--", "--", "--", "--", "--", "--", "--"],
                                ["--", "--", "--", "--", "--", "--", "--", "--"],
                                ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
                                ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
                            ])
        self.whiteTurn = True
        self.moveInfoLog = [] # [MoveInfo1, MoveInfo2, ...]
        self.enpassantCoord = () # (tuple) coordinates for the enpassant move
        self.wKLocation = (7, 4)
        self.bKLocation = (0, 4)
        self.wInCheck = False
        self.bInCheck = False
        self.wCheckmated = False # black win
        self.bCheckmated = False # white win
        self.stalemate = False # tie
        self.currCastlingInfo = CastlingInfo(True, True, True, True)
        self.castlingInfoLog = [CastlingInfo(self.currCastlingInfo.wShortC, self.currCastlingInfo.wLongC, #create a copy of current castling infos
                                            self.currCastlingInfo.bShortC, self.currCastlingInfo.bLongC)]
    
    def check(self):
        if self.whiteTurn:
            self.wInCheck = self.sq_under_threat(self.wKLocation[0], self.wKLocation[1])
            return self.sq_under_threat(self.wKLocation[0], self.wKLocation[1])
        else:
            self.bInCheck = self.sq_under_threat(self.bKLocation[0], self.bKLocation[1])
            return self.sq_under_threat(self.bKLocation[0], self.bKLocation[1])
    
    def sq_under_threat(self, r , c):
        self.whiteTurn = not self.whiteTurn
        oppMoves = self.get_all_moves()
        self.whiteTurn = not self.whiteTurn
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def get_valid_moves(self, MF): ## GS kaldirilip yerine self kullanilabilir ??
        """
        -generate all possible moves and make them
        -for all made moves, generate all the oppenents moves and check if your king is in check 
        -if it is not a valid move
        """
        #create a copy of current castling infos
        tempCurrCastlingInfo = CastlingInfo(self.currCastlingInfo.wShortC, self.currCastlingInfo.wLongC, 
                                            self.currCastlingInfo.bShortC, self.currCastlingInfo.bLongC)
        tempEnpassantCoord = self.enpassantCoord # creating a copy of enpassantCoord     
        allMoves = self.get_all_moves()
        validMoves = []
        # castling (doing that in get_king_moves func. causing RecursionError)
        if self.whiteTurn:
            self.get_castling_moves(self.wKLocation[0], self.wKLocation[1], allMoves)
        else:
            self.get_castling_moves(self.bKLocation[0], self.bKLocation[1], allMoves)
        for i in range(len(allMoves)-1, -1, -1):
            MF.make_move(self, allMoves[i])
            self.whiteTurn = not self.whiteTurn
            if not self.check():
                validMoves.append(allMoves[i])
            self.whiteTurn = not self.whiteTurn
            MF.undo_move(self)
        # checkmate and stalemate
        if len(validMoves) == 0:
            if self.whiteTurn and self.check():
                self.wCheckmated = True
                print("Black Win")
            elif not self.whiteTurn and self.check():
                self.bCheckmated = True
                print("White Win")
            else:
                self.stalemate = True
                print("Tie")
        else: ### burasi kaldirilabilir ??
            self.wCheckmated = False
            self.bCheckmated = False
            self.stalemate = False
        self.enpassantCoord = tempEnpassantCoord
        self.currCastlingInfo = tempCurrCastlingInfo
        return validMoves
    
    def get_all_moves(self):
        allMoves = []
        pieceTypeToFunc = {"P": self.get_pawn_moves, "R": self.get_rook_moves, "N": self.get_knight_moves, 
                           "B": self.get_bishop_moves, "Q": self.get_queen_moves, "K": self.get_king_moves}
        for r in range(ROWS):
            for c in range(COLS):
                if self.board[r][c][0] == "w":
                    pieceColor = True # whiteTurn True
                else:
                    pieceColor = False
                pieceType = self.board[r][c][1]
                if pieceColor == self.whiteTurn and pieceType != "-":
                    pieceTypeToFunc[pieceType](r, c, allMoves)
        return allMoves

    def get_pawn_moves(self, r, c, allMoves):
        pieceColor = self.board[r][c][0]
        if self.whiteTurn:
            direction = -1
        else:
            direction = 1
        # 1 forward 
        nextRow = r + direction
        if 0 <= nextRow < ROWS and self.board[nextRow][c] == "--":
            allMoves.append(MoveInfo((r, c), (nextRow, c), self.board))
            # 2 forward
            if ((self.whiteTurn and r == 6) or ((not self.whiteTurn) and r == 1)):
                nextRow += direction
                if (0 <= nextRow < ROWS) and (self.board[nextRow][c] == "--"):
                    allMoves.append(MoveInfo((r, c), (nextRow, c), self.board))
        # diagonal capture
        for diagonal in [1, -1]:
            nextRow = r + direction
            nextCol = c + diagonal
            if 0 <= nextRow < ROWS and 0 <= nextCol < COLS:
                targetSq = self.board[nextRow][nextCol]
                if targetSq != "--":
                    targetColor = targetSq[0]
                    if pieceColor != targetColor:
                        allMoves.append(MoveInfo((r, c), (nextRow, nextCol), self.board))
                elif (nextRow, nextCol) == self.enpassantCoord:
                    allMoves.append(MoveInfo((r, c), (nextRow, nextCol), self.board, enpassantMove=True))

    def get_rook_moves(self, r, c, allMoves):
        pieceColor = self.board[r][c][0]
        directions = [(1, 0), (-1, 0), (0, -1), (0, 1)] # up down left right
        for direction in directions:
            for step in range(1, ROWS):
                nextRow = r + (step * direction[0])
                nextCol = c + (step * direction[1])
                if 0 <= nextRow < ROWS and 0 <= nextCol < COLS: 
                    targetSq = self.board[nextRow][nextCol]
                    if targetSq == "--": # is target sq empty
                        allMoves.append(MoveInfo((r, c), (nextRow, nextCol), self.board))
                    else:
                        targetColor = targetSq[0]
                        if pieceColor != targetColor: # is target piece diff color
                            allMoves.append(MoveInfo((r, c), (nextRow, nextCol), self.board))
                        break # piece on the way
                else:
                    break # out of board

    def get_knight_moves(self, r, c, allMoves):
        pieceColor = self.board[r][c][0]
        knightMoves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

        for move in knightMoves:
            nextRow = r + move[0]
            nextCol = c + move[1]

            if 0 <= nextRow < ROWS and 0 <= nextCol < COLS:
                targetSq = self.board[nextRow][nextCol]
                if targetSq == "--":
                    allMoves.append(MoveInfo((r, c), (nextRow, nextCol), self.board))
                else:
                    targetColor = targetSq[0]
                    if pieceColor != targetColor:
                        allMoves.append(MoveInfo((r, c), (nextRow, nextCol), self.board))
    
    def get_bishop_moves(self, r, c, allMoves):
        pieceColor = self.board[r][c][0]
        directions = [(1, 1), (-1, -1), (1, -1), (-1, 1)] 

        for direction in directions:
            for step in range(1, ROWS):
                nextRow = r + step * direction[0]
                nextCol = c + step * direction[1]

                if 0 <= nextRow < ROWS and 0 <= nextCol < COLS:
                    targetSq = self.board[nextRow][nextCol]
                    if targetSq == "--": # is target sq empty
                        allMoves.append(MoveInfo((r, c), (nextRow, nextCol), self.board))
                    else:
                        targetColor = targetSq[0]
                        if pieceColor != targetColor: # is target piece diff color
                            allMoves.append(MoveInfo((r, c), (nextRow, nextCol), self.board))
                        break # piece on the way
                else:
                    break  # out of the board
    
    def get_queen_moves(self, r, c, allMoves):
        self.get_rook_moves(r, c, allMoves)
        self.get_bishop_moves(r, c, allMoves)

    def get_king_moves(self, r, c, allMoves):
        pieceColor = self.board[r][c][0]
        king_moves = [(1, 0), (-1, 0), (0, 1), (0, -1), 
                      (1, 1), (-1, -1), (1, -1), (-1, 1)]
        for move in king_moves:
            nextRow = r + move[0]
            nextCol = c + move[1]
            if 0 <= nextRow < ROWS and 0 <= nextCol < COLS:
                targetSq = self.board[nextRow][nextCol]
                """
                # instead of below if-else statement
                if targetSq[0] != pieceColor: 
                    allMoves.append(MoveInfo((r, c), (nextRow, nextCol), self.board))
                """
                if targetSq == "--": 
                    allMoves.append(MoveInfo((r, c), (nextRow, nextCol), self.board))
                else:
                    targetColor = targetSq[0]
                    if pieceColor != targetColor:
                        allMoves.append(MoveInfo((r, c), (nextRow, nextCol), self.board))

    def get_castling_moves(self, r, c, allMoves):
        if self.sq_under_threat(r, c): # if it's check can't do castling
            return 
        if (self.whiteTurn and self.currCastlingInfo.wShortC) or \
            (not self.whiteTurn and self.currCastlingInfo.bShortC):
            self.get_shortC_moves(r, c, allMoves)
        if (self.whiteTurn and self.currCastlingInfo.wLongC) or \
            (not self.whiteTurn and self.currCastlingInfo.bLongC):
            self.get_longC_moves(r, c, allMoves)
    
    def get_shortC_moves(self, r, c, allMoves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.sq_under_threat(r, c+1) and not self.sq_under_threat(r, c+2):
                allMoves.append(MoveInfo((r, c), (r, c+2), self.board, castlingMove=True))

    def get_longC_moves(self, r, c, allMoves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--":
            if not self.sq_under_threat(r, c-1) and not self.sq_under_threat(r, c-2):
                allMoves.append(MoveInfo((r, c), (r, c-2), self.board, castlingMove=True))


class CastlingInfo():
    def __init__(self, wShortC, wLongC, bShortC, bLongC): # wShortC: white short castling
        self.wShortC = wShortC
        self.wLongC = wLongC
        self.bShortC = bShortC
        self.bLongC = bLongC

class MoveFunctions(): 
    def make_move(self, GS, MI):
        GS.board[MI.startRow][MI.startCol] = "--"
        GS.board[MI.endRow][MI.endCol] = MI.movedPiece
        GS.moveInfoLog.append(MI)
        GS.whiteTurn = not GS.whiteTurn
        # update kings locations
        if MI.movedPiece == "wK":
            GS.wKLocation = (MI.endRow, MI.endCol)
        elif MI.movedPiece == "bK":
            GS.bKLocation = (MI.endRow, MI.endCol)
        # pawn promotion
        if MI.pawnPromotion:
            GS.board[MI.endRow][MI.endCol] = MI.movedPiece[0] + "Q"
        # enpassant
        if MI.enpassantMove:
            GS.board[MI.startRow][MI.endCol] = "--"
        # update enpassantCoord
        if MI.movedPiece[1] == "P" and abs(MI.startRow - MI.endRow) == 2: # only when pawn goes 2 forward
            GS.enpassantCoord = ((MI.startRow + MI.endRow)//2, MI.startCol)
        else:
            GS.enpassantCoord = ()
        # castling
        if MI.castlingMove:
            if MI.endCol - MI.startCol == 2: # short castling
                GS.board[MI.endRow][MI.endCol-1] = GS.board[MI.endRow][MI.endCol+1] # create a copy of the rook
                GS.board[MI.endRow][MI.endCol+1] = "--" # delete old rook
            else: # long castling
                GS.board[MI.endRow][MI.endCol+1] = GS.board[MI.endRow][MI.endCol-2] # create a copy of the rook
                GS.board[MI.endRow][MI.endCol-2] = "--" # delete old rook
        # update currCastlingInfo
        if MI.movedPiece == "wK":
            GS.currCastlingInfo.wShortC = False
            GS.currCastlingInfo.wLongC = False
        elif MI.movedPiece == "bK":
            GS.currCastlingInfo.bShortC = False
            GS.currCastlingInfo.bLongC = False
        elif MI.movedPiece == "wR":
            if MI.startRow == 7:
                if MI.startCol == 7:
                    GS.currCastlingInfo.wShortC = False
                elif MI.startCol == 0:
                    GS.currCastlingInfo.wLongC = False
        elif MI.movedPiece == "bR":
            if MI.startRow == 0:
                if MI.startCol == 7:
                    GS.currCastlingInfo.bShortC = False
                elif MI.startCol == 0:
                    GS.currCastlingInfo.bLongC = False
        GS.castlingInfoLog.append(CastlingInfo(GS.currCastlingInfo.wShortC, GS.currCastlingInfo.wLongC,
                                               GS.currCastlingInfo.bShortC, GS.currCastlingInfo.bLongC))
        
    def undo_move(self, GS):
        if len(GS.moveInfoLog) != 0:
            MI = GS.moveInfoLog.pop()
            GS.board[MI.startRow][MI.startCol] = MI.movedPiece
            GS.board[MI.endRow][MI.endCol] = MI.capturedPiece
            GS.whiteTurn = not GS.whiteTurn
            # update kings locations
            if MI.movedPiece == "wK":
                GS.wKLocation = (MI.startRow, MI.startCol)
            elif MI.movedPiece == "bK":
                GS.bKLocation = (MI.startRow, MI.startCol)
            # undo enpassant move
            if MI.enpassantMove:
                GS.board[MI.endRow][MI.endCol] = "--"
                GS.board[MI.startRow][MI.endCol] = MI.capturedPiece
                GS.enpassantCoord = (MI.endRow, MI.endCol) # add the undone enpassant move back to enpassantCoord
            # when undo double forward pawn move reset enpassantCoord
            if MI.movedPiece[1] == "P" and abs(MI.startRow - MI.endRow) == 2:
                GS.enpassantCoord = ()
            # undo castling rights
            GS.castlingInfoLog.pop() # remove the new castling rights from the undone move
            castlingInfo = GS.castlingInfoLog[-1]
            GS.currCastlingInfo.wShortC = castlingInfo.wShortC # set the current castling rights to last one in the list
            GS.currCastlingInfo.wLongC = castlingInfo.wLongC 
            GS.currCastlingInfo.bShortC = castlingInfo.bShortC 
            GS.currCastlingInfo.bLongC = castlingInfo.bLongC 
            # undo castling move
            if MI.castlingMove:
                if MI.endCol - MI.startCol == 2: # short castling
                    GS.board[MI.endRow][MI.endCol+1] = GS.board[MI.endRow][MI.endCol-1]
                    GS.board[MI.endRow][MI.endCol-1] = "--"
                else: # long castling
                    GS.board[MI.endRow][MI.endCol-2] = GS.board[MI.endRow][MI.endCol+1]
                    GS.board[MI.endRow][MI.endCol+1] = "--"
             
class MoveInfo():
    def __init__(self, startSq, endSq, board, enpassantMove = False, castlingMove=False): # enpassantCoord degiskenine default value vermek onu optional attribute yapti
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.movedPiece = board[self.startRow][self.startCol]
        self.mPieceColor = self.movedPiece[0]
        self.mPieceType = self.movedPiece[1]
        self.capturedPiece = board[self.endRow][self.endCol]
        # bu pawnPromo olayini get_pawn_moves a tasi 81035 (opsiyonel class degiskeni??)
        self.pawnPromotion = False
        if self.mPieceType == "P":
            if self.endRow == 0 or self.endRow == 7:
                self.pawnPromotion = True
        self.enpassantMove = enpassantMove
        if self.enpassantMove:
            if self.movedPiece == "wP":
                self.capturedPiece = "bP"
            elif self.movedPiece == "bP":
                self.capturedPiece = "wP" 
        # castling
        self.castlingMove = castlingMove
        self.moveID = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol

    def get_notation(self):
        rowsToRanks = {0: "8", 1: "7", 2: "6", 3: "5",
                       4: "4", 5: "3", 6: "2", 7: "1"}
        colsToFiles = {0: "a", 1: "b", 2: "c", 3: "d",
                       4: "e", 5: "f", 6: "g", 7: "h"}
        
        notation = colsToFiles[self.startCol]+rowsToRanks[self.startRow]+\
        colsToFiles[self.endCol]+rowsToRanks[self.endRow]
        return notation

    def print_notation(self):
        print(self.get_notation())   

    def __eq__(self, other): # overriding equals method for "if MI == validMoves[i]" statement comparison of classes
        if isinstance(other, MoveInfo):
            return self.moveID == other.moveID
        return False
    