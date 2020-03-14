from .tank import Tank
from .tank import Direction
from .tank import Vector2D

import random

class Bfhmarki(Tank):

    # OPTIONAL: If you want a custom name
    def __init__(self, name="BFHMarkI"):
        Tank.__init__(self, name=name)

    def setup(self):
        """ This stuff runs once """
        self.facing = None
        self.tick = 1
        self.last_cooldown = 0
        self.last_move_dir = None
        self.pos = Vector2D(-1, -1)
        self.dirs = [Direction.NORTH, Direction.EAST, Direction.WEST, Direction.SOUTH]

    def IntentWrapper(self, intent, dir=None):
        if intent == "shoot":
            self.Shoot()
            self.last_cooldown = 2
        elif intent == "move":
            self.Move(dir)
            self.last_cooldown = 2
            self.last_move_dir = dir
            if self.pos.x != -1 and self.pos.y != -1:
                self.pos += dir.value
        elif intent == "detect":
            self.Detect()
            self.last_cooldown = 4
        elif intent == "face":
            self.Face(dir)
            self.last_cooldown = 1

    def initialize(self):
        if self.tick == 1:
            self.IntentWrapper("shoot")
            return

        if self.tick == 3:
            self.IntentWrapper("face", Direction.SOUTH)
            return

        # Go to (0, 0) to establish where you are
        if self.pos.x == -1:
            self.IntentWrapper("move", Direction.WEST)
            return

        elif self.pos.y == -1:
            self.IntentWrapper("move", Direction.NORTH)
            return

    def run(self):
        """ This happens every tick that you are not -cooling down- """

        # Keep track of the current tick
        self.tick += self.last_cooldown
        self.last_cooldown = 0
        
        if "type" in self.results:
            if "move" in self.results["type"]:
                if "OUT_OF_BOUNDS" in self.results["status"] and self.last_move_dir == Direction.WEST:
                    self.pos = Vector2D(0, self.pos.y)
                elif "OUT_OF_BOUNDS" in self.results["status"] and self.last_move_dir == Direction.NORTH:
                    self.pos = Vector2D(self.pos.x, 0)

        # Get initial coords
        if self.pos.x == -1 or self.pos.y == -1:
            self.initialize()
            return
        else:
            self.IntentWrapper("shoot")

        # Move left and right in top row and shoot down
        if random.randint(0,100) < 10:
            self.IntentWrapper("move", random.choice([Direction.WEST, Direction.EAST]))
        
