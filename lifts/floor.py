class Floor:

    '''
    A floor in the simulation.

    Args:
        simulation (Simulation): the simulation in which the floor exists
        floor_description (dict): this is a dictionary that contains:
            level (int): the level of the floor
            is_exit(bool): True if the floor is an exit point of the building
            is_entry(bool): True if the floor is an entry point of the building
    '''

    def __init__(self, simulation, floor_description):
        self.simulation = simulation
        for k, v in floor_description.items():
            setattr(self, k, v)
        self.lifts = []
        self.requested_directions = set()

    def push_button(self, direction):
        self.requested_directions.add(direction)
