from dataclasses import dataclass

@dataclass
class SimplePosition:
    name: str
    lon: float
    lat: float = None

    @property
    def d(self):
        return self.__dict__

@dataclass
class SlotPosition:
    __slots__ = ['name', 'lon', 'lat']
    name: str
    lon: float
    lat: float

if __name__ == '__main__':
    a = SlotPosition(name='a', lon=5.0, lat=0.5)
    b = SimplePosition(name='a', lon=5.0, lat=0.5)
    print(b.d)

