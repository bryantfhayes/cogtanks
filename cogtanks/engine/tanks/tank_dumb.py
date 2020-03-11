from .tank import Tank
from .tank import Direction

import random

class Dumb(Tank):
    # OPTIONAL: If you want a custom name
    def __init__(self, name="DumbTank"):
        Tank.__init__(self, name=name)

    def setup(self):
        """ This stuff runs once """
        self.facing = None
        self.dirs = [Direction.NORTH, Direction.EAST, Direction.WEST, Direction.SOUTH]

    def run(self):
        """ This happens every tick that you are not -cooling down- """
        pass