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

    def __init__(self, level, is_exit=False, is_entry=False, directional=True):
        super().__init__()
        self.numeric_location = level
        self.is_exit = is_exit
        self.is_entry = is_entry
        self.directional = directional
        self.requested_directions = set()

    def __str__(self):
        return 'Floor: {}'.format(self.numeric_location)

    on('person.lift.call')
    def push_button(self, person, direction):
        if person.numeric_location != self.numeric_location:
            return
        if not self.directional:
            direction = True
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


def generate_floors(description):
    '''A utility function that will generate all the simulation floors.'''
    pass
