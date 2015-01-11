from simpleactors import on

from .common import LiftsActor, Direction


class Lift(LiftsActor):

    '''
    A lift in the simulation.

    Arguments:
        description: this is a dictionary that contains:
            lid: the name of the lift
            capacity: the maximum capacity
            transit_time: seconds it takes the lift to transit through a floor
            accel_time: seconds it takes to start/stop at a floor
            bottom_floor_number: lower reach of the lift shaft
            top_floor_number: upper reach of the lift shaft
        status (LiftStatus): the initial state of the lift
        floor (Floor): floor where the lift currently is
    '''

    def __init__(self, description, location, open_doors=False):
        super().__init__()
        # Lift description
        self.id = description['lid']
        self.capacity = description['capacity']
        self.transit_time = description['transit_time']
        self.accel_time = description['accel_time']
        self.bottom_floor_number = description['bottom_floor_number']
        self.top_floor_number = description['top_floor_number']
        # Sanity checks
        int_keys = ('capacity', 'bottom_floor_number', 'top_floor_number')
        if any((not isinstance(description[k], int) for k in int_keys)):
            msg = 'All of {} must be integers!'.format(int_keys)
            raise ValueError(msg)
        if self.capacity < 1:
            msg = 'The lift must be able to carry at least one person!'
            raise ValueError(msg)
        if not self.accel_time > self.transit_time:
            msg = 'Starting/Stopping a lift must take longer than transit!'
            raise ValueError(msg)
        if not self.bottom_floor_number < self.top_floor_number:
            msg = 'The lift must have some excursion!'
            raise ValueError(msg)
        curr_num = location.numeric_location
        if not self.bottom_floor_number <= curr_num <= self.top_floor_number:
            msg = 'The location of the lift must be within its excursion.'
            raise ValueError(msg)
        # Lift status
        self.location = location
        self.destination = None
        self.passengers = set()
        self.open_doors = open_doors
        self.intent = None
        # Movement tracking
        self._carry_seconds = 0

    def __str__(self):
        return 'Lift: {}'.format(self.id)

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

    @property
    def direction(self):
        '''Return the direction of the lift.'''
        if self.intent:
            return self.intent
        if self.destination is None:
            return Direction.none
        if self.destination.numeric_location > self.location.numeric_location:
            return Direction.up
        return Direction.down

    @on('command.goto')
    def goto(self, lift, destination):
        '''Process the `goto` command.'''
        if self is not lift:
            return
        # Refuse to go over the top or below bottom
        dest_num = destination.numeric_location
        if not self.bottom_floor_number <= dest_num <= self.top_floor_number:
            self.emit('error.destination.out_of_boundaries')
            return
        # Refuse to surreptitiously change direction
        curr_num = self.location.numeric_location
        dir_err_msg = 'error.destination.conflicting_direction'
        if self.direction is Direction.down and dest_num >= curr_num:
            self.emit(dir_err_msg)
            return
        if self.direction is Direction.up and dest_num <= curr_num:
            self.emit(dir_err_msg)
            return
        # Refuse to move with open doors
        if self.open_doors:
            self.emit('error.goto.doors_are_open')
        # Error if lift already still at destination
        if self.location == destination and self.direction is Direction.none:
            self.emit('error.goto.already_there')
        # If you made it till here... update the destination!
        self.destination = destination

    @on('command.open')
    def open(self, lift, intent=None):
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
        self.intent = intent  # This is the "promised" direction of travel
        self.emit('lift.open')

    @on('command.close')
    def close(self, lift):
        '''Process the `close doors` command.'''
        if self is not lift:
            return
        if self.open_doors is False:
            self.emit('error.close.already_closed')
            return
        self.open_doors = False
        self.intent = None  # Reset any promise of direction
        self.emit('lift.close')

    def arrive(self):
        '''Update lift status on arrival to destination.'''
        self.emit('lift.arrive', floor=self.destination)
        self._carry_seconds = 0
        self.destination = None

    @on('turn.start')
    def take_turn(self, duration):
        '''Process a `turn.start` signal.'''
        if self.destination is None:
            return
        self._carry_seconds += duration
        self.consume_seconds()

    def consume_seconds(self):
        '''Perform all actions for a turn of `duration` seconds.'''
        destination = self.destination
        while self._carry_seconds > self.transit_time:
            decel = destination in (self.location.above, self.location.below)
            # The lift is about to stop
            if decel:
                if self._carry_seconds > self.accel_time:
                    self.arrive()
                break
            # The lift is just moving
            self._carry_seconds -= self.transit_time
            if self.direction is Direction.down:
                self.location = self.location.below
            else:
                self.location = self.location.above
            self.emit('lift.transit', floor=self.location)
