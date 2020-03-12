from tanks.tank import Tank
from tanks.tank import Direction
from tanks.tank import Vector2D
import os
import random
import time
import logging
import json

logging.basicConfig(filename='cogtanks.log', filemode='w', format='%(message)s', level=logging.DEBUG)

PUBLIC_ENUMS = {
    'Direction': Direction,
    # ...
}
class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) in PUBLIC_ENUMS.values():
            return {"__enum__": str(obj)}
        return json.JSONEncoder.default(self, obj)

def as_enum(d):
    if "__enum__" in d:
        name, member = d["__enum__"].split(".")
        return getattr(PUBLIC_ENUMS[name], member)
    else:
        return d

"""
@brief CTArena represents the arean in which the tanks will fight!

Map indexes

 0  1  2  .  .  .  X
0
1
2
.
.
.
Y
"""
class CTArena():
    def __init__(self, width, height, tanks):
        self.entities = []
        self.width = width
        self.height = height

        for tank in tanks:
            self.add_tank_at_random_position(tank)

    def add_tank_at_random_position(self, tank):
        """ Add a tank to a random position on the map """
        while True:
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            pos = Vector2D(x, y)
            if len(self.get_entities_for_pos(pos)) == 0:
                tank._pos = pos
                self.entities.append(tank)
                break

    def print_map(self):
        """ Print the map in a way that makes sense """
        return
        m = [[[] for x in range(self.width)] for y in range(self.height)]

        for entity in self.entities:
            m[entity._pos.y][entity._pos.x].append(entity)

        for row in m:
            print(row)

    def get_entities_for_pos(self, pos):
        """ Return entities at position (x, y) """
        entities = []
        for entity in self.entities:
            if entity._pos == pos:
                entities.append(entity)
        
        return entities

