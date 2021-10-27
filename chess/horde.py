"""Contains the code for the Horde variant"""

from chess import standard as std


class Pawn(std.Pawn):
    def can_move(self, move:str
            ) -> tuple[bool, None|std.Piece|str|bool]|tuple[bool, None|std.Piece, bool]|bool:
        if self.is_occupied(move):
            return False
        if self.is_occupied(move, True) and not self.can_capture(move):
            return False
        if self.pos[0] == move[0]:
            match int(self.pos[1]) - int(move[1]):
                case 1 if self.color:
                    if move[1] == "1":
                        return True, True
                    return True
                case -1 if not self.color:
                    if move[1] == "8":
                        return True, True
                    return True
                case 2 if self.color and self.pos[1] == "7":
                    if self.is_occupied(f"{self.pos[0]}6", both=True):
                        return False
                    return True, f"{self.pos[0]}6"
                case 2 if self.color and self.pos[1] == "8":
                    if self.is_occupied(f"{self.pos[0]}7", both=True):
                        return False
                    return True
                case -2 if not self.color and self.pos[1] == "2":
                    if self.is_occupied(f"{self.pos[0]}3", both=True):
                        return False
                    return True, f"{self.pos[0]}3"
                case -2 if not self.color and self.pos[1] == "1":
                    if self.is_occupied(f"{self.pos[0]}2", both=True):
                        return False
                    return True
            return False
        b = self.can_move_diagonally(move, True, True)
        if self.is_occupied(move, True):
            if not self.can_move_diagonally(move, True):
                return False
            return (bool((b and not self.color) or (not b and self.color)), 
                    std.Piece.board[move].piece, move[1] == ("1" if self.color else "8"))
        if std.Piece.board.en_passant == move:
            if not self.can_move_diagonally(move, True):
                return False
            return (bool((b and not self.color) or (not b and self.color)),
                    std.Piece.board[f"{move[0]}{int(move[1]) + (1 if move[1] == '3' else -1)}"].piece)
        return False



