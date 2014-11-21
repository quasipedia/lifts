#! /usr/bin/env python3
'''
A Lift simulator.
'''
import logging
from random import randint

import toml


DEFAULT = {
    'building': [
        {'floor': 3, 'exit': False},
        {'floor': 2, 'exit': False},
        {'floor': 1, 'exit': False},
        {'floor': 0, 'exit': True},
    ],
    'lifts': [
        {'name': 'main', 'capacity': 4,
         'pass_time': 3, 'stop_time': 6, 'open_time': 10},
    ],
}


log = logging.getLogger('lifts')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


class Person:

    def __init__(self, location, destination):
        self.location = location
        self.destination = destination


class Simulation:

    def __init__(self, description):
        self.description = description
        self.state = {
            'people': [Person(None, randint(0, 3)) for i in range(30)],
            'lifts': self._init_lifts()
        }

    def _init_lifts(self, lifts):
        '''Return the initial state for all lifts.'''
        ret = {}
        for lift in lifts:
            ret[lift['name']] = {
                'location': 0, 'load': 0, 'up': False, 'down': False}
        return ret


def main():
    log.debug('Simulation started.')
    print(toml.dumps(DEFAULT))


if __name__ == '__main__':
    main()