"""
@brief CTBattle is the cogtank battle simulation. It requires CTArean and Tank objects.
"""
class CTBattle():
    def __init__(self, width=12, height=9, max_ticks=1000, ticks_per_second=3):
        self.curtick = 0
        self.ticks_per_second = ticks_per_second
        self.running = False
        self.max_ticks = max_ticks
        self.log = { "ticks" : [], "gameinfo" : {}}

        # Load all tanks
        tanks = self.load_all_tanks()

        # Create an arena
        self.arena = CTArena(width, height, tanks)

    def writelog(self):
        """ Write output log """
        with open("tickdata.json", "w") as fp:
            fp.write(json.dumps(self.log, cls=EnumEncoder))

    def start(self):
        """ Start a simulation """
        self.running = True

        # Store JSON game data
        self.gameinfo = {"starting_tank_count" : len(self.arena.entities), "starting_tanks" : list(map(str, self.arena.entities)), "ticks_per_second" : self.ticks_per_second, "max_ticks" : self.max_ticks, "width" : self.arena.width, "height" : self.arena.height}
    
        print("Starting simulation...")
        print(self.gameinfo)

        for tank in self.arena.entities:
            tank.setup()

        while self.running:
            self.tick()
            time.sleep(1 / self.ticks_per_second)
        else:
            self.gameinfo["total_ticks"] = self.curtick
            self.log["gameinfo"] = self.gameinfo
            self.writelog()

    def tick(self):
        """ This method is called at a steady interval and moves the game forward. """
        self.curtick += 1
        ticklog = {"tick" : self.curtick}
        ticklog["tanks"] = {}
        ticklog["deaths"] = []

        logging.info("Running tick: {}".format(self.curtick))

        # First pass: Gather intents and clea results from last tick
        for tank in self.arena.entities:
            ticklog["tanks"][str(tank)] = {}
            ticklog["tanks"][str(tank)]["cooldown"] = tank._cooldown
            ticklog["tanks"][str(tank)]["facing"] = tank._facing
            ticklog["tanks"][str(tank)]["last_result"] = tank.results
            ticklog["tanks"][str(tank)]["pos"] = {"x" : tank._pos.x, "y" : tank._pos.y}
            if tank._cooldown > 0:
                tank._cooldown -= 1
            else:
                tank._intent = None
                tank.run()
                tank.results = {}
            
            ticklog["tanks"][str(tank)]["intent"] = tank._intent

        # Second pass: Shoot and Instant actions
        for tank in self.arena.entities:
            if tank._intent is not None:
                intenttype = tank._intent["type"]
                if intenttype == "shoot":
                    tank.results = self._shoot(tank)
                    if tank.results["target"] is not None:
                        ticklog["tanks"][tank.results["target"]]["hit"] = True
        
        # Pass 2.5 - Log HP
        for tank in self.arena.entities:
            # Log hp AFTER shooting occurs since it is instant
            ticklog["tanks"][str(tank)]["hp"] = tank._hp

        # Third pass: Move, Face, Detect
        for tank in self.arena.entities:
            if tank._intent is not None:
                intenttype = tank._intent["type"]
                if intenttype == "move":
                    tank.results = self._move(tank, tank._intent["direction"])
                elif intenttype == "face":
                    tank.results = self._face(tank, tank._intent["direction"])
                elif intenttype == "detect":
                    tank.results = self._detect(tank)

        # Fourth pass: clear all intents and add cooldowns
        for tank in self.arena.entities:
            if tank._intent is not None:
                tank._cooldown += tank._intent["cooldown"]
                tank._intent = None
            if tank._hp <= 0:
                logging.info("{} was killed!".format(str(tank)))
                ticklog["deaths"].append(str(tank))

        # Get rid of dead tanks
        self.arena.entities = [e for e in self.arena.entities if e._hp > 0]

        # DEBUG: Log the map
        self.arena.print_map()

        # Log tick info
        self.log["ticks"].append(ticklog)

        # Termination conditions
        if len(self.arena.entities) == 1:
            logging.info("{} WON!".format(str(self.arena.entities[0])))
            print("{} WON!".format(str(self.arena.entities[0])))
            self.running = False
            return
        elif len(self.arena.entities) == 0:
            logging.info("NOBODY WON!")
            print("NOBODY WON!")
            self.running = False
            return
        elif self.curtick >= self.max_ticks:
            self.running = False
            logging.info("MAX TICK REACHED - NOBODY WON!")
            print("MAX TICK REACHED - NOBODY WON!")
            return

        # Making it here means we will probably run another tick
        return

    def load_all_tanks(self):
        """ Load all tanks from: tanks/tank_*.py """
        tanks = []
        for filename in os.listdir("tanks"):
            # For each tank_*.py in tanks/ directory, load module and create a new tank object.
            if filename.endswith(".py") and filename.startswith("tank_"):
                name = filename.strip(".py").strip("tank_")
                tankmodule = __import__("tanks.{}".format(filename.strip(".py")), fromlist=[name])
                tankclass = getattr(tankmodule, name.capitalize())
                tank = tankclass()
                tanks.append(tank)
        return tanks

    def add_tank_by_name(self, name, rename=None):
        """ Add a specified tank by name """
        for filename in os.listdir("tanks"):
            # For each tank_*.py in tanks/ directory, load module and create a new tank object.
            if filename.endswith(".py") and filename.startswith("tank_"):
                if name == filename.strip(".py").strip("tank_"):
                    tankmodule = __import__("tanks.{}".format(filename.strip(".py")), fromlist=[name])
                    tankclass = getattr(tankmodule, name.capitalize())
                    tank = tankclass(name=rename)
                    self.arena.add_tank_at_random_position(tank)

    def _shoot(self, tank):
        logging.info("{0} performed: {1}".format(str(tank), "shoot"))
        
        hit = False
        target = None
        if tank._facing == Direction.SOUTH:
            for y in range(tank._pos.y + 1, self.arena.height):
                for e in self.arena.get_entities_for_pos(Vector2D(tank._pos.x, y)):
                    e._hp -= 1
                    target = str(e)
                    hit = True
                if hit:
                    break
        elif tank._facing == Direction.EAST:
            for x in range(tank._pos.x + 1, self.arena.width):
                for e in self.arena.get_entities_for_pos(Vector2D(x, tank._pos.y)):
                    e._hp -= 1
                    target = str(e)
                    hit = True
                if hit:
                    break
        elif tank._facing == Direction.WEST:
            for x in range(tank._pos.x - 1, 0, -1):
                for e in self.arena.get_entities_for_pos(Vector2D(x, tank._pos.y)):
                    e._hp -= 1
                    target = str(e)
                    hit = True
                if hit:
                    break
        elif tank._facing == Direction.NORTH:
            for y in range(tank._pos.y - 1, 0, -1):
                for e in self.arena.get_entities_for_pos(Vector2D(tank._pos.x, y)):
                    e._hp -= 1
                    target = str(e)
                    hit = True
                if hit:
                    break
        else:
            return { "status" : "UNKNOWN DIRECTION", "type" : "shoot" }

        return { "status" : "OK", "hit" : hit, "type" : "shoot", "target" : target }

    def _move(self, tank, dir):
        logging.info("{0} performed: {1}".format(str(tank), "move"))

        new_position = tank._pos + dir.value
        collisions = 0

        # Make sure new_position is within arena
        if new_position.x >= self.arena.width or new_position.y >= self.arena.height or new_position.x < 0 or new_position.y < 0:
            return { "status" : "OUT OF BOUNDS", "type" : "move"}

        # Make sure no one is currently in new_position
        for e in self.arena.entities:
            if e._pos == new_position:
                collisions += 1

        # Make sure no one else has the intent to move to new_position
        for t in self.arena.entities:
            if t != tank and t._intent is not None:
                intenttype = t._intent["type"]
                if intenttype == "move":
                    if t._pos + t._intent["direction"].value == new_position:
                        collisions += 1
        
        # If there were any collisions, then don't move
        if collisions > 0:
            return { "status" : "COLLISION", "type" : "" }
        else:
            tank._pos = new_position
            return { "status" : "OK", "type" : "move" }

    def _face(self, tank, dir):
        logging.info("{0} performed: {1}".format(str(tank), "face"))
        tank._facing = dir
        return { "status" : "OK", "type" : "face" }

    def _detect(self, tank):
        logging.info("{0} performed: {1}".format(str(tank), "detect"))
        entities = []
        for e in self.arena.entities:
            if e != tank:
                entities.append(tank._pos - e._pos)
        return { "status" : "OK", "found" : entities, "type" : "detect" }


def main():
    battle = CTBattle(ticks_per_second=100, max_ticks=10000)
    battle.add_tank_by_name("simple", rename="Bot-1")
    #battle.add_tank_by_name("simple", rename="Bot-2")
    #battle.add_tank_by_name("simple", rename="Bot-3")
    #battle.add_tank_by_name("simple", rename="Bot-4")
    battle.start()

if __name__ == "__main__":
    main()
