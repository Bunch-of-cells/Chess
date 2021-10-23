from __future__ import annotations

"""Contains the Board"""

from collections import Counter
import pprint
from abc import ABC, abstractmethod
from threading import Thread
from time import sleep


class Piece(ABC):
    """A chess piece

    Args:
        color (int): Color of the piece (0 for white, 1 for black)
        pos (str): position of the piece
    """

    type_:str = ""
    board:Board = None

    def __init__(self, color:int, pos:str) -> None:
        self.color = color  # 0(white) or 1(black)
        self.pos = pos
        self.type:str = self.type_

    def __str__(self) -> str:
        if self.color:
            return self.type.lower()
        return self.type.upper()

    @abstractmethod
    def move(self, move:str) -> None:
        """Moves the piece to the given square

        Args:
            move (str): destination square
        
        Raises:
            ValueError: If the square passed is not valid
        """

    @abstractmethod
    def can_move(self, move:str) -> bool:
        """Checks if the piece can move to the given square

        Args:
            move (str): The square

        Returns:
            bool: If the piece can move to that square
        """

    @abstractmethod
    def get_moves(self) -> list[str]:
        """Gets a list of all the moves for the pieces

        Returns:
            list[str]: list of all of the piece's moves
        """

    def can_move_diagonally(self, move:str, one:bool=False, dir_:bool|None=None) -> bool:
        """Checks if the piece can move diagonally to the given square

        Args:
            move (str): The square
            one (bool): if the piece can only move 1 square. Defaults to False.
            dir_ (bool|None): if the piece can only move forward 1 square in the given 
            direction. Defaults to False.

        Returns:
            bool: If the piece can move diagonally to that square
        """

        cond = abs(ord(self.pos[0]) - ord(move[0])) == abs(int(self.pos[1]) - int(move[1]))
        if not cond or self.is_available(move):
            return False
        if dir_ is not None:
            if not abs(ord(self.pos[0]) - ord(move[0])) == 1:
                return False
            return int(move[1]) - int(self.pos[1]) == (1 if dir_ else  -1)
        if one:
            return abs(ord(self.pos[0]) - ord(move[0])) == 1
        stepy = abs(int(move[1]) - int(self.pos[1]))//(int(move[1]) - int(self.pos[1]))
        stepx = abs(ord(move[0]) - ord(self.pos[0]))//(ord(move[0]) - ord(self.pos[0]))
        sq = chr(ord(self.pos[0]) + stepx) + str(int(self.pos[1]) + stepy)
        while sq != move:
            if sq[0] == "i" or sq[1] in "09":
                break
            if Piece.board[sq].piece is not None:
                return False
            sq = chr(ord(sq[0]) + stepx) + str(int(sq[1]) + stepy)
        return True

    def can_move_straight(self, move:str, one:bool=False) -> bool:
        """Checks if the piece can move straight to the given square

        Args:
            move (str): The square
            one (bool): if the piece can only move 1 square. Defaults to False.

        Returns:
            bool: If the piece can move straight to that square
        """

        cond = (move[0] == self.pos[0]) != (move[1] == self.pos[1])
        if not cond or self.is_available(move):
            return False
        if one:
            cond_a =  abs(ord(self.pos[0]) - ord(move[0])) == 1
            cond_b = abs(int(self.pos[1]) - int(move[1])) == 1
            return cond_a or cond_b
        if move[1] == self.pos[1]:
            step = abs(ord(move[0]) - ord(self.pos[0]))//(ord(move[0]) - ord(self.pos[0]))
            return not any(Piece.board[f'{chr(file)}{move[1]}'].piece is not None
                for file in range(ord(self.pos[0])+step, ord(move[0]), step))
        if move[0] == self.pos[0]:
            step = abs(ord(move[1]) - ord(self.pos[1]))//(ord(move[1]) - ord(self.pos[1]))
            return all(Piece.board[f'{move[0]}{rank}'].piece is None
                for rank in range(int(self.pos[1])+step, int(move[1]), step))
        return False

    def is_available(self, square:str, opponent:bool=False) -> bool:
        """Checks if the square is occupied by another of your own piece

        Args:
            move (str): The square
            opponent (bool): returns True if square is occupied by an opponent piece.
            Defaults to False.

        Returns:
            bool: If the square is occupied
        """

        piece = Piece.board[square].piece
        if opponent:
            return piece and piece.color != self.color
        return piece and piece.color == self.color

    def delete(self) -> None:
        """Deletes the piece"""
        Piece.board[self.pos].piece = None
        Piece.board.pieces.remove(self)
        del self

    def get_diagonal_moves(self) -> list[str]:
        """Gets all of the piece's diagonal moves

        Returns:
            list[str]: a list of all of the piece's diagonal moves'
        """
        moves = []
        m = chr(ord(self.pos[0])+1)+str(int(self.pos[1])+1)
        while check_UCI(self.pos+m) and self.can_move(m):
            moves.append(m)
            m = chr(ord(m[0])+1)+str(int(m[1])+1)
        m = chr(ord(self.pos[0])-1)+str(int(self.pos[1])-1)
        while check_UCI(self.pos+m) and self.can_move(m):
            moves.append(m)
            m = chr(ord(m[0])-1)+str(int(m[1])-1)
        m = chr(ord(self.pos[0])-1)+str(int(self.pos[1])+1)
        while check_UCI(self.pos+m) and self.can_move(m):
            moves.append(m)
            m = chr(ord(m[0])-1)+str(int(m[1])+1)
        m = chr(ord(self.pos[0])+1)+str(int(self.pos[1])-1)
        while check_UCI(self.pos+m) and self.can_move(m):
            moves.append(m)
            m = chr(ord(m[0])+1)+str(int(m[1])-1)
        return moves

    def get_straight_moves(self) -> list[str]:
        """Gets all of the piece's straight moves

        Returns:
            list[str]: a list of all of the piece's straight moves'
        """
        moves = []
        m = chr(ord(self.pos[0])+1)
        while check_UCI(self.pos+m+self.pos[1]) and self.can_move(m+self.pos[1]):
            moves.append(m+self.pos[1])
            m = chr(ord(m)+1)
        m = chr(ord(self.pos[0])-1)
        while check_UCI(self.pos+m+self.pos[1]) and self.can_move(m+self.pos[1]):
            moves.append(m+self.pos[1])
            m = chr(ord(m)-1)
        m = str(int(self.pos[1])+1)
        while check_UCI(self.pos+self.pos[0]+m) and self.can_move(self.pos[0]+m):
            moves.append(self.pos[0]+m)
            m = str(int(m)+1)
        m = str(int(self.pos[1])-1)
        while check_UCI(self.pos+self.pos[0]+m) and self.can_move(self.pos[0]+m):
            moves.append(self.pos[0]+m)
            m = str(int(m)-1)
        return moves


