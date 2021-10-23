"""Contains the code for the Three Check variant"""

from chess import standard as std


class King(std.King):
    """King piece

    Args:
        color (int): color of the piece
        position (tuple[int, int]): Position of the piece in a numeric form.
    """
    max_checks = 3

    def __init__(self, color:int, position:tuple[int, int]) -> None:
        self.lives = self.max_checks
        super().__init__(color=color, position=position)


class Board(std.Board):
    """The Chess Board

    Args:
        fen (str, optional): starting FEN. Defaults to the standard starting FEN.
        format_ (str, optional): Time format. Defaults to "5+0".
    """
    starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 +0+0"

    def play(self, move:str) -> None:
        """Play the given move

        Args:
            move (str): The move to play

        Raises:
            IllegalMoveError: If the move is Illegal
            ValueError: If the game is over
        """
        super().play(move)
        if std.Square[self.wking.pos].is_attacked():
            self.wking.checks += 1
        elif std.Square[self.bking.pos].is_attacked():
            self.bking.checks += 1
        self.is_over()

    def is_over(self) -> None:
        """Checks if the game is over

        Returns:
            str: Game over message
        """
        msg = ""
        if self.clock.is_up():
            if self.is_insufficient_material()[self.turn]:
                msg = "Draw by Time out"
            msg = "Time out!"
        elif self.wking.checks >= self.wking.max_checks:
            msg = "Three Checks, white lost"
        elif self.bking.checks >= self.bking.max_checks:
            msg = "Three Checks, black lost"
        moves = self.get_moves()
        if not moves:
            msg = "Stalemate"
        elif not self.filter_checks(moves):
            msg = "Checkmate"
        elif self.half_moves >= 100:
            msg = "Draw by 50 move rule"
        elif 3 in std.Counter(self.move_fen).values():
            msg = "Threefold repetition"
        elif self.is_insufficient_material()[2]:
            msg = "Insufficient material"
        elif msg:
            self.clock.stop()
            print(msg)
            exit()

    def make_board(self, fen:str) -> None:
        """Makes the board

        Args:
            fen (str): FEN for the board

        Raises:
            ValueError: if the fen is invalid
        """
        checks = fen[-4:]
        super().make_board(fen[:-5])
        self.bking.checks = int(checks[1])
        self.wking.checks = int(checks[3])

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
        return super().generate_fen() + f" +{self.bking.checks}+{self.wking.checks}"
