from simpleactors import on

from .common import (
    log,
    LiftsActor,
    LiftStatus,
    Event,
    Command,
    Message,
    Direction)


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
        self.bottom_floor_number = description['bottom_floor_number']
        self.top_floor_number = description['top_floor_number']
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
        '''Return the number of the floor the lift is at.'''
        return self.location.numeric_location

    @property
    def at_top(self):
        '''Return True with lift at top of its possible excursion.'''
        return self.location.numeric_location == self.top_floor_number
    
    @property
    def at_bottom(self):
        '''Return True with lift at bottom of its possible excursion.'''
        return self.location.numeric_location == self.bottom_floor_number

    @property
    def full(self):
        '''Ruturn True if the lift has reached maximum capacity.'''
        return len(self.passengers) == self.capacity

    @property
    def is_moving(self):
        '''Return True if the lift is not still.'''
        return self.direction is not Direction.none
    
    @on('turn.start')
    def turn_action(self, duration):
        '''Perform all actions for a turn of `duration` seconds.'''
        pass

    @on('command.goto')
    def goto(self, lift, destination):
        '''Process the `goto` command.'''
        if self is not lift:
            return
        self.destination = destination
        # Add top/bottom logic
        # Add direction

    @on('command.open')
    def open_doors(self, lift):
        '''Process the `open` command.'''
        if self is not lift:
            return
        if self.is_moving:
            self.emit('error.open.still_moving')
            return
        if self.open_doors is True:
            self.emit('error.open.already_open')
            return
        self.open_doors = True
        self.emit('lift.open')

    @on('command.close')
    def close_doors(self, lift):
        '''Process the `close doors` command.'''
        if self is not lift:
            return
        if self.open_doors is False:
            self.emit('error.close.already_closed')
            return
        self.open_doors = False
        self.emit('lift.close')

    def arrive(self):
        '''Update lift status on arrival to destination.'''
        self.direction = Direction.none
        # set top/bottom flags
