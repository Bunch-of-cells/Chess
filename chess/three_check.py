"""Contains the code for the Three Check variant"""

from chess import standard as std


class King(std.king):
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

    def filter_checks(self, moves:list[str]) -> list[str]:
        """Filters the moves to remove checks

        Args:
            moves (list[str]): List of moves

        Returns:
            list[str]: Filtered list of moves
        """
        if std.Square[self.wking.pos].is_attacked():
            self.wking.lives -= 1
        if std.Square[self.bking.pos].is_attacked():
            self.bking.lives -= 1
        super().filter_checks(self, moves)

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
        elif self.wking.lives < 0:
            msg = "Three Checks, white lost"
        elif self.bking.lives < 0:
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
        parts = fen.split()
        checks = parts.pop()
        super().make_board(fen)
        self.bking.lives = int(checks[1])
        self.wking.lives = int(checks[3])
