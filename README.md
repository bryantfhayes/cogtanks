# Cogtanks
Cogtanks is a super sweet game where you program a tank, and then make it autonomously fight other tanks!

# Game Modes
* Last Tank Standing - You win if all the other tanks are destroyed before the end of the game.

# Programming your tank!
## Prerequisites
* Python3.6+ installed on your machine
* Basic python skillz

## How your tank works
Each tick, the engine determines if your tank is eligible to perform your tank's run() function. It is eligible as long as your *cooldown* is 0. Your cooldown is increased whenever you issue an _intent_.

### Intent
The API calls available to you below don't actually cause your tank to do anything, but instead register an _intent_ to do something. Once every eligible tank's run function is complete, all _intents_ are resolved at once. Most _intents_ are resolved with their update effecting the state of the subsequent tick, however bullets are fast, so the `Shoot()` call evaluates immediatley. This means that if TankA moves out of the line-of-sight of TankB on the same tick that TankB shoots, it will still get hit.

You can also only have a single _intent_ per tick. That means that if your tank tried to `Shoot()` then `Move(dir)` in the same tick, only the last _intent_ (in this case `Move(dir)`) would actually happen.

### Intent results
Checking the return status of an _intent_ does not provide any information. In order to see the results of your last action, use the `self.results` dictionary available to you inside your run function. This dictionary will contain the type of _intent_ you performed, status, and any additional information about the results of that action. Take for example the response of a `Shoot()` _intent_:
```python
{
    "status": "OK",
    "hit": false,
    "type": "shoot"
}
```

## The API
### self.Move(dir)
----
Move your tank one space in the given direction (`Direction.NORTH`, `Direction.EAST`, `Direction.WEST`, `Direction.SOUTH`). If there is a conflict, and error will be returned with details.

#### Cooldown
2 ticks

#### Params

| parameter | type | description             |
|-----------|------|-------------------------|
| *dir* | Tank.Direction | Direction to move |

#### Result
Returns one of the following statuses:

| status  | description              |
|---------|--------------------------|
| "OK"    | Your move was successful |