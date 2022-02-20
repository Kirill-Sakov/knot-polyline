"""Module of vector realization."""
import math


class Vec2d:
    """Realisation 2d Vector."""
    def __init__(self, x, y):
        self.x: float = x
        self.y: float = y

    def __str__(self):
        return f'{{x: {self.x}, y: {self.y}}}'

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Vec2d(x, y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return Vec2d(x, y)

    def __mul__(self, num):
        x = self.x * num
        y = self.y * num
        return Vec2d(x, y)

    def __len__(self) -> float:
        """Vector length"""
        x = self.x ** 2
        y = self.y ** 2
        return math.sqrt(x + y)

    def int_pair(self) -> tuple:
        """Return tuple with current coordinates."""
        return self.x, self.y

    def reverse_x(self):
        self.x = -self.x

    def reverse_y(self):
        self.y = -self.y