Lifts
=====

A lift simulator (AI game)

<!-- MarkdownTOC -->

- Quick overview
- AI clients
- Interface
- Non-executable commands
- World specifications
- Statistic specifications
- Awards and badges

<!-- /MarkdownTOC -->


Quick overview
--------------

This is the "engine" behind the `flits` AI game.  It will create and run for
you a virtual world in which people need to use lifts to get in and out of a
building.

The game uses two files (one for input and one for output) to interact with AI
clients, whose task is to control the lifts in a sensible way.


AI clients
----------

Clients executable must accept two commandline parameters:

    my-awesome-AI-client server-to-client client-to-server

- `server-to-client`: The file where the simulation will write its output (see
  "Outputs" section below)
- `client-to-server`: The file where the AI client will write the commands for
  the simulation (see "Inputs" section below)


Interface
---------

The protocol is text based.  Each line represent a message.


### Outputs

Possible outputs from the engine:

- **`WORLD <object>`** - Description of the simulation's world, expressed as a
  JSON-encoded object (see below for details).  This message is generated only
  once, before the simulation has started.
- **`TURN <turn-number>`** - Turn number `<turn-number>` has started.
- **`READY`** - The output for the turn is done, waiting for the client input.
- **`LIFT_CALL <floor-number> <direction>`** - A lift has been called at
  a given floor number to go `UP`, `DOWN` or `-` (possible values for
  `<direction>`)
- **`FLOOR_REQUEST <lift-id> <floor-number>`** - Somebody in lift `<lift-id>`
  has pressed the floor button `<floor-number>`
- **`TRANSIT <lift-id> <floor-number>`** - A lift is transiting through a given
  floor (see why this is useful to know in the "Note" to "Nin-executable
  commands" below)
- **`ARRIVED <lift-id> <floor-number>`** - A lift has arrived at a given floor.
- **`ERROR <text>`** - The command `<command>` has generated an error.
  `<text>` is a multi-word explanation of what the error is.
- **`END`** - The simulation has ended.
- **`STATS <object>`** - The simulation statistics, expressed as a JSON-encoded
  object (see below for details).  This message is generated only once, after
  the simulation has ended.


### Inputs

Valid input that a client can generate for the engine:

- **`READY`** - Inform the simulation engine that the client has bootstrapped
  and online.
- **`GOTO <lift-id> <floor-number>`** - Instruct a lift to move to a given
  floor.
- **`OPEN <lift-id> <direction>`** - Open the doors of a lift, signal to people
  on the floor where the lift will move next [`UP`, `DOWN`, `-`].  As in real
  life, indicating the direction the lift will move next will make only people
  going in that direction to get onboard.  To update the `<direction>` of a
  lift with its door already open, just issue a new `OPEN` command.
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

Todo: add possibility of bi-directional trips (get down on a lift,
get up through another lift)


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
- Most democratic (smallest sigma for waiting times)
- Better all-round performance (weight what above)
- Best flexibility (good performance in different worlds)
