"""Contains the code for the Crazyhouse variant"""

from chess import standard as std


class Piece:
    def delete(self) -> None:
        """Deletes the piece"""
        del std.Piece.board[self.pos]
        if self in std.Piece.board.pieces:
            std.Piece.board.pieces.remove(self)
        elif self in std.Piece.board.wpocket:
            std.Piece.board.wpocket.remove(self)
        elif self in std.Piece.board.bpocket:
            std.Piece.board.bpocket.remove(self)

    def place(self, pos):
        for no, square in std.SquareMeta.squares.items():
            if no == pos:
                square.piece = self
                self.pos = no
                std.Piece.board.pieces.append(self)
                break


class King(Piece, std.King):pass
class Queen(Piece, std.Queen):pass
class Bishop(Piece, std.Bishop):pass
class Rook(Piece, std.Rook):pass
class Knight(Piece, std.Knight):pass


class Pawn(Piece, std.Pawn):
    def move(self, move:str) -> None:
        """A pawn move"""
        match self.can_move(move):
            case True:
                del std.Piece.board[self.pos]
                self.pos = move
                std.Piece.board[move].piece = self
            case (True, std.Piece() as piece):
                piece.delete()
                del std.Piece.board[self.pos]
                self.pos = move
                std.Piece.board[self.pos].piece = self

            case (True, std.Piece() as piece, True):
                self.delete()
                piece.delete()
                match move[2]:
                    case "q":
                        p = std.Queen(self.color, (ord(move[0])-97, int(move[1])-1))
                    case "r":
                        p = std.Rook(self.color, (ord(move[0])-97, int(move[1])-1))
                    case "n":
                        p = std.Knight(self.color, (ord(move[0])-97, int(move[1])-1))
                    case "b":
                        p = std.Bishop(self.color, (ord(move[0])-97, int(move[1])-1))
                p.promoted = True
                std.Piece.board[move].piece = p
                std.Piece.board.pieces.append(p)
                del self

            case (True, std.Piece() as piece, False):
                piece.delete()
                del std.Piece.board[self.pos]
                self.pos = move
                std.Piece.board[self.pos].piece = self

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
                p.promoted = True
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

    starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR/PPP w KQkq - 0 1"

    def make_board(self, fen:str) -> None:
        """Makes the board

        Args:
            fen (str): FEN for the board
        """
        self.pieces:list[std.Piece] = []
        self.wking:std.King = None
        self.bking:std.King = None
        self.wpocket:list[std.Piece] = []
        self.bpocket:list[std.Piece] = []
        self.board = [[std.Square((i, j)) for i in range(8)] for j in range(8)]
        parts = fen.split()
        self.turn = 0 if parts[1] == "w" else 1
        self.en_passant = None if parts[3] == "-" else parts[3]
        self.half_moves = int(parts[4])
        self.full_moves = int(parts[5])
        self.make_pieces(parts[0])
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

    def make_pieces(self, pieces:str) -> None:
        """Makes the board

        Args:
            pieces (str): piece fen

        Raises:
            ValueError: If the passed piece fen is invalid
        """
        current = [0, 0]
        p = pieces.split("/")
        pocket = p.pop() if len(p) == 9 else ""
        for rank in p[::-1]:
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
                        piece = std.King(1, current[::-1])
                        self.bking = piece
                    case "K":
                        if self.wking:
                            raise ValueError("More than 1 White King")
                        piece = std.King(0, current[::-1])
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

        for p in pocket:
            match p:
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
                case _:
                    raise ValueError("Illegal FEN")
            if p.islower():
                self.bpocket.append(piece)
            else:
                self.wpocket.append(piece)

    def generate_fen(self) -> str:
        """Genrates FEN for given board"""
        fen = f"{self.generate_piece_fen()}/{self.generate_pocket_fen()} {'b' if self.turn else 'w'} "
        fen += f"{self.castling()} {self.en_passant or '-'} {self.half_moves} {self.full_moves}"
        return fen

    def generate_pocket_fen(self) -> str:
        ret = ""
        for piece in self.wpocket + self.bpocket:
            ret += str(piece)
        return ret

    def get_moves(self) -> list[str]:
        """Gets a list of all the moves without filtering checks"""
        if self.g_moves:
            if self.g_moves[0] == [self.turn, self.full_moves]:
                return self.g_moves[1]
        moves = []
        for piece in self.pieces:
            if piece.color == self.turn:
                moves.extend(map(lambda n: piece.pos+n, piece.get_moves()))
        for piece in getattr(self, f"{'b' if self.turn else 'w'}pocket"):
            for no, square in std.SquareMeta.squares.items():
                if square.piece is None:
                    if isinstance(piece, Pawn) and no[1] in "18":
                        pass
                    elif hasattr(piece, "promoted"):
                        pass
                    else:
                        moves.append(f"@{str(piece)}{no}")
        self.g_moves = [[self.turn, self.full_moves], moves]
        return moves

    def _old_play(self, move:str) -> None:
        before = self.en_passant
        self.prev = self.generate_fen()
        if move[0] == "@":
            piece = None
            for piece in getattr(self, f"{'b' if self.turn else 'w'}pocket"):
                if str(piece) == move[1]:
                    getattr(self, f"{'b' if self.turn else 'w'}pocket").remove(piece)
                    break
            piece.place(move[2:])
        else:
            self[move[:2]].piece.move(move[2:])
        self.turn = int(not self.turn)
        if before and self.en_passant == before:
            self.en_passant = None

    def play(self, move:str) -> None:
        """Play the given move

        Args:
            move (str): The move to play

        Raises:
            IllegalMoveError: If the move is Illegal
            ValueError: If the game is over
        """
        if not move in self.filter_checks(self.get_moves()):
            raise std.IllegalMoveError(msg="Illegal move")
        self.move_fen.append(self.generate_piece_fen())
        before = self.en_passant
        self.half_moves += 1
        if move[0] == "@":
            for piece in getattr(self, f"{'b' if self.turn else 'w'}pocket"):
                if str(piece) == move[1]:
                    getattr(self, f"{'b' if self.turn else 'w'}pocket").remove(piece)
                    break
            piece.place(move[2:])
        else:
            piece = self[move[:2]].piece
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
        print(self.wpocket)
        print(self.bpocket)
        self.is_over()

    def is_over(self) -> None:
        """Ends the game if the game is over"""
        msg = ""
        if self.clock.is_up():
            if (not getattr(self, f"{'b' if self.turn else 'w'}pocket")) and self.is_insufficient_material()[self.turn]:
                msg = "Draw by Time out"
            msg = "Time out!"
        elif not (moves := self.get_moves()):
            msg = "Stalemate"
        elif not self.filter_checks(moves):
            msg = "Checkmate"
        elif self.half_moves >= 100:
            msg = "Draw by 50 move rule"
        elif 3 in std.Counter(self.move_fen).values():
            msg = "Threefold repetition"
        elif not (self.wpocket and self.bpocket) and self.is_insufficient_material()[2]:
            msg = "Insufficient material"
        if msg:
            self.clock.stop()
            print(msg)
            exit()

    def __getitem__(self, index:str) -> std.Square:
        # if not check_UCI(index):
        #     return None
        return self.board[int(index[1])-1][ord(index[0])-97]

    def __setitem__(self, index:str, value:std.Piece) -> None:
        # if not check_UCI(index):
        #     return None
        if self.board[int(index[1])-1][ord(index[0])-97].piece is not None:
            raise ValueError("Already a piece there")
        self.board[int(index[1])-1][ord(index[0])-97].piece = value

    def __delitem__(self, index:str) -> None:
        if not check_UCI(index):
            return None
        piece = self.board[int(index[1])-1][ord(index[0])-97].piece
        if isinstance(piece, std.Piece):
            self.board[int(index[1])-1][ord(index[0])-97].piece = None
        else:
            raise ValueError("No piece to remove")



def check_UCI(move:str) -> bool:
    """Checks if the move is correct or not

    Args:
        move (str): The move to check

    Returns:
        bool: if the move is according to UCI notation or not
    """
    return len(move) == 2 and move[1] in "12345678" and move[0] in "abcdefgh"
