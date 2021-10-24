"""Contains the code for Racing Kings variant"""

from chess import standard as std


class Board(std.Board):
    """The Chess Board

    Args:
        fen (str, optional): starting FEN. Defaults to the standard starting FEN.
        format_ (str, optional): Time format. Defaults to "5+0".
    """

    starting_fen = "8/8/8/8/8/8/krbnNBRK/qrbnNBRQ w - - 0 1"

    def filter_checks(self, moves:list[str]) -> list[str]:
        """Filters the moves to remove checks

        Args:
            moves (list[str]): List of moves

        Returns:
            list[str]: Filtered list of moves
        """
        filtered = []
        for move in moves:
            self._old_play(move)
            if not (std.Square[self.wking.pos].is_attacked() 
                    or std.Square[self.bking.pos].is_attacked()):
                filtered.append(move)
            self.reverse()
        return filtered

    def is_over(self) -> None:
        """Ends the game if the game is over"""
        msg = ""
        if self.clock.is_up():
            msg = "Time out!"
        elif self.wking.pos[1] == "8":
            print("white won the race")
        elif self.bking.pos[1] == "8":
            print("black won the race")
        moves = self.get_moves()
        if not moves:
            msg = "Stalemate"
        elif not self.filter_checks(moves):
            msg = "Checkmate"
        elif self.half_moves >= 100:
            msg = "Draw by 50 move rule"
        elif 3 in std.Counter(self.move_fen).values():
            msg = "Threefold repetition"
        if msg:
            self.clock.stop()
            print(msg)
            exit()

