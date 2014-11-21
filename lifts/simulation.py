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
TIME_COMPRESSION = 360  # 350 --> 1h = 10sec
GRANULARITY = 0.5  # in seconds
GRACE_PERIOD = 3  # in seconds

LiftState = Enum('LiftState', 'moving loading ready')
Event = Enum('Event', 'buttonpress stepin stepout queue')
Dirs = Enum('Dirs', 'up down')

logging.basicConfig(
    format='%(asctime)s - %(levelname)-8s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %03d',
    level=logging.DEBUG)
log = logging.getLogger('lifts')


class Person:

    def __init__(self, simulation, pid, location, destination, action_time):
        self.pid = pid
        self.emit = simulation.listen
        self.location = location
        self.destination = destination
        self.action_time = action_time

    def _arrived(self):
        '''Reach the destination.'''
        self.destination = None
        log.info('%s has reached their destination.', self.pid)

    def _enter_building(self):
        '''Enter the building.'''
        log.info('%s has entered the building.', self.pid)
        self.location = 0
        if self.location == self.destination:
            return self._arrived()
        direction = Dirs.up if self.location < self.destination else Dirs.down
        self.emit(Event.buttonpress, direction=direction)

    def act(self):
        '''Perform the next action.'''
        if self.location is None:
            self._enter_building()


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
        self.step_counter = 0

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
        for pid in range(self.description['simulation']['population']):
            event_time = max(0, gauss(duration / 2, duration / 6))
            pid_string = '#{0:05d}'.format(pid)
            destination = choice(options)
            ret.append(Person(self, pid_string, None, destination, event_time))
        return ret

    def _init_lifts(self):
        '''Return the initial state for all lifts.'''
        ret = []
        for description in self.description['lifts']:
            ret.append(Lift(self, description, 0, 0, LiftState.ready))
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
            if person.action_time is None:
                continue
            if elapsed > person.action_time:
                person.act()
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
        done = lambda: all((p.destination is None for p in self.people))
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