class IllegalMoveError(Exception):
    """Error raised when an illegal move is played"""
    def __init__(self, piece:Piece='', move:str='', msg:str='') -> None:
        if msg:
            super().__init__(msg)
        else:
            super().__init__(f"{piece} at {piece.pos} cannot play {move}")


class King(Piece):
    """King piece

    Args:
        color (int): color of the piece
        position (tuple[int, int]): Position of the piece in a numeric form.
    """
    type_ = "K"
    CASTLING = ("g1", "g8", "c1", "c8")
    CASTLED_ROOK = ("f1", "f8", "d1", "d8")

    def __init__(self, color:int, position:tuple[int, int]) -> None:
        pos = f"{chr(position[0]+97)}{position[1]+1}"
        if (pos[1] == "1" and not color) or (pos[1] == "8" and color):
            self.moved = False
        else:
            self.moved = True
        self.k = not self.moved
        self.q = not self.moved
        super().__init__(color, pos)

    def move(self, move:str) -> None:
        if not (castle := self.can_move(move)):
            raise IllegalMoveError(self, move)
        if isinstance(castle, Rook):
            self.castle(castle)
        elif self.is_available(move, True):
            Piece.board.half_moves = 0
            Piece.board[move].piece.delete()
        del Piece.board[self.pos]
        self.pos = move
        Piece.board[move].piece = self
        self.moved = True

    def get_moves(self) -> list[str]:
        moves = []
        for i in (1, 0, -1):
            for j in (1, 0, -1):
                if i == j == 0:
                    continue
                square = f"{chr(ord(self.pos[0]) + i)}{int(self.pos[1]) + j}"
                if check_UCI(self.pos+square) and self.can_move(square):
                    moves.append(square)
        castle = self.can_castle()
        if castle[0]:
            moves.append(self.CASTLING[1] if self.color else self.CASTLING[0])
        if castle[1]:
            moves.append(self.CASTLING[3] if self.color else self.CASTLING[2])
        return moves

    def can_move(self, move:str) -> bool:
        if len(move) == 2 and not self.is_available(move):
            if self.can_move_straight(move, True) or self.can_move_diagonally(move, True):
                return True
            castle = self.can_castle()
            if move in self.CASTLING[:2]:
                return castle[0]
            elif move in self.CASTLING[2:]:
                return castle[1]

    def castle(self, piece:Rook) -> None:
        """Castles the king"""
        if hasattr(piece, "kingside"):
            if self.color:
                piece.move(self.CASTLED_ROOK[1])
            else:
                piece.move(self.CASTLED_ROOK[0])
            delattr(piece, "kingside")
        elif hasattr(piece, "queenside"):
            if self.color:
                piece.move(self.CASTLED_ROOK[3])
            else:
                piece.move(self.CASTLED_ROOK[2])
            delattr(piece, "queenside")
        else:
            raise Exception(piece.__dict__)

    def can_castle(self) -> tuple[None|Rook, None|Rook]:
        """Checks if the king can castle or not

        Returns:
            tuple[None|Rook, None|Rook]: A tuple of rooks which can castle with the king
        """
        kingside = None
        queenside = None
        if self.moved or Square[self.pos].is_attacked():
            return None, None
        # for piece in self.board.pieces:
        #     if piece.type == "R" and piece.color == self.color and not piece.moved:
        #         if self.castle_route(-1) or self.castle_route(1):
        #             if piece.pos[0] > self.pos[0] and self.k:
        #                 kingside = piece
        #                 piece.kingside = None
        #             elif self.q:
        #                 queenside = piece
        #                 piece.queenside = None

        return kingside, queenside

    def castle_route(self, side:int) -> bool:
        """Checks if the path is clear and checkless for castling

        Args:
            side (int): side the king wants to castle, 1 or -1

        Returns:
            bool: If the king can castle or not
        """
        move = chr(ord(self.pos[0])+side)
        if self.is_available(move+self.pos[1]):
            return False
        step = abs(ord(move) - ord(self.pos[0]))//(ord(move) - ord(self.pos[0]))
        for file in range(ord(self.pos[0])+step, ord(move[0]), step):
            if Piece.board[f'{chr(file)}{move[1]}'].piece is not None:
                return False
            # if Square[f'{chr(file)}{move[1]}'].is_attacked():
            #     return False
        return True


