from enum import Enum

from simpleactors import Actor
import logbook

# ENUMERATORS
Direction = Enum('Dirs', 'up down none')
Event = Enum('Event', 'call_button floor_button')
LiftStatus = Enum('LiftStatus', 'moving open closed')
Command = Enum('Command', 'ready goto open close')
Message = Enum(
    'Message',
    'world turn ready lift_call floor_request transit arrived error end stats')

log = logbook.Logger('Lifts')


class LiftsActor(Actor):

    '''An abstract base class for all actors in the lift simulation.'''

    @property
    def numeric_location(self):
        '''Return the number of the floor the person is at.'''
        raise NotImplementedError

    @property
    def compass(self):
        '''Return the Direction to reach destination.'''
        if self.numeric_location == self.destination.numeric_location:
            return Direction.none
        if self.numeric_location < self.destination.numeric_location:
            return Direction.up
        if self.numeric_location > self.destination.numeric_location:
            return Direction.down
