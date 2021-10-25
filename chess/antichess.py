"""Contains the code for antichess variant"""

from chess import standard as std


class King(std.King):
    """King piece

    Args:
        color (int): color of the piece
        position (tuple[int, int]): Position of the piece in a numeric form.
    """
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

    def can_move(self, move:str) -> bool:
        if len(move) == 2 and not self.is_occupied(move):
            if self.can_move_straight(move, True) or self.can_move_diagonally(move, True):
                return True


class Pawn(std.Pawn):
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
                for k in "rnqbk":
                    move = chr(ord(self.pos[0])+i) + str(int(self.pos[1])+j)+k
                    if std.check_UCI(self.pos+move):
                        res = self.can_move(move)
                        if isinstance(res, tuple):
                            if res[0]:
                                moves.append(move)
                        elif res:
                            moves.append(move)
            for l in "rnqbk":
                move = self.pos[0]+ str(int(self.pos[1])+i)+l
                if std.check_UCI(self.pos+move):
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
                del std.Piece.board[self.pos]
                self.pos = move
                std.Piece.board[move].piece = self
            case (True, std.Piece() as piece):
                del std.Piece.board[self.pos]
                del std.Piece.board[piece.pos]
                self.pos = move
                std.Piece.board[self.pos].piece = self
                std.Piece.board.pieces.remove(piece)

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
                    case "k":
                        p = King(self.color, (ord(move[0])-97, int(move[1])-1))
                std.Piece.board[move].piece = p
                std.Piece.board.pieces.append(p)
                del self

            case (True, std.Piece() as piece, False):
                del std.Piece.board[self.pos]
                del std.Piece.board[piece.pos]
                self.pos = move
                std.Piece.board[self.pos].piece = self
                std.Piece.board.pieces.remove(piece)

            case(True, True):
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
                    case "k":
                        p = King(self.color, (ord(move[0])-97, int(move[1])-1))
                std.Piece.board[move].piece = p
                std.Piece.board.pieces.append(p)
                del self

            case(True, y):
                del std.Piece.board[self.pos]
                self.pos = move
                std.Piece.board[self.pos].piece = self
                std.Piece.board.en_passant = y
            case _:
                raise std.IllegalMoveError(self, move)
        
        std.Piece.board.half_moves = 0


class Board(std.Board):
    """The Chess Board

    Args:
        fen (str, optional): starting FEN. Defaults to the standard starting FEN.
        format_ (str, optional): Time format. Defaults to "5+0".
    """

    starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - 0 1"

    def filter_checks(self, moves:list[str]) -> list[str]:
        """Filters the moves to check captures

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
            bpieces = len(self.pieces)
            self._old_play(move)
            if len(self.pieces) != bpieces:
                filtered.append(move)
            self.reverse()
        if not filtered:
            filtered = moves
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
                        piece = King(1, current[::-1])
                    case "K":
                        piece = King(0, current[::-1])
                    case _:
                        raise ValueError("Illegal FEN")
                self.board[current[0]][current[1]].piece = piece
                self.pieces.append(piece)
                current[1] += 1
            current[0] += 1
            current[1] = 0
  
    def make_board(self, fen:str) -> None:
        """Makes the board

        Args:
            fen (str): FEN for the board
        """
        self.pieces:list[std.Piece] = []
        self.board = [[std.Square((i, j)) for i in range(8)] for j in range(8)]
        parts = fen.split()
        self.turn = 0 if parts[1] == "w" else 1
        self.en_passant = None if parts[2] == "-" else parts[3]
        self.half_moves = int(parts[3])
        self.full_moves = int(parts[4])
        self.make_pieces(parts[0])

    def is_over(self) -> None:
        """Ends the game if the game is over"""
        msg = ""
        if self.clock.is_up():
            msg = "Time out!"
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

    def generate_fen(self) -> str:
        """Genrates FEN for given board"""
        fen = f"{self.generate_piece_fen()} {'b' if self.turn else 'w'}"
        fen += f" {self.en_passant or '-'} {self.half_moves} {self.full_moves}"
        return fen 


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
            return move[1] in "27" and move[3] in "18" and move[4] in "qrnbk"
    return False