class Rook(Piece):
    """Rook piece

    Args:
        color (int): color of the piece
        position (tuple[int, int]): Position of the piece in a numeric form.
    """
    type_ = "R"

    def __init__(self, color:int, position:tuple[int,int]) -> None:
        pos = f"{chr(position[0]+97)}{position[1]+1}"
        self.moved = True
        if pos[1] == "1" and not color:
            self.moved = False
        elif pos[1] == "8" and color:
            self.moved = False
        super().__init__(color, pos)

    def move(self, move:str) -> None:
        if not self.can_move(move):
            raise IllegalMoveError(self, move)
        if self.is_available(move, True):
            Piece.board.half_moves = 0
            Piece.board.pieces.remove(Piece.board[move].piece)
            del Piece.board[move]
        del Piece.board[self.pos]
        self.pos = move
        Piece.board[move].piece = self
        self.moved = True

    def get_moves(self) -> list[str]:
        return self.get_straight_moves()

    def can_move(self, move:str) -> bool:
        if len(move) == 2:
            return self.can_move_straight(move)


class Bishop(Piece):
    """Bishop piece

    Args:
        color (int): color of the piece
        position (tuple[int, int]): Position of the piece in a numeric form.
    """
    type_ = "B"

    def __init__(self, color:int, position:tuple[int,int]) -> None:
        pos = f"{chr(position[0]+97)}{position[1]+1}"
        super().__init__(color, pos)

    def move(self, move:str) -> None:
        if not self.can_move(move):
            raise IllegalMoveError(self, move)
        if self.is_available(move, True):
            Piece.board.half_moves = 0
            Piece.board.pieces.remove(Piece.board[move].piece)
            del Piece.board[move]
        del Piece.board[self.pos]
        self.pos = move
        Piece.board[move].piece = self

    def get_moves(self) -> list[str]:
        return self.get_diagonal_moves()

    def can_move(self, move:str) -> bool:
        if len(move) == 2:
            return self.can_move_diagonally(move)


