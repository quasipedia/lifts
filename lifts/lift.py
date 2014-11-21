from enums import LiftStatus


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
        self.people = []  # Nobody is in the lift
        self.requested_destinations = set()  # No one has pressed a button

    def enter(self, person):
        self.people.append(person)

    def exit(self, person):
        self.people.remove(person)

    def is_available(self):
        return (
            self.status != LiftStatus.moving and
            len(self.people < self.capacity))

    def push_button(self, floor):
        self.requested_destinations.add(floor)
