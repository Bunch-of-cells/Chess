import socket
import threading
from chess.standard import Board


class Server:
    """
    The Server

    Args:
        server (str): Server ip on which the server is hosted, default is your ipv4
        post (int): Port on which the server is hosted, default is 5050
    """

    port = 5050
    server = socket.gethostbyname(socket.gethostname())

    HEADER = 64
    DISCONNECT = "!DISCONNECT"
    FORMAT = "utf-8"

    fen :None|int|str = None
    board :None|Board = None

    c1 = None
    c2 = None

    def __init__(self, server:str|None=None, port:int|None=None) -> None:
        self.server = server or Server.server
        self.port = port or Server.port
        self.addr = (server, port)

        print("[STARTING] server is starting...")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(self.addr)
        server.listen()
        print(f"[LISTENING] server is listening on {self.server}")

        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()
            print(f"Active Connections: {threading.active_count() - 1}")

    def handle_client(self, conn, addr) -> None:
        """Handles a new client connection

        Args:
            conn : The client socket
            addr (str): the address of the connection
        """
        print(f"[NEW CONNECTION] {addr} connected.")
        print(type(addr))
        if Server.fen == 123:
            raise Exception("Too many players")

        # Get FEN
        msg_length = conn.recv(self.HEADER).decode(self.FORMAT)
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(self.FORMAT)
        if msg == Server.fen:
            Server.c2 = conn
            Server.fen = 123
            Server.board = Board(msg)
        else:
            if Server.c1:
                Server.c1.close()
            Server.c1 = conn
            Server.fen = msg

        while Server.c2:
            msg_length = conn.recv(self.HEADER).decode(self.FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(self.FORMAT)
                if msg == self.DISCONNECT:
                    print(f"[DISCONNECTED] {addr} disconnected.")
                    print(f"Active Connections: {threading.active_count() - 1}")
                    break
                print(f"[{addr}] {msg}")
                Server.board.play(msg)
                self.send_fen()

        conn.close()
        if conn is Server.c2:
            Server.c2 = None
        else:
            Server.c1 = None

    def send_fen(self) -> None:
        message = Server.board.generate_piece_fen().encode(self.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b" " * (self.HEADER - len(send_length))
        Server.c1.send(send_length)
        Server.c1.send(message)
        Server.c2.send(send_length)
        Server.c2.send(message)


Server()