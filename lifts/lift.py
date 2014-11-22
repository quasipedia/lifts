from log import log
from enums import LiftStatus, Event


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
        self.floor = floor
        self.floor.lifts.append(self)
        self.people = set()  # Nobody is in the lift
        self.requested_destinations = set()  # No one has pressed a button
        log.debug('initialised lift "%s" at level %s', self.name, floor.level)

    def __str__(self):
        return 'Lift:{}'.format(self.name)

    def enter(self, person):
        self.people.add(person)

    def exit(self, person):
        self.people.discard(person)

    def is_available(self):
        return (
            self.status != LiftStatus.moving and
            len(self.people) < self.capacity)

    def push_button(self, floor):
        if floor not in self.requested_destinations:
            self.requested_destinations.add(floor)
            self.simulation.route(self, Event.floor_button, level=floor.level)

    def process(self, command, entity, **kwargs):
        log.debug('Lift "{}"" received command "{}"', self.name, command)
