# Cogtanks
Cogtanks is a super sweet game where you program a tank, and then make it autonomously fight other tanks!

# Game Modes
* Last Tank Standing - You win if all the other tanks are destroyed before the end of the game.

# Usage
## Prerequisites
* Python3.6+ installed on your machine
* Basic python skillz

## Create Your Tank
To create your first tank, create a file inside `cogtanks/engine/tanks`. The name of the file must be formatted like:
`tank_tankname.py`.
* Starts with `tank_`
* All lower case
* Ends with `.py`

Your tank name is the the name of a class, capitalizing the first letter. This class must inherit from `Tank`. I recommend starting with the example code below:

```python
from .tank import Tank
from .tank import Direction

import random

class Simple(Tank):

    # OPTIONAL: If you want a custom name
    def __init__(self, name="SimpleTank"):
        Tank.__init__(self, name=name)

    def setup(self):
        """ This stuff runs once, setup variables and stuff """
        self.facing = None
        self.dirs = [Direction.NORTH, Direction.EAST, Direction.WEST, Direction.SOUTH]

    def run(self):
        """ This happens every tick that you are not cooling down """

        # Do stuff
        if self.facing is None:
            self.Face(Direction.EAST)
            self.facing = Direction.EAST
        elif "type" in self.results and self.results["type"] != "move":
            self.Move(random.choice(self.dirs))
        else:
            self.Shoot()

        # Randomly do other stuff
        if random.randint(0,100) < 10:
            self.Detect()
        elif random.randint(0,100) < 20:
            self.Face(random.choice(self.dirs))
        

```

### Other Rules
* Never use variables or functions starting with an underscore. These are private and that is cheating!
* Don't manipulate parent `Tank` class in any way.
* Don't try to take advantage of the underlying cogtank engine, just write a self contained `run()` function.

## Make the Tanks Fight!
In order to kick off a battle, and generate the `tickdata.json` file, run:
```bash
> cd cogtanks/engine
> python cogtanks.py
```

This is make one tank for each AI found in `cogtanks/engine/tanks` and make them fight eachother either until one is left, or the tick limit is hit (Default: 5000 ticks)

## Visualizer
Following every run of the application, `tickdata.json` is created. This file contains all the information for the epic battle your tanks had. In order to see what your tank is doing, use the visualizer app:
```
cogtanks/visualizer/bin/CTVisualizer.exe
```
![](https://media.giphy.com/media/dXL3snonjGl0X5qDw9/giphy.gif)

### Controls
Beisdes the available buttons, you can use the following keyboard shortcuts as well:
| shortcut  | description              |
|----------|--------------------------|
| Left Arrow     | Go back 1 tick |
| Right Arrow     | Go forward 1 tick |
| Up Arrow     | Speed up "Run All" playback |
| Down Arrow     | Slow down "Run All" playback |
| Escape     | Cancel "Run All" playback |

Pressing the _Load_ button will reload the `tickdata.json` file, so a fast way to test is to run a simulation, press _Load_ and repeat for each iteration!

# Programming your tank!

## How Your Tank Works
Each tick, the engine determines if your tank is eligible to perform your tank's `run()` function. It is eligible as long as your *cooldown* is 0. Your cooldown is increased whenever you issue an _intent_.

### Intent
The API calls available to you below don't actually cause your tank to do anything, but instead register an _intent_ to do something. Once every eligible tank's run function is complete, all _intents_ are resolved at once. Most _intents_ are resolved with their update effecting the state of the subsequent tick, however bullets are fast, so the `Shoot()` call evaluates immediatley. This means that if TankA moves out of the line-of-sight of TankB on the same tick that TankB shoots, it will still get hit.

You can also only have a single _intent_ per tick. That means that if your tank tried to `Shoot()` then `Move(dir)` in the same tick, only the last _intent_ (in this case `Move(dir)`) would actually happen.

### Intent Results
Checking the return status of an _intent_ does not provide any information. In order to see the results of your last action, use the `self.results` dictionary available to you inside your run function. This dictionary will contain the type of _intent_ you performed, status, and any additional information about the results of that action. Take for example the response of a `Shoot()` _intent_:
```python
{
    "status": "OK",
    "hit": false,
    "type": "shoot"
}
```

# The API
## self.Move(dir)
Move your tank one space in the given direction (`Direction.NORTH`, `Direction.EAST`, `Direction.WEST`, `Direction.SOUTH`). If there is a conflict, and error will be returned with details.

### Cooldown
2 ticks

### Params

| parameter | type | description             |
|-----------|------|-------------------------|
| *dir* | Tank.Direction | Direction to move |

### Results
* **status**
    * OK - Your move was successful
    * COLLISION - You tried to move to the same tile as another tank, both movements therefore failed
    * OUT_OF_BOUNDS - You tried to move off the grid

## self.Face(dir)
Make your tank face the given direction (`Direction.NORTH`, `Direction.EAST`, `Direction.WEST`, `Direction.SOUTH`).

### Cooldown
1 ticks

### Params

| parameter | type | description             |
|-----------|------|-------------------------|
| *dir* | Tank.Direction | Direction to face |

### Results
* **status**
    * OK - You are now facing the chosen direction

## self.Shoot()
Make your tank shoot a bullet in the _Direction_ it is facing.

### Cooldown
2 ticks

### Params

N/A

### Results
* **status**
    * OK - You fired a bullet
* **target**
    * null - You missed
    * name_of_tank - You hit this tank
* **hit**
    * true - You hit someone
    * false - You missed

## self.Detect()
Scan the map and determine where other tanks are, relative to your position.

### Cooldown
4 ticks

### Params

N/A

### Results
* **status**
    * OK - Success
* **found**
    * List containing each other tank's position relative to yours. Each item in the list is a list that looks like: `[x, y]`

