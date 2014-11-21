#! /usr/bin/env python3
'''
A Lift simulator.
'''
from copy import deepcopy
from time import time, sleep
from random import choice, gauss

#import toml

from log import log
from person import Person
from floor import Floor
from lift import Lift
from enums import LiftStatus, PersonStatus


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


class Simulation:

    def __init__(self, description):
        self.description = self._time_compress(description)
        self.floors = self._init_floors()
        self.entries = [f for f in self.floors if f.is_entry]
        self.exits = [f for f in self.floors if f.is_exit]
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
