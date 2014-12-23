from simpleactors import on, KILL

from .common import log, Direction, LiftsActor


class Person(LiftsActor):

    '''A person in the simulation.

    A person is "moving" as soon as it enters the simulation.  The object gets
    destroyed as soon as the person reaches it's destination

    Aguments:
        pid: a human-friendly identifier for the person (string)
        location: the current position of the person (normally a floor, but
            could as well be a lift, although it makes no sense)
        destination: the final destination of the person (floor)
    '''

    def __init__(self, pid, location, destination):
        super().__init__()
        self.pid = pid
        self.location = location
        self.destination = destination
        if self.location == self.destination:
            self.arrive()
        else:
            self.call_lift()

    def __str__(self):
        return self.pid

    @property
    def numeric_location(self):
        '''Return the number of the floor the person is at.'''
        return self.location.numeric_location

    def _should_get_off(self, lift):
        '''Return True if the most sensible thing to do is get off the lift.'''
        compass = self.compass  # Save recomputation for each test
        if compass is Direction.none:
            return True
        if compass != lift.direction:
            return True
        if compass is Direction.down and lift.at_bottom:
            return True
        if compass is Direction.up and lift.at_top:
            return True
        return False

    def _should_get_on(self, lift):
        '''Return True if the most sensible thing to do is get on the lift.'''
        if not lift.full and lift.direction in (self.compass, Direction.none):
            return True
        return False

    @on('lift.open')
    def on_lift_open(self, message, lift):
        '''Take action if a lift opens neraby.'''
        if self.location == lift:
            if self._should_get_off(lift):
                self.emit('person.lift.off', lift)
                self.location = lift.location
            if lift.location == self.destination:
                self.arrive()
            else:
                self.call_lift()
        if self.location == lift.location:
            if self._should_get_on(lift):
                self.emit('person.lift.on', lift)

    def call_lift(self):
        self.emit('person.lift.call', direction=self.compass)

    def arrive(self):
        self.emit('person.arrived')
        self.emit(KILL, self)
