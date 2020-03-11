from enum import Enum
from collections import namedtuple
from math import hypot

class Vector2D(namedtuple('Vector2D', ('x', 'y'))):
    __slots__ = ()

    def __abs__(self):
        return type(self)(abs(self.x), abs(self.y))

    def __int__(self):
        return type(self)(int(self.x), int(self.y))

    def __add__(self, other):
        return type(self)(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return type(self)(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return type(self)(self.x * other, self.y * other)

    def __div__(self, other):
        return type(self)(self.x / other, self.y / other)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return str((self.x, self.y))

    def dot_product(self, other):
        return self.x * other.x + self.y * other.y

    def distance_to(self, other):
        """ uses the Euclidean norm to calculate the distance """
        return hypot((self.x - other.x), (self.y - other.y))

class Direction(Enum):
    NORTH = Vector2D(0, -1)
    EAST = Vector2D(1, 0)
    WEST = Vector2D(-1, 0)
    SOUTH = Vector2D(0, 1)

"""
@brief Tank base class. Users will override this class to customize their tank logic.
"""
class Tank():
    def __init__(self):
        self._cooldown = 0
        self._intent = None
        self._hp = 2
        self._pos = Vector2D(0, 0)
        self._facing = Direction.NORTH
        self.results = {}

    def setup(self):
        """ Runs once when simulation starts """
        pass

    def run(self):
        """ Main run function that will execute each tick, unless the cooldown is > 0 """
        pass

    #
    # Public API
    #

    def Move(self, dir):
        self._intent = { "type" : "move" , "direction" : dir, "cooldown" : 2 }

    def Shoot(self):
        self._intent = { "type" : "shoot", "cooldown" : 2 }

    def Face(self, dir):
        self._intent = { "type" : "face" , "direction" : dir, "cooldown" : 1 }

    def Detect(self):
        self._intent = { "type" : "detect", "cooldown" : 4 }