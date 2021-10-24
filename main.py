from chess import standard as std, torpedo as tc


def main() -> None:
    # b = std.Board(std.generate_chess960_pieces() + " w - - 0 1", "0.05+0")
    b = tc.Board("8/8/P7/K7/8/k7/8/8 w KQkq - 0 3")

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