class Queen(Piece):
    """Queen piece

    Args:
        color (int): color of the piece
        position (tuple[int, int]): Position of the piece in a numeric form.
    """
    type_ = "Q"

    def __init__(self, color:int, position:tuple[int, int]=()) -> None:
        if position:
            pos = f"{chr(position[0]+97)}{position[1]+1}"
        else:
            pos = "d8" if color else "d1"
        super().__init__(color, pos)

    def move(self, move:str) -> None:
        if not self.can_move(move):
            raise IllegalMoveError(self, move)
        if self.is_available(move, True):
            Piece.board.half_moves = 0
            Piece.board.pieces.remove(Piece.board[move].piece)
            del Piece.board[move]
        del Piece.board[self.pos]
        self.pos = move
        Piece.board[move].piece = self

    def get_moves(self) -> list[str]:
        return self.get_straight_moves() + self.get_diagonal_moves()

    def can_move(self, move:str) -> bool:
        if len(move) == 2:
            return self.can_move_straight(move) or self.can_move_diagonally(move)


class Knight(Piece):
    """Knight piece

    Args:
        color (int): color of the piece
        position (tuple[int, int]): Position of the piece in a numeric form.
    """
    type_ = "N"

    def __init__(self, color:int, position:tuple[int,int]) -> None:
        pos = f"{chr(position[0]+97)}{position[1]+1}"
        super().__init__(color, pos)

    def move(self, move:str) -> None:
        if not self.can_move(move):
            raise IllegalMoveError(self, move)
        if self.is_available(move, True):
            Piece.board.half_moves = 0
            Piece.board[move].piece.delete()
        del Piece.board[self.pos]
        self.pos = move
        Piece.board[move].piece = self

    def can_move(self, move:str) -> bool:
        if len(move) == 2 and not self.is_available(move):
            if abs(ord(self.pos[0]) - ord(move[0])) == 2:
                return abs(int(self.pos[1]) - int(move[1])) == 1
            elif abs(ord(self.pos[0]) - ord(move[0])) == 1:
                return abs(int(self.pos[1]) - int(move[1])) == 2
        return False

    def get_moves(self) -> list[str]:
        moves = []
        for i in (2, -2, 1, -1):
            for j in (2, -2, 1, -1):
                if abs(i) != abs(j):
                    square = f"{chr(ord(self.pos[0]) + i)}{int(self.pos[1]) + j}"
                    if check_UCI(self.pos+square) and self.can_move(square):
                        moves.append(square)
        return moves


