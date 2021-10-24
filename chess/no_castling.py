"""Contains the code for the No Castling variant"""

from chess import standard as std


class King(std.King):
    """King piece

    Args:
        color (int): color of the piece
        position (tuple[int, int]): Position of the piece in a numeric form.
    """

    def can_move(self, move:str) -> bool:
        if len(move) == 2 and not self.is_occupied(move):
            if self.can_move_straight(move, True) or self.can_move_diagonally(move, True):
                return True
        return False

    def get_moves(self) -> list[str]:
        moves = []
        for i in (1, 0, -1):
            for j in (1, 0, -1):
                if i == j == 0:
                    continue
                square = f"{chr(ord(self.pos[0]) + i)}{int(self.pos[1]) + j}"
                if std.check_UCI(self.pos+square) and self.can_move(square):
                    moves.append(square)
        return moves


class Board(std.Board):
    """The Chess Board

    Args:
        fen (str, optional): starting FEN. Defaults to the standard starting FEN.
        format_ (str, optional): Time format. Defaults to "5+0".
    """
    starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - 0 1"

    def make_board(self, fen:str) -> None:
        """Makes the board

        Args:
            fen (str): FEN for the board

        Raises:
            ValueError: if the fen is invalid
        """
        self.pieces:list[std.Piece] = []
        self.wking:King = None
        self.bking:King = None
        self.board = [[std.Square((i, j)) for i in range(8)] for j in range(8)]
        parts = fen.split()
        self.turn = 0 if parts[1] == "w" else 1
        self.en_passant = None if parts[2] == "-" else parts[2]
        self.half_moves = int(parts[3])
        self.full_moves = int(parts[4])
        self.make_pieces(parts[0])

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
                    case "R":
                        piece = std.Rook(0, current[::-1])
                    case "N":
                        piece = std.Knight(0, current[::-1])
                    case "B":
                        piece = std.Bishop(0, current[::-1])
                    case "Q":
                        piece = std.Queen(0, current[::-1])
                    case "P":
                        piece = std.Pawn(0, current[::-1])
                    case "k":
                        if self.bking:
                            raise ValueError("More than 1 Black King")
                        piece = King(1, current[::-1])
                        self.bking = piece
                    case "K":
                        if self.wking:
                            raise ValueError("More than 1 White King")
                        piece = King(0, current[::-1])
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

    def generate_fen(self) -> str:
        """Genrates FEN for given board"""
        fen = f"{self.generate_piece_fen()} {'b' if self.turn else 'w'}"
        fen += f" {self.en_passant or '-'} {self.half_moves} {self.full_moves}"
        return fen
