#! /usr/bin/env python3
'''
A Lift simulator.

Usage:
  lifts <sim-file> [<file-interface-dir>]
  lifts -h | --help
  lifts --version

Options:
  -h --help     Show this screen.
  --version     Show version.
'''

import os
from time import time, sleep
from random import choice, gauss, seed

import toml
from docopt import docopt
from simpleactors import Director

from .person import Person
from .floor import Floor
from .lift import Lift
from .interface import FileInterface
from .common import Command, Message


POST_END_GRACE_PERIOD = 60  # in seconds
CLIENT_BOOT_GRACE_PERIOD = 10  # in seconds


class Simulation:

    def __init__(self, sim_file, interface_dir='/tmp/lifts'):
        self._load_sim_file(sim_file)
        from pprint import pprint; pprint(self.description)
        FileInterface(interface_dir)
        self._init_floors()
        exit(0)
        self._init_lifts()
        self._init_people()

    def _load_sim_file(self, sim_file):
        '''Load, parse and expand the simulation file.'''
        sim_fname = os.path.realpath(sim_file)
        # Load the master file
        path, _ = os.path.split(sim_fname)
        with open(sim_fname) as file_:
            sim = toml.load(file_)
        # Expand the building
        building_fname = '{}.toml'.format(sim['building']['model'])
        with open(os.path.join(path, 'buildings', building_fname)) as file_:
            sim['building'] = toml.load(file_)['floor']
        # Expand the lifts
        processed_lifts = []
        for lift in sim['lifts']:
            fname = '{}.toml'.format(lift['model'])
            with open(os.path.join(path, 'lifts', fname)) as file_:
                exp = toml.load(file_)
            exp['bottom_floor_number'], exp['top_floor_number'] = lift['range']
            exp['location'] = lift['location']
            exp['open_doors'] = lift['open_doors']
            processed_lifts.append(exp)
        sim['lifts'] = processed_lifts
        # If provided, initialise the random seed
        try:
            seed(sim['people']['seed'])
        except KeyError:
            print('no seed')
            pass
        self.description = sim

    def _init_floors(self):
        '''A utility function that will generate all the simulation floors.'''
        building = self.description['building']
        by_level = {floor['level']: Floor(**floor) for floor in building}
        min_level = min(by_level.keys())
        max_level = max(by_level.keys())
        for level, instance in by_level.items():
            if level > min_level:
                instance.below = by_level[level - 1]
            if level < max_level:
                instance.above = by_level[level + 1]

    def _init_lifts(self):
        '''Set and return the initial state for all lifts.'''
        self.lifts = {}
        for description in self.description['lifts']:
            floor = choice(list(self.floors.values()))
            lift = Lift(self, description, LiftStatus.open, floor)
            self.lifts[lift.name] = lift

    def _init_people(self):
        '''Set and return the initial state for all people.'''
        self.people = []
        duration = self.description['simulation']['duration_min']
        for pid in range(self.description['simulation']['population']):
            event_time = max(0, gauss(duration / 2, duration / 6))
            pid_string = '#{0:05d}'.format(pid)
            destination = choice(list(self.floors.values()))
            self.people.append(Person(self, pid_string, PersonStatus.idle,
                                      None, destination, event_time))

    def step(self):
        '''Run a single step of the simulation.'''
        self.step_counter += 1
        self.route(Message.turn, None, self.step_counter)
        elapsed = time() - self.start_time
        log.debug('Step {} ({:.3f} s)', self.step_counter, elapsed)
        for command, entity, floor in self.interface.get_commands():
            self.route(command, entity, floor)
        for person in self.people:
            person.step(elapsed)
        intended_duration = self.start_time + GRANULARITY * self.step_counter
        sleep_duration = max(intended_duration - time(), 0)
        sleep(sleep_duration)

    def check_client_is_ready(self):
        '''Return True if the client AI is ready to play.'''
        start_waiting_time = time()
        while time() < start_waiting_time + CLIENT_BOOT_GRACE_PERIOD:
            if False:  # Change with real test
                yield True
            yield False

    def run(self):
        '''Run the simulation.'''
        log.debug('Waiting for the AI client to signal their readiness.')
        checker = self.check_client_is_ready()
        try:
            while not next(checker):
                sleep(0.5)
        except StopIteration:
            log.critical('The client never sent the READY signal.')
            exit(1)
        log.info('Simulation started')
        # Set time limits and utility functions
        duration = self.description['simulation']['duration_min']
        self.start_time = time()
        hard_limit = self.start_time + duration + POST_END_GRACE_PERIOD
        overdue = lambda: time() > hard_limit
        done = lambda: all(p.status == PersonStatus.done for p in self.people)
        # Run the main loop
        while not done():
            if overdue():
                log.error('Hard time limit hit')
                break
            self.step()
        # Post-simulation operations
        elapsed = time() - self.start_time
        self.route(Message.ended)
        log.info('Simulation ended, total duration: {:.3f} seconds', elapsed)


def main():
    args = docopt(__doc__, version='0.1')
    simulation = Simulation(
        sim_file=args['<sim-file>'],
        interface_dir=args['<file-interface-dir>'])
    simulation.run()

if __name__ == '__main__':
    main()
