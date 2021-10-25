"""Contains the code for Racing Kings variant"""

from chess import standard as std


class Board(std.Board):
    """The Chess Board

    Args:
        fen (str, optional): starting FEN. Defaults to the standard starting FEN.
        format_ (str, optional): Time format. Defaults to "5+0".
    """

    starting_fen = "8/8/8/8/8/8/krbnNBRK/qrbnNBRQ w - - 0 1"

    def __init__(self, fen:str="", format_:str="5+0") -> None:
        super().__init__(fen, format_)
        self.end = None

    def filter_checks(self, moves:list[str]) -> list[str]:
        """Filters the moves to remove checks

        Args:
            moves (list[str]): List of moves

        Returns:
            list[str]: Filtered list of moves
        """
        if self.filter_moves:
            if self.filter_moves[0] == [self.turn, self.full_moves]:
                return self.filter_moves[1]
        filtered = []
        for move in moves:
            self._old_play(move)
            if not (std.Square[self.wking.pos].is_attacked() 
                    or std.Square[self.bking.pos].is_attacked()):
                filtered.append(move)
            self.reverse()
        self.filter_moves = [[self.turn, self.full_moves], filtered]
        return filtered

    def is_over(self) -> None:
        """Ends the game if the game is over"""
        msg = ""
        if self.clock.is_up():
            msg = "Time out!"

        elif self.wking.pos[1] == "8":
            if self.bking.pos[1] == "8":
                msg = "Race is drawn"
            elif self.end == 1:
                msg = "white won the race"
            elif any(p[1] == "8" for p in self.bking.get_moves()):
                self.end = 1
            else:
                msg = "white won the race"

        elif self.bking.pos[1] == "8":
            if self.wking.pos[1] == "8":
                msg = "Race is drawn"
            elif self.end == 0:
                msg = "black won the race"
            elif any(p[1] == "8" for p in self.wking.get_moves()):
                self.end = 0
            else:
                msg = "black won the race"
        elif not self.get_moves():
            msg = "Stalemate"
        elif self.half_moves >= 100:
            msg = "Draw by 50 move rule"
        elif 3 in std.Counter(self.move_fen).values():
            msg = "Threefold repetition"
        if msg:
            self.clock.stop()
            print(msg)
            exit()

