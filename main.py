from chess import standard as std


def main() -> None:
    b = std.Board("8/3k4/8/8/5n2/6B1/2K5/8 w - - 0 1", "0.05+0")

    while True:
        m = input("::>><<:: ")
        if m == "moves":
            print((moves := b.filter_checks(b.get_moves())), len(moves))
        elif m == "show":
            b.print_board()
            print(b.clock.time())
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
