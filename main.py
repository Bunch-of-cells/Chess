from chess import *


def main() -> None:
    b = CrazyHouse()

    while True:
        m = input("::>><<:: ")
        if m == "moves":
            print((moves := b.filter_checks(b.get_moves())), len(moves))
        elif m == "show":
            b.print_board()
            print(b.clock.time())
        elif m == "pieces":
            print(b.pieces)
        elif m == "fen":
            print(b.generate_fen())
        elif m == "abort":
            b.abort()
        elif m == "resign":
            b.resign(b.turn)
        elif m == "draw":
            b.draw()
        else:
            try:
                b.play(m)
            except std.IllegalMoveError as e:
                print(e)


if __name__ == "__main__":
    main()
