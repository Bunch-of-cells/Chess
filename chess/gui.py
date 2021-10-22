from tkinter import Label, PhotoImage, Button, SUNKEN

class Piece(Label):
    root = None
    move = None
    buttons = []
    pieces:list["Piece"] = []

    def __init__(self, file:int, rank:int, img:str, type_:str,**kwargs) -> None:
        self.file = file
        self.rank = rank
        self.orgX = file *100
        self.orgY = rank *100
        self.type = type_
        img = "/home/alumin112/Desktop/Python Projects/Chess/chess/assets/" + img
        self.photo = PhotoImage(file=img)
        super().__init__(self.root, image=self.photo,**kwargs)
        self.place(x=file*100, y=rank*100)
        self.bind("<Button-1>", self.drag_start)
        self.bind("<Button-3>", self.delete)
        self.bind("<B1-Motion>", self.drag_move)
        self.bind("<B1-ButtonRelease>", self.drag_stop)
        Piece.pieces.append(self)

    def drag_start(self, event) -> None:
        self.startX = event.x
        self.startY = event.y

    def delete(self, _) -> None:
        self.destroy()
        Piece.pieces.remove(self)
        del self

    def drag_move(self, event) -> None:
        x = self.winfo_x() - self.startX + event.x
        y = self.winfo_y() - self.startY + event.y
        if 0 < x < self.root.winfo_width() and 0 < y < self.root.winfo_height():
            self.place(x=x, y=y)

    def drag_stop(self, _) -> None:
        posi = round(self.winfo_x()/100)*100, round(self.winfo_y()/100)*100
        pos = round(self.winfo_x()/100), (round(self.winfo_y()/100) - 4)*-1 + 3
        orgpos = self.orgX//100, (self.orgY//100 - 4)*-1 + 3
        if pos != orgpos:
            move = f"{chr(orgpos[0]+97)}{orgpos[1]+1}{chr(pos[0]+97)}{pos[1]+1}"
            if Piece.board.can_play(move):
                if self.type == "P" and move[3] in "18":
                    self.orgX, self.orgY = posi
                    choice = 1 if move[3] == "8" else -1
                    for val, name in enumerate(["rook", "queen", "bishop", "knight"]):
                        img = f"/home/alumin112/Desktop/Python Projects/Chess/chess/assets/{'b' if Piece.board[move].piece.color else 'w'}{name}.png"
                        photo = PhotoImage(file=img)
                        button = Button(Piece.root, font=("Arial", 20), relief=SUNKEN, bd=2,
                                    command=lambda n=name:self.radio(move, n, 
                                    Piece.board[move].piece.color), image=photo)
                        button.photo = photo
                        Piece.buttons.append(button)
                        button.place(x=self.orgX, y=self.orgY+(choice* (100+ val*100)))

                elif not Piece.buttons:
                    self.orgX, self.orgY = posi
                    Piece.board.play(move)

        self.place(x=self.orgX, y=self.orgY)

    def radio(self, move:str, name:str, color:int) -> None:
        img = f"/home/alumin112/Desktop/Python Projects/Chess/chess/assets/{'b' if color else 'w'}{name}.png"
        self.photo = PhotoImage(file=img)
        self.config(image=self.photo)
        self.type = name[(1 if name=="knight" else 0)].upper()
        Piece.board.play(move+name[(1 if name=="knight" else 0)])
        for button in self.buttons:
            button.destroy()
        Piece.buttons = []
