from chess import standard as std, three_check as tc, no_castling as nc, torpedo as tp, \
    king_of_the_hill as koth, racing_kings as rk


class Standard(std.Board): pass
class ThreeCheck(tc.Board): pass
class NoCastling(nc.Board): pass
class Torpedo(tp.Board): pass
class KingOfTheHill(koth.Board): pass
class RacingKings(rk.Board): pass
class FromPosition(std.Board):pass


class Chess960(std.Board):
    def __init__(self, fen:str="", format_:str="5+0") -> None:
        if not fen:
            fen = std.generate_chess960_pieces() + " w - - 0 1"
        super().__init__(fen, format_)
