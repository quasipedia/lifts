#! /usr/bin/env python3
'''
A Lift simulator.
'''
import logging
from time import time, sleep
from random import choice, gauss

import toml


DEFAULT = {
    'building': [
        {'level': 3, 'exit': False},
        {'level': 2, 'exit': False},
        {'level': 1, 'exit': False},
        {'level': 0, 'exit': True},
    ],
    'lifts': [
        {'name': 'main', 'capacity': 4,
         'pass_time': 3, 'stop_time': 6, 'open_time': 10},
    ],
    'simulation': {
        'duration': 30,
        'population': 30
    }
}

logging.basicConfig(
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M:%S %03d',
    level=logging.DEBUG)
log = logging.getLogger('lifts')


class Person:

    def __init__(self, location, destination, action_time):
        self.location = location
        self.destination = destination
        self.action_time = action_time

    def act(self):
        '''Perform the next action.'''
        if self.location is None:
            log.debug('Person %s has entered the building.', id(self))
            self.location = 0


class Simulation:

    def __init__(self, description):
        self.description = description
        self.people = self._init_people()
        self.lifts = self._init_lifts()

    def _init_people(self):
        '''Return the initial state for all people.'''
        options = [floor['level'] for floor in self.description['building']]
        duration = self.description['simulation']['duration']
        ret = []
        for person in range(self.description['simulation']['population']):
            event_time = max(0, gauss(duration / 2, duration / 6))
            ret.append(Person(None, choice(options), event_time))
        return ret

    def _init_lifts(self):
        '''Return the initial state for all lifts.'''
        ret = {}
        for lift in self.description['lifts']:
            ret[lift['name']] = {
                'location': 0, 'load': 0, 'up': False, 'down': False}
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
