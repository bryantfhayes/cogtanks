from .tank import Tank
from .tank import Direction

import random

class Simple(Tank):

    # OPTIONAL: If you want a custom name
    def __init__(self, name="SimpleTank"):
        Tank.__init__(self, name=name)

    def setup(self):
        """ This stuff runs once """
        self.facing = None
        self.dirs = [Direction.NORTH, Direction.EAST, Direction.WEST, Direction.SOUTH]

    def run(self):
        """ This happens every tick that you are not -cooling down- """
        #print("Results from last tick: {}".format(self.results))

        if self.facing is None:
            self.Face(Direction.EAST)
            self.facing = Direction.EAST
        # elif "type" in self.results and self.results["type"] == "detect":
        #     for f in self.results["found"]:
        #         if f[0] > 0 and f[1] == 0:
        #             self.Shoot()
        elif "type" in self.results and self.results["type"] != "move":
            self.Move(random.choice(self.dirs))
        else:
            self.Shoot()

        if random.randint(0,100) < 10:
            self.Detect()
        elif random.randint(0,100) < 20:
            self.Face(random.choice(self.dirs))
        
