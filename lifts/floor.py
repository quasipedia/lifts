from simpleactors import on

from .common import LiftsActor, Event


class Floor(LiftsActor):

    '''A floor in the simulation.

    Arguments:
        level: the level of the floor
        is_exit: True if the floor is an exit point of the building
        is_entry: True if the floor is an entry point of the building
        directional: True if the button on the floor is directional
    '''

    def __init__(self, level, is_exit=False, is_entry=False):
        super().__init__()
        self.is_exit = is_exit
        self.is_entry = is_entry
        self.requested_directions = set()
        # Since these are going to do other Floor instances, they will be set
        # up at a different time, by an external routine
        self.above = self.below = None

    def __str__(self):
        return 'Floor: {}'.format(self.numeric_location)

    @property
    def numeric_location(self):
        # One can't just overwrite a property decorator by setting a real
        # proprety instead, so...
        return self.level

    @on('person.lift.call')
    def push_button(self, person, direction):
        if person.numeric_location != self.numeric_location:
            return
        if direction not in self.requested_directions:
            self.requested_directions.add(direction)

    @on('lift.open')
    def lift_has_opened(self):
        # If not at floor, skip
        # Button reset for lift direction
        # Prevent lock button for that direction
        pass

    @on('lift.close')
    def lift_has_closed(self):
        # If not at floor, skip
        # Unlock button for direction
        pass