class Pawn(Piece):
    """a Pawn

    Args:
        color (int): color of the piece
        position (tuple[int, int]): Position of the piece in a numeric form.
    """
    type_ = "P"

    def __init__(self, color:int, position:tuple[int, int]) -> None:
        pos = f"{chr(position[0]+97)}{position[1]+1}"
        super().__init__(color, pos)
    
    def get_moves(self) -> list[str]:
        moves = []
        for i in (1, 2, -1, -2):
            move = self.pos[0] + str(int(self.pos[1])+i)
            if check_UCI(self.pos+move) and move[1] not in "18":
                res = self.can_move(move)
                if isinstance(res, tuple):
                    if res[0]:
                        moves.append(move)
                elif res:
                    moves.append(move)
        for i in (1, -1):
            for j in (1, -1):
                move = chr(ord(self.pos[0])+i) + str(int(self.pos[1])+j)
                if check_UCI(self.pos+move) and move[1] not in "18":
                    res = self.can_move(move)
                    if isinstance(res, tuple):
                        if res[0]:
                            moves.append(move)
                    elif res:
                        moves.append(move)
                for k in "rnqb":
                    move = chr(ord(self.pos[0])+i) + str(int(self.pos[1])+j)+k
                    if check_UCI(self.pos+move):
                        res = self.can_move(move)
                        if isinstance(res, tuple):
                            if res[0]:
                                moves.append(move)
                        elif res:
                            moves.append(move)
            for l in "rnqb":
                move = self.pos[0]+ str(int(self.pos[1])+i)+l
                if check_UCI(self.pos+move):
                    res = self.can_move(move)
                    if isinstance(res, tuple):
                        if res[0]:
                            moves.append(move)
                    elif res:
                        moves.append(move)
        return moves

    def move(self, move:str) -> None:
        """A pawn move"""
        match self.can_move(move):
            case True:
                del Piece.board[self.pos]
                self.pos = move
                Piece.board[move].piece = self
            case (True, Piece() as piece):
                del Piece.board[self.pos]
                del Piece.board[piece.pos]
                self.pos = move
                Piece.board[self.pos].piece = self
                Piece.board.pieces.remove(piece)

            case (True, Piece() as piece, True):
                del Piece.board[self.pos]
                Piece.board.pieces.remove(piece)
                del Piece.board[piece.pos]
                Piece.board.pieces.remove(self)
                match move[2]:
                    case "q":
                        p = Queen(self.color, (ord(move[0])-97, int(move[1])-1))
                    case "r":
                        p = Rook(self.color, (ord(move[0])-97, int(move[1])-1))
                    case "n":
                        p = Knight(self.color, (ord(move[0])-97, int(move[1])-1))
                    case "b":
                        p = Bishop(self.color, (ord(move[0])-97, int(move[1])-1))
                Piece.board[move].piece = p
                Piece.board.pieces.append(p)
                del self

            case (True, Piece() as piece, False):
                del Piece.board[self.pos]
                del Piece.board[piece.pos]
                self.pos = move
                Piece.board[self.pos].piece = self
                Piece.board.pieces.remove(piece)

            case(True, True):
                del Piece.board[self.pos]
                Piece.board.pieces.remove(self)
                match move[2]:
                    case "q":
                        p = Queen(self.color, (ord(move[0])-97, int(move[1])-1))
                    case "r":
                        p = Rook(self.color, (ord(move[0])-97, int(move[1])-1))
                    case "n":
                        p = Knight(self.color, (ord(move[0])-97, int(move[1])-1))
                    case "b":
                        p = Bishop(self.color, (ord(move[0])-97, int(move[1])-1))
                Piece.board[move].piece = p
                Piece.board.pieces.append(p)
                del self

            case(True, y):
                del Piece.board[self.pos]
                self.pos = move
                Piece.board[self.pos].piece = self
                Piece.board.en_passant = y
            case _:
                raise IllegalMoveError(self, move)
        
        Piece.board.half_moves = 0

    def can_move(self, move:str
            ) -> tuple[bool, None|Piece|str|bool]|tuple[bool, None|Piece, bool]|bool:
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
                    return True, f"{self.pos[0]}6"
                case -2 if not self.color and self.pos[1] == "2":
                    return True, f"{self.pos[0]}3"
            return False
        b = self.can_move_diagonally(move, True, True)
        if self.is_available(move, True):
            if not self.can_move_diagonally(move, True):
                return False
            return (bool((b and not self.color) or (not b and self.color)), 
                    Piece.board[move].piece, move[1] == ("1" if self.color else "8"))
        if Piece.board.en_passant == move:
            if not self.can_move_diagonally(move, True):
                return False
            return (bool((b and not self.color) or (not b and self.color)),
                    Piece.board[f"{move[0]}{int(move[1]) + (1 if move[1] == '3' else -1)}"].piece)
        return False


