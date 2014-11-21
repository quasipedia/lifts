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
        {'level': 3, 'exit': False},
        {'level': 2, 'exit': False},
        {'level': 1, 'exit': False},
        {'level': 0, 'exit': True},
    ],
    'lifts': [
        {'name': 'main', 'capacity': 4,
         'pass_sec': 3, 'accel_sec': 6, 'loading_sec': 10},
    ],
    'simulation': {
        'duration_min': 60,
        'population': 30
    }
}
TIME_COMPRESSION = 360  # 1h = 10sec

LiftState = Enum('LiftState', 'moving loading ready')
Event = Enum('Event', 'buttonpress stepin stepout queue')

logging.basicConfig(
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M:%S %03d',
    level=logging.DEBUG)
log = logging.getLogger('lifts')


class Person:

    def __init__(self, simulation, location, destination, action_time):
        self.simulation = simulation
        self.location = location
        self.destination = destination
        self.action_time = action_time

    def act(self):
        '''Perform the next action.'''
        if self.location is None:
            log.debug('Person %s has entered the building.', id(self))
            self.location = 0


class Lift:

    def __init__(self, simulation, description, location, load, state):
        for k, v in description.items():
            setattr(self, k, v)
        self.simulation = simulation
        self.location = location
        self.load = load
        self.state = state


class Simulation:

    def __init__(self, description):
        self.description = self._time_compress(description)
        self.people = self._init_people()
        self.lifts = self._init_lifts()

    def _time_compress(self, description):
        ret = deepcopy(description)
        for lift in ret['lifts']:
            for k, v in lift.items():
                lift[k] = v / TIME_COMPRESSION if k.endswith('_sec') else v
        ret['simulation']['duration_min'] *= 60 / TIME_COMPRESSION
        return ret

    def _init_people(self):
        '''Return the initial state for all people.'''
        options = [floor['level'] for floor in self.description['building']]
        duration = self.description['simulation']['duration_min']
        ret = []
        for person in range(self.description['simulation']['population']):
            event_time = max(0, gauss(duration / 2, duration / 6))
            ret.append(Person(self, None, choice(options), event_time))
        return ret

    def _init_lifts(self):
        '''Return the initial state for all lifts.'''
        ret = []
        for description in self.description['lifts']:
            ret.append(Lift(self, description, 0, 0, LiftState.ready))
        return ret

    def step(self):
        '''Run a single step of the simulation.'''
        elapsed = time() - self.starttime
        log.debug('Elapsed %.6f ms', elapsed)
        for person in self.people:
            if person.action_time is None:
                continue
            if elapsed > person.action_time:
                person.act()
        sleep(.1)

    def run(self):
        '''Run the simulation.'''
        self.starttime = time()
        log.debug('Simulation started.')
        while any((person.location is None for person in self.people)):
            self.step()
        log.debug('Simulation ended.')


def main():
    simulation = Simulation(DEFAULT)
    simulation.run()


if __name__ == '__main__':
    main()