class Board(std.Board):
    """The Chess Board

    Args:
        fen (str, optional): starting FEN. Defaults to the standard starting FEN.
        format_ (str, optional): Time format. Defaults to "5+0".
    """

    starting_fen = "rnbqkbnr/pppppppp/8/1PP2PP1/PPPPPPPP/PPPPPPPP/PPPPPPPP/PPPPPPPP w kq - 0 1"

    def __init__(self, format_:str="5+0") -> None:
        super().__init__("", format_)

    def make_board(self, fen:str) -> None:
        """Makes the board

        Args:
            fen (str): FEN for the board
        """
        self.pieces:list[std.Piece] = []
        self.king:std.King = None
        self.board = [[std.Square((i, j)) for i in range(8)] for j in range(8)]
        parts = fen.split()
        self.turn = 0 if parts[1] == "w" else 1
        self.en_passant = None if parts[3] == "-" else parts[3]
        self.half_moves = int(parts[4])
        self.full_moves = int(parts[5])
        self.make_pieces(parts[0])
        self.king.q = False
        self.king.k = False

        if parts[2] == "-":
            self.king.moved = True
        else:
            for string in parts[2]:
                match string:
                    case "k":
                        self.king.k = True
                    case "q":
                        self.king.q = True
                    case _:
                        raise ValueError("Illegal FEN")

    def filter_checks(self, moves:list[str]) -> list[str]:
        """Filters the moves to remove checks

        Args:
            moves (list[str]): List of moves

        Returns:
            list[str]: Filtered list of moves
        """
        if self.turn == 0:
            return moves
        if self.filter_moves:
            if self.filter_moves[0] == [self.turn, self.full_moves]:
                return self.filter_moves[1]
        filtered = []
        for move in moves:
            self._old_play(move)
            if not std.Square[self.king.pos].is_attacked():
                filtered.append(move)
            self.reverse()
        self.filter_moves = [[self.turn, self.full_moves], filtered]
        return filtered

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
                        piece = std.Pawn(1, current[::-1])
                    case "P":
                        piece = Pawn(0, current[::-1])
                    case "k":
                        if self.king:
                            raise ValueError("More than 1 Black King")
                        piece = std.King(1, current[::-1])
                        self.king = piece
                    case _:
                        raise ValueError("Illegal FEN")
                self.board[current[0]][current[1]].piece = piece
                self.pieces.append(piece)
                current[1] += 1
            current[0] += 1
            current[1] = 0

    def is_over(self) -> None:
        """Ends the game if the game is over"""
        msg = ""
        if self.clock.is_up():
            if self.is_insufficient_material()[self.turn] and self.turn:
                msg = "Draw by Time out"
            else:
                msg = "Time out!"
        elif not (moves := self.get_moves()):
            if all(piece.color == 1 for piece in self.pieces):
                msg = "Horde was destroyed"
            else:
                msg = "Stalemate"
        elif not self.filter_checks(moves):
            msg = "Checkmate"
        elif self.half_moves >= 100:
            msg = "Draw by 50 move rule"
        elif 3 in std.Counter(self.move_fen).values():
            msg = "Threefold repetition"
        elif self.is_insufficient_material()[2]:
            msg = "Insufficient material"
        if msg:
            self.clock.stop()
            print(msg)
            exit()

    def is_insufficient_material(self) -> tuple[bool, bool, bool]:
        """Checks if a player has insufficient material

        Returns:
            tuple[bool, bool, bool]:
            if black or white or both have insufficient material to mate
        """
        black, white = [], []
        wins, bins, draw = False, False, False
        bb, wb = False, False
        for piece in self.pieces:
            if piece.color and piece is not self.king:
                if piece.type in "BN":
                    black.append(piece)
                else:
                    bb = True
            elif not piece.color:
                if piece.type in "BN":
                    white.append(piece)
                else:
                    wb = True

        if len(white) <= 1:
            wins = True
        else:
            color = ord(white[0].pos[0]) %2 == int(white[0].pos[1]) %2
            for piece in white:
                if piece.type == "B":
                    if color is (ord(piece.pos[0]) %2 == int(piece.pos[1]) %2):
                        wins = True
                    else:
                        wins = False
                        break
                else:
                    wins = False
                    break

        if len(black) <= 1:
            bins = True
        else:
            color = ord(black[0].pos[0]) %2 == int(black[0].pos[1]) %2
            for piece in black:
                if piece.type == "B":
                    if color is (ord(piece.pos[0]) %2 == int(piece.pos[1]) %2):
                        wins = True
                    else:
                        wins = False
                        break
                else:
                    wins = False
                    break

        if wins and bins and not (wb or bb):
            if not black and not white:
                draw = True
            elif black and black[0].type == "N" and not white:
                draw = True
            elif white[0].type == "N" and not black:
                draw = True
            elif all(p.type == "B" for p in white) and all(p.type == "B" for p in black):
                draw = True
                for b, w in zip(black, white):
                    bcolor = (ord(w.pos[0]) %2 == int(w.pos[1]) %2)
                    wcolor = (ord(b.pos[0]) %2 == int(b.pos[1]) %2)
                    if wcolor is not bcolor:
                        draw = False
                        break

        if wb:
            return False, False if bb else bins, False 
        elif bb:
            return False if wb else wins, False, False
        return wins, bins, draw

    def castling(self) -> str:
        """Returns the castling rights for FEN generation"""
        king = False
        queen = False
        if self.king.moved:
            return "-"

        for piece in self.pieces:
            if piece.type == "R" and not piece.moved:
                if piece.color:
                    if piece.pos[0] > self.king.pos[0] and self.king.k and king is not None:
                        king = "k"
                    elif self.king.q and queen is not None:
                        queen = "q"

        return "".join(list(filter(None, (king, queen)))) or "-"
