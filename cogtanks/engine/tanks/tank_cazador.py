from .tank import Tank
from .tank import Direction

import math

# wander around. shoot when you collide with someone.
class Cazador(Tank):

    def __init__(self, name="Cazador"):
        Tank.__init__(self, name=name)

    def setup(self):
        self.facing = None
        self.moveDir = None
        self.moveQueue = []
        self.moveQueue.append(lambda : self.Detect())

    def run(self):
        if len(self.moveQueue) > 0:
            self.moveQueue[0]()
            self.moveQueue = self.moveQueue[1:]
        elif self.results["type"] == "detect":
            # find which loc, when projected, is closest to us
            nearestLoc = self.results["found"][0]
            nearestTankDist = min(math.fabs(nearestLoc[0]), math.fabs(nearestLoc[1]))
            for loc in self.results["found"][1:]:
                nearerAxis = min(math.fabs(loc[0]), math.fabs(loc[1]))
                if nearerAxis < nearestTankDist:
                    nearestLoc = loc
                    nearestTankDist = nearerAxis
            # move to be in line with nearest tank
            if math.fabs(nearestLoc[0]) < math.fabs(nearestLoc[1]):
                # move along x-axis
                if nearestLoc[0] > 0:
                    #move right
                    self.moveDir = Direction.EAST
                elif nearestLoc[0] < 0:
                    #move left
                    self.moveDir = Direction.WEST
                #else:
                    #we're in line! FIRE!
                #which way do we face?
                if nearestLoc[1] > 0:
                    #face down
                    self.facing = Direction.NORTH
                else:
                    #face up
                    self.facing = Direction.SOUTH
            else:
                # move along y-axis
                if nearestLoc[1] > 0:
                    #move down
                    self.moveDir = Direction.NORTH
                elif nearestLoc[1] < 0:
                    #move up
                    self.moveDir = Direction.SOUTH
                #else:
                    #we're in line! FIRE!
                #which way do we face?
                if nearestLoc[0] > 0:
                    #face left
                    self.facing = Direction.WEST
                else:
                    #face right
                    self.facing = Direction.EAST
            self.Face(self.facing)
            for _ in range(int(nearestTankDist)):
                self.moveQueue.append(lambda : self.Move(self.moveDir))
            self.moveQueue.append(lambda : self.Shoot())
            self.moveQueue.append(lambda : self.Shoot())
            self.moveQueue.append(lambda : self.Detect())