class SquareMeta(type):
    """Metaclass for the square class"""
    squares = {}
    def __call__(cls, pos):
        obj = super().__call__(pos)
        SquareMeta.squares[f"{chr(pos[0]+97)}{pos[1]+1}"] = obj
        return obj

    def __getitem__(self, index:str) -> Square:
        return self.squares[index]


class Square(metaclass=SquareMeta):
    """A Square

    Args:
        pos (tuple[int, int]): A numeric form of the position of the square
    """
    def __init__(self, pos:tuple[int, int]) -> None:
        self.pos = pos
        self.piece:Piece = None

    def __repr__(self) -> str:
        return str(self.piece or " ")

    def is_attacked(self) -> bool:
        """Returns a bool if the square is attacked by an enemy piece"""
        for piece in Piece.board.pieces:
            if (piece.color != self.piece.color
                and piece.type != self.piece.type  # Important idk why to avoid recursion
                and piece.can_move(self.piece.pos)
            ):
                    return True
        return False


class Clock:
    """A chess Clock

    Args:
        format_ (str): Time format. TIME+INCREMENT+DELAY
        turn (int, optional): Which player has to move. 0 for white and 1 for black.
        Defaults to 0.
        sleep (float, optional): Time between each clock loop. Used to lower the cpu load.
        Defaults to 0.1.

    Raises:
        ValueError: When a wrong format is passed
    """
    def __init__(self, format_:str, turn:int=0, sleep:float=0.1) -> None:
        time = format_.split("+")
        self.turn = turn
        self.increment = 0
        self.delay = 0
        self.ticking = False

        match time:
            case [x]:
                self.initial = int(x)*600
            case [x, y]:
                self.initial = int(x)*600
                self.increment = int(y)*10
            case [x, y, z]:
                self.initial = int(x)*600
                self.increment = int(y)*10
                self.delay = int(z)*10
            case x:
                raise ValueError(f"Wrong Time format: '{x}'")
        self.white = self.initial
        self.black = self.initial
        self.sleep = sleep

    def tick(self, attr:str) -> None:
        """Ticks the clock

        Args:
            attr (str): Player to move
        """
        # Wait for the delay
        delay = 0
        while self.ticking and delay < self.delay:
            sleep(self.sleep)
            delay += self.sleep*10

        # Decrement the clock as time passes
        while self.ticking:
            sleep(self.sleep)
            setattr(self, attr, getattr(self, attr)-self.sleep*10)
            if getattr(self, attr) <= 0:
                break

        # Increment after every move
        setattr(self, attr, getattr(self, attr)+self.increment)

    def __call__(self) -> None:
        attr = "white" if self.turn == 0 else "black"
        self.ticking = False
        sleep(self.sleep)
        self.ticking = True
        self.turn = int(not self.turn)
        Thread(target=self.tick, args=(attr,)).start()

    def stop(self) -> None:
        """Stops the clock"""
        self.ticking = False

    def time(self) -> tuple[float, float]:
        """Returns the time left for both players"""
        return self.white/10, self.black/10

    def is_up(self) -> bool:
        """Returns a bool if any of the players' time is up"""
        return any(player <= 0 for player in self.time())


