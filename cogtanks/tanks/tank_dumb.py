from .tank import Tank
from .tank import Direction

import random

class Dumb(Tank):
    def __repr__(self):
        """ OPTIONAL: Override name of your Tank! """
        return "D"

    def setup(self):
        """ This stuff runs once """
        self.facing = None
        self.dirs = [Direction.NORTH, Direction.EAST, Direction.WEST, Direction.SOUTH]

    def run(self):
        """ This happens every tick that you are not -cooling down- """
        pass