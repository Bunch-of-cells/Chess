from chess import gui
import socket
import threading

class Client:
    PORT = 5050
    SERVER = "127.0.1.1"
    ADDR = (SERVER, PORT)
    HEADER = 64
    DISCONNECT = "!DISCONNECT"
    FORMAT = "utf-8"

    def __init__(self, func, fen) -> None:
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDR)
        self.fen = None
        self.flag = True
        threading.Thread(target=self.start, args=(func)).start()
        self.send(fen)

    def start(self, func) -> None:
        while self.flag:
            func(self.client.recv(2048).decode(self.FORMAT))

    def send(self, msg:str) -> None:
        message = msg.encode(self.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b" " * (self.HEADER - len(send_length))
        self.client.send(send_length)
        self.client.send(message)

    def disconnect(self) -> None:
        self.send(self.DISCONNECT)
        self.flag = False


class Standard:
    starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    def __init__(self, user1, user2, fen="") -> None:
        if not fen:
            fen = Standard.starting_fen
        self.user1 = user1
        self.user2 = user2
        
        self.client = Client(self.move)
        self.create_board(fen)
        self.client.disconnect()

    def create_board(self, fen) -> None:
        self.root = gui.Tk()
        self.root.resizable(False, False)
        self.frame = gui.Frame(self.root)
        self.img = gui.PhotoImage(file="/home/alumin112/Desktop/Python Projects/Chess/chess/assets/board.png")
        gui.Label(self.frame, image=self.img).pack()
        gui.Piece.root = self.root
        self.start(fen)
        self.frame.pack()
        self.root.mainloop()

    def start(self, fen) -> None:
        current = [0, 0]
        for rank in fen[0].split("/")[::-1]:
            for square in rank:
                if square.isdigit():
                    current[1] += int(square)
                    continue
                match square:
                    case "r":
                        img = "brook.png"
                    case "n":
                        img = "bknight.png"
                    case "b":
                        img = "bbishop.png"
                    case "q":
                        img = "bqueen.png"
                    case "p":
                        img = "bpawn.png"
                    case "R":
                        img = "wrook.png"
                    case "N":
                        img = "wknight.png"
                    case "B":
                        img = "wbishop.png"
                    case "Q":
                        img = "wqueen.png"
                    case "P":
                        img = "wpawn.png"
                    case "k":
                        img = "bking.png"
                    case "K":
                        img = "wking.png"
                    case _:
                        raise ValueError("Illegal FEN")
                gui.Piece(current[1], (current[0]-4)*-1 + 3, img, repr(square.piece))
                current[1] += 1
            current[0] += 1
            current[1] = 0

    def move(self, fen:str) -> None:
        for piece in gui.Piece.pieces:
            piece.delete()
        self.start(fen)
