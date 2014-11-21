#! /usr/bin/env python3
'''
A Lift simulator.
'''
import logging
from copy import deepcopy
from time import time, sleep
from random import choice, gauss

#import toml
from enum import Enum


DEFAULT = {
    'building': [
        {'level': 3, 'is_exit': False, 'is_entry': False},
        {'level': 2, 'is_exit': False, 'is_entry': False},
        {'level': 1, 'is_exit': False, 'is_entry': False},
        {'level': 0, 'is_exit': True, 'is_entry': True},
    ],
    'lifts': [
        {'name': 'main', 'capacity': 4,
         'pass_sec': 3, 'accel_sec': 6, 'load_sec': 10},
    ],
    'simulation': {
        'duration_min': 60,
        'population': 30
    }
}
TIME_COMPRESSION = 1200  # 360 --> 1h = 10sec
GRANULARITY = 0.3  # in seconds
GRACE_PERIOD = 1  # in seconds

LiftStatus = Enum('LiftStatus', 'moving loading ready')
PersonStatus = Enum('PersonStatus', 'busy moving done')
Event = Enum('Event', 'buttonpress')
Dirs = Enum('Dirs', 'up down')

logging.basicConfig(
    format='%(asctime)s - %(levelname)-8s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %03d',
    level=logging.DEBUG)
log = logging.getLogger('lifts')


class Person:

    '''
    A person in the simulation.

    Args:
        simulation (Simulation): the simulation in which the person lives
        pid (str): a unique id for the person
        status (PersonStatus): the initial state of the person
        location (Floor or None): floor or None [not in the building]
        destination (Floor): floor or None [not in the building]
        trig_time: time at which to trig the commute
    '''

    def __init__(self, simulation, pid, status, location, destination,
                 trig_time):
        self.simulation = simulation
        self.emit = simulation.listen
        self.pid = pid
        self.status = status
        self.location = location
        self.destination = destination
        self.trig_time = trig_time
        self.lift = None  # There is no lift assiciated to this person

    def _enter_building(self):
        '''Enter the building.'''
        log.info('%s has entered the building.', self.pid)
        self.location = 0

    def _move(self):
        if (self.lift.status != LiftStatus.moving and
                self.location == self.destination):
            log.info('%s has reached their destination.', self.pid)
            self.lift.exit(self)
            self.status = PersonStatus.done
        else:
            self.status = PersonStatus.moving
        direction = Dirs.up if self.location < self.destination else Dirs.down
        self.emit(Event.buttonpress, direction=direction)

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
        location (Floor): floor where the lift currently is
    '''

    def __init__(self, simulation, lift_description, status, location):
        self.simulation = simulation
        for k, v in lift_description.items():
            setattr(self, k, v)
        self.status = status
        self.location = location
        self.people = []  # Nobody is in the lift

    def enter(self, person):
        self.people.append(person)

    def exit(self, person):
        self.people.remove(person)

    def empty_slot(self):
        return len(self.people < self.capacity)


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


class Simulation:

    def __init__(self, description):
        self.description = self._time_compress(description)
        self.floors = self._init_floors()
        self.people = self._init_people()
        self.lifts = self._init_lifts()
        self.step_counter = 0

    def _time_compress(self, description):
        ret = deepcopy(description)
        for lift in ret['lifts']:
            for k, v in lift.items():
                lift[k] = v / TIME_COMPRESSION if k.endswith('_sec') else v
        ret['simulation']['duration_min'] *= 60 / TIME_COMPRESSION
        return ret

    def _init_floors(self):
        '''Set and return the initial state for all floors.'''
        ret = []
        for floor_description in reversed(self.description['building']):
            ret.append(Floor(self, floor_description))
        return ret

    def _init_people(self):
        '''Set and return the initial state for all people.'''
        ret = []
        duration = self.description['simulation']['duration_min']
        for pid in range(self.description['simulation']['population']):
            event_time = max(0, gauss(duration / 2, duration / 6))
            pid_string = '#{0:05d}'.format(pid)
            destination = choice(self.floors)
            ret.append(Person(self, pid_string, PersonStatus.busy,
                              None, destination, event_time))
        return ret

    def _init_lifts(self):
        '''Set and return the initial state for all lifts.'''
        ret = []
        for description in self.description['lifts']:
            ret.append(Lift(self, description, LiftStatus.ready, 0))
        return ret

    def listen(self, event_name, **kwargs):
        '''Listen to events generated by the objects in the game.'''
        log.debug('Received %s', event_name)

    def step(self):
        '''Run a single step of the simulation.'''
        self.step_counter += 1
        elapsed = time() - self.start_time
        log.debug('Step %d (%.3f seconds in)', self.step_counter, elapsed)
        for person in self.people:
            person.step(elapsed)
        intended_duration = self.start_time + GRANULARITY * self.step_counter
        sleep_duration = max(intended_duration - time(), 0)
        sleep(sleep_duration)

    def run(self):
        '''Run the simulation.'''
        log.debug('Simulation started.')
        duration = self.description['simulation']['duration_min']
        self.start_time = time()
        hard_limit = self.start_time + duration + GRACE_PERIOD
        overdue = lambda: time() > hard_limit
        done = lambda: all(p.status == PersonStatus.done for p in self.people)
        while not done():
            if overdue():
                log.error('Hard time limit hit')
                break
            self.step()
        log.debug('Simulation ended.')


def main():
    simulation = Simulation(DEFAULT)
    simulation.run()


if __name__ == '__main__':
    main()
