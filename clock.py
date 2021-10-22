from threading import Thread, active_count
from time import sleep

class Clock:
    def __init__(self, format:str, turn:int=0, sleep:float=0.1) -> None:
        time = format.split("+")
        self.turn = turn
        self.increment = 0
        self.delay = 0
        self.ticking = False
        match time:
            case [x]:
                self.initial = int(x)
            case [x, y]:
                self.initial = int(x)
                self.increment = int(y)
            case [x, y, z]:
                self.initial = int(x)
                self.increment = int(y)
                self.delay = int(z)
            case x:
                raise ValueError(f"Wrong Time format: '{x}'")
        self.white = self.initial*10
        self.black = self.initial*10
        self.sleep = sleep

    def tick(self, turn:int) -> None:
        attr = "white" if turn == 0 else "black"
        while self.ticking:
            sleep(self.sleep)
            setattr(self, attr, getattr(self, attr)+self.sleep*10)

    def __call__(self) -> None:
        self.ticking = False
        sleep(self.sleep)
        self.ticking = True
        self.turn = int(not self.turn)
        Thread(target=self.tick, args=(self.turn, )).start()

    def end(self) -> None:
        self.ticking = False

    def time(self) -> tuple[float, float]:
        return self.white/10, self.black/10

    def is_up(self) -> bool:
        return any(self.time() <= 0)

clock = Clock("5+0")
while True:
    input()
    clock()
    assert active_count() == 2, "More threads"
    print(clock.time())
