from random import choice

from log import log
from enums import PersonStatus, LiftStatus, Dirs


class Person:

    '''
    A person in the simulation.

    Args:
        simulation (Simulation): the simulation in which the person lives
        pid (str): a unique id for the person
        status (PersonStatus): the initial state of the person
        floor (Floor or None): floor or None [not in the building]
        destination (Floor): floor or None [not in the building]
        trig_time: time at which to trig the commute
    '''

    def __init__(self, simulation, pid, status, floor, destination, trig_time):
        self.simulation = simulation
        self.pid = pid
        self.status = status
        self.floor = floor
        self.destination = destination
        self.trig_time = trig_time
        self.lift = None  # There is no lift assiciated to this person

    def _enter_building(self):
        '''Enter the building.'''
        self.status = PersonStatus.moving
        self.floor = choice(self.simulation.entries)
        log.info('%s has entered the building on floor %s.',
                 self.pid, self.floor.level)
        if self.floor == self.destination:
            self._reach_destination()

    def _reach_destination(self):
        log.info('%s has reached destination.', self.pid)
        self.status = PersonStatus.done
        if self.lift:
            self.lift.exit(self)
            self.lift = None

    def _enter_lift(self, lift):
        log.info('%s has entered lift %s', self.pid, lift.name)
        self.lift = lift
        self.lift.enter(self)
        self.lift.push_button(self.destination)

    def _move(self):
        # The person is waiting for a lift
        if self.lift is None:
            options = [l for l in self.floor.lifts if l.is_available()]
            # A lift is available!
            if options:
                self._enter_lift(choice(options))
            # No lift, call one.
            go_up = self.floor.level < self.destination.level
            direction = Dirs.up if go_up else Dirs.down
            self.floor.push_button(direction)
        elif self.lift.status != LiftStatus.moving:
            if self.destination == self.lift.floor:
                self._reach_destination()

    def step(self, elapsed):
        '''Perform the next action.'''
        if self.status == PersonStatus.done:
            return
        if self.status == PersonStatus.busy:
            if elapsed > self.trig_time:
                self._enter_building()
        # Entering the building needs to fall through the following case too
        if self.status == PersonStatus.moving:
            self._move()
