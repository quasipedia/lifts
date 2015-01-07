'''
Test suite for the simulation module.
'''

import unittest
import unittest.mock as mock

import simpleactors as sa

import lifts.simulation as simulation
from lifts.floor import Floor


TEST_DESCRIPTION = {
    'building': [{'is_entry': False, 'is_exit': False, 'level': 3},
                 {'is_entry': False, 'is_exit': False, 'level': 2},
                 {'is_entry': False, 'is_exit': False, 'level': 1},
                 {'is_entry': True, 'is_exit': True, 'level': 0}],
    'clocking': {'client_turn_ms': 50, 'ticks_per_turn': 1, 'total_ticks': 10},
    'id': 'Basic',
    'lifts': [{'accel_time': 6,
               'bottom_floor_number': 0,
               'capacity': 4,
               'directional': True,
               'location': 0,
               'open_doors': False,
               'top_floor_number': 4,
               'transit_time': 3}],
    'people': {'population': 5, 'seed': 'deterministic'}
}


class TestSimulation(unittest.TestCase):

    '''Tests for the Simulation class.'''

    def setUp(self):
        with mock.patch.object(simulation.Simulation, '__init__',
                               return_value=None):
            self.sim = simulation.Simulation()
        self.sim.description = TEST_DESCRIPTION

    def tearDown(self):
        sa.reset()

    def test_init_floors_instances(self):
        '''_init_floors create a floor instance for each level.'''
        self.sim._init_floors()
        self.assertEqual(4, len(sa.global_actors))

    def test_init_floors_above(self):
        '''_init_floors links an `above` instance for all floors but top.'''
        self.sim._init_floors()
        for floor in sa.global_actors:
            nl = floor.numeric_location
            # http://bugs.python.org/issue19438
            expected = Floor if nl < 3 else type(None)
            self.assertTrue(isinstance(floor.above, expected))

    def test_init_floors_below(self):
        '''_init_floors links an `below` instance for all floors but bottom.'''
        self.sim._init_floors()
        for floor in sa.global_actors:
            nl = floor.numeric_location
            # http://bugs.python.org/issue19438
            expected = Floor if nl > 0 else type(None)
            self.assertTrue(isinstance(floor.below, expected))