class Board:
    """The Chess Board

    Args:
        fen (str, optional): starting FEN. Defaults to the standard starting FEN.
        format_ (str, optional): Time format. Defaults to "5+0".

    Raises:
        ValueError: [description]
    """

    starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    def __init__(self, fen:str="", format_:str="5+0") -> None:
        if not fen:
            fen = Board.starting_fen
        Piece.board = self
        self.moves:list[str] = []
        self.prev = None
        self.move_fen:list[str] = []
        self.printer = pprint.PrettyPrinter(indent=4).pprint
        self.make_board(fen)
        self.clock = Clock(format_, self.turn)
        if (msg := self.is_over()):
            raise ValueError(msg)

    def make_board(self, fen:str) -> None:
        """Makes the board

        Args:
            fen (str): FEN for the board

        Raises:
            ValueError: if the fen is invalid
        """
        self.pieces:list[Piece] = []
        self.wking:King = None
        self.bking:King = None
        self.board = [[Square((i, j)) for i in range(8)] for j in range(8)]
        current = [0, 0]
        parts = fen.split()
        self.turn = 0 if parts[1] == "w" else 1
        self.en_passant = None if parts[3] == "-" else parts[3]
        self.half_moves = int(parts[4])
        self.full_moves = int(parts[5])
        for rank in parts[0].split("/")[::-1]:
            for square in rank:
                if square.isdigit():
                    current[1] += int(square)
                    continue
                match square:
                    case "r":
                        piece = Rook(1, current[::-1])
                    case "n":
                        piece = Knight(1, current[::-1])
                    case "b":
                        piece = Bishop(1, current[::-1])
                    case "q":
                        piece = Queen(1, current[::-1])
                    case "p":
                        piece = Pawn(1, current[::-1])
                    case "R":
                        piece = Rook(0, current[::-1])
                    case "N":
                        piece = Knight(0, current[::-1])
                    case "B":
                        piece = Bishop(0, current[::-1])
                    case "Q":
                        piece = Queen(0, current[::-1])
                    case "P":
                        piece = Pawn(0, current[::-1])
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

        self.wking.q = False
        self.wking.k = False
        self.bking.q = False
        self.bking.k = False

        if parts[2] == "-":
            self.wking.moved = True
            self.bking.moved = True
        else:
            for string in parts[2]:
                match string:
                    case "K":
                        self.wking.q = True
                    case "Q":
                        self.wking.k = True
                    case "k":
                        self.bking.k = True
                    case "q":
                        self.bking.q = True
                    case _:
                        raise ValueError("Illegal FEN")

    def castling(self) -> str:
        """Returns the castling rights for FEN generation"""
        wking = False
        wqueen = False
        bking = False
        bqueen = False
        if self.wking.moved:
            if self.bking.moved:
                return "-"
            wking = None
            wqueen = None
        if self.bking.moved:
            bking = None
            bqueen = None

        for piece in self.pieces:
            if piece.type == "R" and not piece.moved:
                if piece.color:
                    if piece.pos[0] > self.bking.pos[0] and self.bking.k and bking is not None:
                        bking = "k"
                    elif self.bking.q and bqueen is not None:
                        bqueen = "q"
                else:
                    if piece.pos[0] > self.wking.pos[0] and self.wking.k and wking is not None:
                        wking = "K"
                    elif self.wking.q and wqueen is not None:
                        wqueen = "Q"

        return "".join(list(filter(None, (wking, wqueen, bking, bqueen)))) or "-"

    def generate_fen(self) -> str:
        """Genrates FEN for given board"""
        fen = f"{self.generate_piece_fen()} {'b' if self.turn else 'w'} {self.castling()}"
        fen += f" {self.en_passant or '-'} {self.half_moves} {self.full_moves}"
        return fen

    def generate_piece_fen(self) -> str:
        """Returns the pieces for fen generation."""
        fen = ""
        empty = 0
        for rank in self.board[::-1]:
            for square in rank:
                if not square.piece:
                    empty += 1
                    continue
                if empty:
                    fen += str(empty)
                    empty = 0
                fen += str(square)
            if empty:
                fen += str(empty)
                empty = 0
            fen += "/"
        return fen[:-1]

    def print_board(self) -> None:
        """Prints the board"""
        self.printer(self.board[::-1])

    def __getitem__(self, index:str) -> Square:
        return self.board[int(index[1])-1][ord(index[0])-97]

    def __setitem__(self, index:str, value:Piece) -> None:
        if self.board[int(index[1])-1][ord(index[0])-97].piece is not None:
            raise ValueError("Already a piece there")
        self.board[int(index[1])-1][ord(index[0])-97].piece = value

    def __delitem__(self, index:str) -> None:
        piece = self.board[int(index[1])-1][ord(index[0])-97].piece
        if isinstance(piece, Piece):
            self.board[int(index[1])-1][ord(index[0])-97].piece = None
        else:
            raise ValueError("No piece to remove")

    def __repr__(self) -> str:
        return str(self.board)

    def can_play(self, move:str) -> bool:
        """Checks if the move can be played

        Args:
            move (str): The move

        Returns:
            bool: if the move can be played
        """
        if not check_UCI(move):
            return False
        piece = self[move[:2]].piece
        if isinstance(piece, Pawn) and piece.color == self.turn:
            b = piece.can_move(move[2:])
            if isinstance(b, tuple):
                return b[0]
            return b
        if isinstance(piece, Piece) and piece.color == self.turn:
            return piece.can_move(move[2:])
        return False

    def get_moves(self) -> list[str]:
        """Gets a list of all the moves without filtering checks"""
        moves = []
        for piece in self.pieces:
            if piece.color == self.turn:
                moves.extend(map(lambda n: piece.pos+n, piece.get_moves()))
        return moves

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
            if Square[self.wking.pos].is_attacked() or Square[self.bking.pos].is_attacked():
                pass
            else:
                filtered.append(move)
            self.reverse()
        return filtered

    def reverse(self) -> None:
        """Reverses a played move"""
        if not self.prev:
            raise IllegalMoveError(msg="No move has been played")
        self.make_board(self.prev)
        self.prev = None

    def play(self, move:str) -> None:
        """Play the given move

        Args:
            move (str): The move to play

        Raises:
            IllegalMoveError: If the move is Illegal
            ValueError: If the game is over
        """
        if not move in self.filter_checks(self.get_moves()):
            raise IllegalMoveError(msg="Illegal move")
        piece = self[move[:2]].piece
        self.move_fen.append(self.generate_piece_fen())
        before = self.en_passant
        self.half_moves += 1
        piece.move(move[2:])
        self.turn = int(not self.turn)
        if before and self.en_passant == before:
            self.en_passant = None
        self.moves.append(f"{self.full_moves}. {move}")
        print(f"{self.full_moves}. {move}")
        if piece.color:
            self.full_moves += 1
        self.clock()
        self.print_board()
        print(self.clock.time())
        error = self.is_over()
        if error:
            self.clock.stop()
            raise ValueError(error)

    def is_over(self) -> str:
        """Checks if the game is over

        Returns:
            str: Game over message
        """
        moves = self.get_moves()
        if not moves:
            return "Stalemate"
        if not self.filter_checks(moves):
            return "Checkmate"
        if self.half_moves >= 100:
            return "Draw by 50 move rule"
        if self.clock.is_up():
            if self.is_insufficient_material()[self.turn]:
                return "Draw by Time out"
            return "Time out!"
        if 3 in Counter(self.move_fen).values():
            return "Threefold repetition"
        if self.is_insufficient_material()[2]:
            return "Insufficient material"
        return ""

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
            if piece.color and piece is not self.bking:
                if piece.type in "BN":
                    black.append(piece)
                else:
                    bb = True
            elif piece is not self.wking and not piece.color:
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
            elif white and white[0].type == "B" or black and black[0].type == "B":
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

    def _old_play(self, move:str) -> None:
        before = self.en_passant
        self.prev = self.generate_fen()
        self[move[:2]].piece.move(move[2:])
        self.turn = int(not self.turn)
        if before and self.en_passant == before:
            self.en_passant = None

    def resign(self, color:int) -> None:
        """Resign the game"""
        raise ValueError(f"Resignation by {color}")

    def draw(self) -> None:
        """Draw the game"""
        raise ValueError("Draw on agreement")

    def abort(self) -> None:
        """Abort the game"""
        raise ValueError("Aborted")


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
            return move[1] in "27" and move[3] in "18" and move[4] in "qrnb"
    return False
