"""Contains the code for the Torpedo variant"""

from chess import standard as std


class Pawn(std.Pawn):
    """a Pawn

    Args:
        color (int): color of the piece
        position (tuple[int, int]): Position of the piece in a numeric form.
    """

    def move(self, move:str) -> None:
        """A pawn move"""
        match self.can_move(move):

            case (True, std.Piece() as piece, True):
                del std.Piece.board[self.pos]
                std.Piece.board.pieces.remove(piece)
                del std.Piece.board[piece.pos]
                std.Piece.board.pieces.remove(self)
                match move[2]:
                    case "q":
                        p = std.Queen(self.color, (ord(move[0])-97, int(move[1])-1))
                    case "r":
                        p = std.Rook(self.color, (ord(move[0])-97, int(move[1])-1))
                    case "n":
                        p = std.Knight(self.color, (ord(move[0])-97, int(move[1])-1))
                    case "b":
                        p = std.Bishop(self.color, (ord(move[0])-97, int(move[1])-1))
                std.Piece.board[move].piece = p
                std.Piece.board.pieces.append(p)
                del self

            case (True, std.Piece() as piece, False):
                del std.Piece.board[self.pos]
                del std.Piece.board[piece.pos]
                self.pos = move
                std.Piece.board[self.pos].piece = self
                std.Piece.board.pieces.remove(piece)

            case (True, True):
                del std.Piece.board[self.pos]
                std.Piece.board.pieces.remove(self)
                match move[2]:
                    case "q":
                        p = std.Queen(self.color, (ord(move[0])-97, int(move[1])-1))
                    case "r":
                        p = std.Rook(self.color, (ord(move[0])-97, int(move[1])-1))
                    case "n":
                        p = std.Knight(self.color, (ord(move[0])-97, int(move[1])-1))
                    case "b":
                        p = std.Bishop(self.color, (ord(move[0])-97, int(move[1])-1))
                std.Piece.board[move].piece = p
                std.Piece.board.pieces.append(p)
                del self

            case (True, False):
                del std.Piece.board[self.pos]
                self.pos = move
                std.Piece.board[move].piece = self

            case(True, str() as y, False):
                del std.Piece.board[self.pos]
                self.pos = move
                std.Piece.board[self.pos].piece = self
                std.Piece.board.en_passant = y

            case(True, str(), True):
                del std.Piece.board[self.pos]
                self.pos = move
                std.Piece.board[self.pos].piece = self

                del std.Piece.board[self.pos]
                std.Piece.board.pieces.remove(self)
                match move[2]:
                    case "q":
                        p = std.Queen(self.color, (ord(move[0])-97, int(move[1])-1))
                    case "r":
                        p = std.Rook(self.color, (ord(move[0])-97, int(move[1])-1))
                    case "n":
                        p = std.Knight(self.color, (ord(move[0])-97, int(move[1])-1))
                    case "b":
                        p = std.Bishop(self.color, (ord(move[0])-97, int(move[1])-1))
                std.Piece.board[move].piece = p
                std.Piece.board.pieces.append(p)
                del self

            case _:
                raise std.IllegalMoveError(self, move)

        std.Piece.board.half_moves = 0

    def can_move(self, move:str) -> \
            tuple[bool, bool]|tuple[bool, std.Piece|str, bool]|bool:
        if self.is_occupied(move):
            return False
        if self.is_occupied(move, True) and not self.can_capture(move):
            return False
        if self.pos[0] == move[0]:
            match int(self.pos[1]) - int(move[1]):
                case 1 if self.color:
                    return True, move[1] == "1"
                case -1 if not self.color:
                    return True, move[1] == "8"
                case 2 if self.color:
                    if self.is_occupied(f"{self.pos[0]}{int(self.pos[1])-1}", both=True):
                        return False
                    return True, f"{self.pos[0]}{int(self.pos[1])-1}", move[1] == "1"
                case -2 if not self.color:
                    if self.is_occupied(f"{self.pos[0]}{int(self.pos[1])+1}", both=True):
                        return False
                    return True, f"{self.pos[0]}{int(self.pos[1])+1}", move[1] == "8"
            return False

        b = self.can_move_diagonally(move, True, True)
        if self.is_occupied(move, True):
            if not self.can_move_diagonally(move, True):
                return False
            return (bool((b and not self.color) or (not b and self.color)), 
                    std.Square[move[:2]].piece, move[1] == ("1" if self.color else "8"))
        if std.Piece.board.en_passant == move:
            if not self.can_move_diagonally(move, True):
                return False
            return (bool((b and not self.color) or (not b and self.color)),
                    std.Square[f"{move[0]}{int(move[1]) + (1 if self.color else -1)}"].piece,
                    move[1] == ("1" if self.color else "8"))
        return False

    def get_moves(self) -> list[str]:
        moves = []
        for i in (1, 2, -1, -2):
            move = self.pos[0] + str(int(self.pos[1])+i)
            if std.check_UCI(self.pos+move) and move[1] not in "18":
                res = self.can_move(move)
                if isinstance(res, tuple):
                    if res[0]:
                        moves.append(move)
                elif res:
                    moves.append(move)

        for i in (1, -1):
            for j in (1, -1):
                move = chr(ord(self.pos[0])+i) + str(int(self.pos[1])+j)
                if std.check_UCI(self.pos+move) and move[1] not in "18":
                    res = self.can_move(move)
                    if isinstance(res, tuple):
                        if res[0]:
                            moves.append(move)
                    elif res:
                        moves.append(move)
                for k in "rnqb":
                    move = chr(ord(self.pos[0])+i) + str(int(self.pos[1])+j)+k
                    if std.check_UCI(self.pos+move):
                        res = self.can_move(move)
                        if isinstance(res, tuple):
                            if res[0]:
                                moves.append(move)
                        elif res:
                            moves.append(move)
            for l in "rnqb":
                move = self.pos[0]+ str(int(self.pos[1])+i)+l
                if std.check_UCI(self.pos+move):
                    res = self.can_move(move)
                    if isinstance(res, tuple):
                        if res[0]:
                            moves.append(move)
                    elif res:
                        moves.append(move)

        for i in (2, -2):
            for k in "rnqb":
                move = chr(ord(self.pos[0])) + str(int(self.pos[1])+i)+k
                if check_UCI(self.pos+move):
                    res = self.can_move(move)
                    if isinstance(res, tuple):
                        if res[0]:
                            moves.append(move)
                    elif res:
                        moves.append(move)
        return moves


