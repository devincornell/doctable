
import dataclasses

@dataclasses.dataclass
class Test:
    x: int
    y: int

class TestSlot:
    __slots__ = ['x', 'y']
    def __init__(self, x, y):
        self.x = x
        self.y = y


if __name__ == '__main__':
    t = Test(0, 0)
    print(t.__dict__)
    ts = TestSlot(0, 0)
    print(t.__dict__)











