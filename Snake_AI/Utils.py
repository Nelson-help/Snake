class Point:
    x: int
    y: int

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __eq__(self, other: "Point") -> bool:
        return self.x == other.x and self.y == other.y

    def distanceTo(self, other: "Point") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def directionTo(self, other: "Point") -> "Point":
        return Point(other.x - self.x, other.y - self.y)

    def toTuple(self) -> tuple:
        return (self.x, self.y)