class Board(std.Board):
    """The Chess Board

    Args:
        fen (str, optional): starting FEN. Defaults to the standard starting FEN.
        format_ (str, optional): Time format. Defaults to "5+0".
    """
    starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - 0 1"

    def make_pieces(self, pieces:str) -> None:
        """Makes the board

        Args:
            pieces (str): piece fen

        Raises:
            ValueError: If the passed piece fen is invalid
        """
        current = [0, 0]
        for rank in pieces.split("/")[::-1]:
            for square in rank:
                if square.isdigit():
                    current[1] += int(square)
                    continue
                match square:
                    case "r":
                        piece = std.Rook(1, current[::-1])
                    case "n":
                        piece = std.Knight(1, current[::-1])
                    case "b":
                        piece = std.Bishop(1, current[::-1])
                    case "q":
                        piece = std.Queen(1, current[::-1])
                    case "p":
                        piece = Pawn(1, current[::-1])
                    case "R":
                        piece = std.Rook(0, current[::-1])
                    case "N":
                        piece = std.Knight(0, current[::-1])
                    case "B":
                        piece = std.Bishop(0, current[::-1])
                    case "Q":
                        piece = std.Queen(0, current[::-1])
                    case "P":
                        piece = Pawn(0, current[::-1])
                    case "k":
                        if self.bking:
                            raise ValueError("More than 1 Black King")
                        piece = std.King(1, current[::-1])
                        self.bking = piece
                    case "K":
                        if self.wking:
                            raise ValueError("More than 1 White King")
                        piece = std.King(0, current[::-1])
                        self.wking = piece
                    case _:
                        raise ValueError("Illegal FEN")
                self.board[current[0]][current[1]].piece = piece
                self.pieces.append(piece)
                current[1] += 1
            current[0] += 1
            current[1] = 0

        if not (self.wking and self.bking):
            raise ValueError("Missing Kings")


def check_UCI(move:str) -> bool:
    """Checks if the move is correct or not

    Args:
        move (str): The move to check

    Returns:
        bool: if the move is according to UCI notation or not
    """
    if len(move) == 4:
        if move[0] in "abcdefgh" and move[2] in "abcdefgh":
            return move[1] in "12345678" and move[3] in "12345678"
    elif len(move) == 5:
        if move[0] in "abcdefgh" and move[2] in "abcdefgh":
            return move[1] in "2736" and move[3] in "18" and move[4] in "qrnb"
    return False
