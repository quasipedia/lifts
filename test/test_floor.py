'''
Test suite for the floor module.
'''

import unittest
import unittest.mock as mock

import simpleactors as sa

from lifts.floor import Floor
from lifts.common import Direction


class MockActor:

    def __init__(self, location):
        self.location = location


class TestFloor(unittest.TestCase):

    '''Tests for the Floor class.'''

    def setUp(self):
        self.floor = Floor(level=0, is_exit=True, is_entry=True)
        self.mock_emit = mock.MagicMock()
        self.floor.emit = self.mock_emit

    def tearDown(self):
        sa.reset()

    def test_string(self):
        '''The string representation of a Floor is its level.'''
        self.assertEqual('Floor: 0', '{}'.format(self.floor))

    def test_numeric_location(self):
        '''The numeric_location of a floor is it's level'''
        self.assertEqual(0, self.floor.numeric_location)

    def test_call_wrong_floor(self):
        '''A call is ignored if it does not happen at the concerned floor.'''
        self.floor.push_button(MockActor('not-here'), Direction.up)
        self.assertFalse(self.mock_emit.called)

    def test_direction_already_booked(self):
        '''A call is ignored if the floor had already been requested.'''
        self.floor.requested_directions.add(Direction.up)
        self.floor.push_button(MockActor(self.floor), Direction.up)
        self.assertFalse(self.mock_emit.called)

    def test_direction_add(self):
        '''A call adds the requested direction to the floor.'''
        self.floor.push_button(MockActor(self.floor), Direction.up)
        self.assertIn(Direction.up, self.floor.requested_directions)

    def test_lift_close_wrong_floor(self):
        '''A close message is ignored if it dose not concern the floor.'''
        self.floor.lift_has_closed(MockActor('not-here'))
        self.assertFalse(self.mock_emit.called)

    def test_lift_close_reset_call(self):
        '''A requested direction is reset when the lift for that dir closes.'''
        self.floor.requested_directions.add(Direction.up)
        lift = MockActor(self.floor)
        lift.direction = Direction.up
        self.floor.lift_has_closed(lift)
        self.assertNotIn(Direction.up, self.floor.requested_directions)
