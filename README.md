Lifts
=====

A lift simulator (AI game)


Quick overview
--------------

This is the "engine" behind the `flits` AI game.  It will create and run for
you a virtual world in which people need to use lifts to get in and out of a
building.

The game uses two files (one for input and one for output) to interact with AI
clients, whose task is to control the lifts in a sensible way.


File interface
--------------

The protocol is text based.  Each line represent a message.


### Outputs

Possible outputs from the engine:

- **`WORLD <object>`** - Description of the simulation's world, expressed as a
  JSON-encoded object (see below for details).  This message is generated only
  once, before the simulation has started.
- `STARTED` - The simulation has started.
- **`LIFT_CALLED <floor-number> <direction>`** - A lift has been called at
  a given floor number to go `UP`, `DOWN` or `SOMEWHERE` (possible values for
  `<direction>`)
- **`FLOOR_REQUESTED <lift-id> <floor-number>`** - Somebody in lift `<lift-id>`
  has pressed the floor button `<floor-number>`
- **`ERROR <text>`** - The command `<command>` has generated an error.
  `<text>` is a multi-word explanation of what the error is.
- **`ENDED`** - The simulation has ended.
- **`STATS <object>`** - The simulation statistics, expressed as a JSON-encoded
  object (see below for details).  This message is generated only once, after
  the simulation has ended.


### Inputs

Valid input that a client can generate for the engine:

- **`MOVE <lift-id> <floor-number>`** - Instruct a lift to move to a given
  floor.
- **`OPEN <lift-id>`** - Open the doors of a lift.
- **`CLOSE <lift-id>`** - Close the doors of a lift.


Non-executable commands
-----------------------

Commands that have a valid syntax but cannot be executed will be ignored.
Under no circumstances commands are "queued" for later execution.

Example of non-executable command: issuing a `OPEN` when a lift is not still at
a floor, or when its doors are already open.

**NOTE:** The `MOVE` command can be overridden with a second `MOVE` command
if - and only if - the second `MOVE` command does not imply a change of
direction of movement (i.e. a lift moving from floor 3 to 6 can be instructed
to stop at floor 5 if it hasn't passed it already, but could never ever be
instructed to move towards floor 2)


World specifications
--------------------

xxxx


Statistic specifications
------------------------

xxxx


Awards and badges
-----------------

Ideas:

- Quickest evac (less time to empty building)
- Environmental friendly (watts)
- Short distance (floors travelled)
- Shortest average waiting time
- Most balanced used of lifts
- Better all-round performance (weight what above)
- Best flexibility (good performance in different worlds)