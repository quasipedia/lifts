from simpleactors import on, INITIATE

from .common import (
    log,
    LiftsActor,
    LiftStatus,
    Event,
    Command,
    Message,
    Direction)


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

    '''
    A lift in the simulation.

    Args:
        description (dict): this is a dictionary that contains:
            lid: the name of the lift
            capacity: the maximum capacity
            transit_time: seconds it takes the lift to transit through a floor
            accel_time: seconds it takes to start/stop at a floor
        status (LiftStatus): the initial state of the lift
        floor (Floor): floor where the lift currently is
    '''

    def __init__(self, description, location, open_doors=False):
        super().__init__()
        # Lift description
        self.lid = description['lid']
        self.capacity = description['capacity']
        self.transit_time = description['transit_time']
        self.accel_time = description['accel_time']
        # Lift status
        self.location = location
        self.direction = Direction.none
        self.destination = None
        self.passengers = set()
        self.open_doors = open_doors

    def __str__(self):
        return self.lid

    @property
    def numeric_location(self):
        return self.location.numeric_location

    @on('turn.start')
    def move(self, duration):
        '''Perform all actions for a turn of `duration` seconds.'''
        pass

    @on('command.goto')
    def set_destination(self, lift, destination):
        if self is not lift:
            return
        self.destination = destination
        # Add top/bottom logic
        # Add direction

    @on('command.open')
    def open_doors(self, lift):
        if self is not lift:
            return
        if self.direction is not Direction.none:
            self.emit('error.open.still_moving')
            return
        if self.open_doors is True:
            self.emit('error.open.already_open')
            return
        self.open_doors = True
        self.emit('lift.open')

    @on('command.close')
    def close_doors(self, lift):
        if self is not lift:
            return
        if self.open_doors is False:
            self.emit('error.close.already_closed')
            return
        self.open_doors = False
        self.emit('lift.close')

    def arrive(self):
        self.direction = Direction.none
        # set top/bottom flags
