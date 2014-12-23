from simpleactors import on, INITIATE

from .common import (
    log,
    LiftsActor,
    LiftStatus,
    Event,
    Command,
    Message)


class Lift:

    '''
    A lift in the simulation.

    Args:
        simulation (Simulation): the simulation in which the lift exists
        lift_description (dict): this is a dictionary that contains:
            name: the name of the lift
            capacity: the maximum capacity
            pass_sec: the time it takes the lift to transit through a floor
            accel_sec: the time it takes to start/stop at a floor
            load_sec: the time the doors stay open for
        status (LiftStatus): the initial state of the lift
        floor (Floor): floor where the lift currently is
    '''

    def __init__(self, simulation, lift_description, status, floor):
        self.simulation = simulation
        for k, v in lift_description.items():
            setattr(self, k, v)
        self.status = status
        self.moving_direction = None
        self.floor = floor
        self.floor.lifts.append(self)
        self.people = set()  # Nobody is in the lift
        self.requested_destinations = set()  # No one has pressed a button
        log.debug('initialised lift "{}" at level {}', self.name, floor.level)

    def __str__(self):
        return 'Lift:{}'.format(self.name)

    def enter(self, person):
        self.people.add(person)

    def exit(self, person):
        self.people.discard(person)

    def is_available(self):
        return (
            self.status == LiftStatus.open and
            len(self.people) < self.capacity)

    def push_button(self, floor):
        if floor not in self.requested_destinations:
            self.requested_destinations.add(floor)
            self.simulation.route(Event.floor_button, self, floor.level)

    def move(self, command, entity, direction):
        log.debug('Lift "{}"" received command "{}"', self.name, command)
        if command == Command.open:
            if self.status != LiftStatus.closed:
                msg = 'Cannot open doors while moving!'
                self.simulation.route(Message.error, self, msg)
            else:
                self.status = LiftStatus.open
        elif command == Command.close:
            if self.status != LiftStatus.open:
                msg = 'The doors are already closed!'
                self.simulation.route(Message.error, self, msg)
            else:
                self.status = LiftStatus.closed
        elif command == Command.move:
            if self.status != LiftStatus.closed:
                msg = 'Cannot move a lift while doors are open!'
                self.simulation.route(Message.error, self, msg)
            else:
                self.status = LiftStatus.moving
                self.moving_direction = direction


class Lift(LiftsActor):

    @on(INITIATE)
    def init(self):
        # Save initial state, emit initial lift.open
        pass

    @on('tick')
    def move(self):
        # Advance in the planned actions, emit transit/open/close as necessary
        pass
