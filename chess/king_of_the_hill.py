"""Contains the code for the King of the Hill variant"""

from chess import standard as std


class Board(std.Board):
    """The Chess Board

    Args:
        fen (str, optional): starting FEN. Defaults to the standard starting FEN.
        format_ (str, optional): Time format. Defaults to "5+0".
    """
    def is_over(self) -> None:
        """Ends the game if the game is over"""
        msg = ""
        if self.clock.is_up():
            msg = "Time out!"
        moves = self.get_moves()
        if self.wking.pos in ('e4', 'd4', 'e5', 'd5'):
            print("King of the Hill, white won")
        if self.bking.pos in ('e4', 'd4', 'e5', 'd5'):
            print("King of the Hill, black won")
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

