'''
Test suite for the lift module.
'''

import unittest
import unittest.mock as mock

import simpleactors as sa

from lifts.common import Direction
from lifts.lift import Lift


class MockFloor:

    def __init__(self, numeric_location):
        self.numeric_location = numeric_location


class TestLift(unittest.TestCase):

    '''Tests for the Lift class.'''

    def setUp(self):
        description = {
            'lid': 'SpamLift',
            'capacity': 2,
            'transit_time': 3,
            'accel_time': 6,
            'bottom_floor_number': 0,
            'top_floor_number': 10,
        }
        self.ground_floor = MockFloor(0)
        self.top_floor = MockFloor(10)
        self.lift = Lift(description, self.ground_floor)

    def tearDown(self):
        sa.reset()

    def test_numeric_location(self):
        '''The numeric location of a lift is the current floor number.'''
        self.assertEqual(0, self.lift.numeric_location)

    def test_at_top(self):
        '''A lift knows when it is at the top floor it can reach.'''
        self.lift.location = self.top_floor
        self.assertTrue(self.lift.at_top)

    def test_at_bottom(self):
        '''A lift knows when it is at the bottom floor it can reach.'''
        self.assertTrue(self.lift.at_bottom)

    def test_full(self):
        '''A lift can detect if it is full.'''
        for n in range(self.lift.capacity):
            self.lift.passengers.add(object())
        self.assertTrue(self.lift.full)

    def test_is_moving(self):
        '''A lift can detect if it is moving.'''
        self.lift.goto(self.lift, self.top_floor)
        self.assertTrue(self.lift.is_moving)

    def test_turn_action_no_action(self):
        '''A lift will stay still during a turn if no destination.'''
        self.fail()

    def test_turn_action_update_position(self):
        '''A lift will update its position during its turn.'''
        self.fail()

    def test_turn_action_reach_destination(self):
        '''A lift will stop and change its status if reach destination.'''
        self.fail()

    def test_goto_ignore(self):
        '''A goto command is ignored if not specifically addressed to self.'''
        self.lift.goto('<some-other-lift>', MockFloor(5))
        self.assertFalse(self.lift.is_moving)

    def test_goto_error_out_of_boundaries(self):
        '''A goto command will fail with destination out of top-bottom.'''
        err_msg = 'error.destination.out_of_boundaries'
        with mock.patch.object(self.lift, 'emit') as mock_emit:
            self.lift.goto(self.lift, MockFloor(11))
            mock_emit.assert_called_once_with(err_msg)
        with mock.patch.object(self.lift, 'emit') as mock_emit:
            self.lift.goto(self.lift, MockFloor(-1))
            mock_emit.assert_called_once_with(err_msg)

    def test_goto_error_wrong_direction(self):
        '''A goto command will fail with lift moving in opposite direction.'''
        err_msg = 'error.destination.conflicting_direction'
        self.lift.location = MockFloor(5)
        self.lift.goto(self.lift, self.ground_floor)
        with mock.patch.object(self.lift, 'emit') as mock_emit:
            self.lift.goto(self.lift, self.top_floor)
            mock_emit.assert_called_once_with(err_msg)

    def test_goto_error_already_still(self):
        '''A goto command will fail if the lift is still at its destination.'''
        with mock.patch.object(self.lift, 'emit') as mock_emit:
            self.lift.goto(self.lift, self.ground_floor)
            mock_emit.assert_called_once_with('error.goto.already_there')

    def test_goto_error_doors_open(self):
        '''A goto command will fail if doors are open.'''
        self.lift.open(self.lift)
        self.lift.goto(self.lift, self.top_floor)
        with mock.patch.object(self.lift, 'emit') as mock_emit:
            self.lift.goto(self.lift, self.top_floor)
            mock_emit.assert_called_once_with('error.goto.doors_are_open')

    def test_goto_success_from_still(self):
        '''A goto command will succeed for a lift that is still.'''
        self.lift.goto(self.lift, self.top_floor)
        self.assertTrue(self.lift.is_moving)
        self.assertEqual(self.top_floor, self.lift.destination)

    def test_goto_success_update(self):
        '''A goto command can be overridden with new one in same direction.'''
        middle_floor = MockFloor(5)
        self.lift.goto(self.lift, self.top_floor)
        self.lift.goto(self.lift, middle_floor)
        self.assertTrue(self.lift.is_moving)
        self.assertEqual(middle_floor, self.lift.destination)

    def test_open_moving(self):
        '''An open command fails if the lift is still moving.'''
        self.lift.goto(self.lift, self.top_floor)
        with mock.patch.object(self.lift, 'emit') as mock_emit:
            self.lift.open(self.lift)
            mock_emit.assert_called_once_with('error.open.still_moving')

    def test_open_already_open(self):
        '''An open command will fail for an already open lift.'''
        self.lift.open(self.lift)
        with mock.patch.object(self.lift, 'emit') as mock_emit:
            self.lift.open(self.lift)
            mock_emit.assert_called_once_with('error.open.already_open')

    def test_open_success(self):
        '''A lift can open upon command.'''
        self.lift.open(self.lift)
        self.assertTrue(self.lift.open_doors)

    def test_close_already_closed(self):
        '''A close command will raies if the lift is already closed.'''
        with mock.patch.object(self.lift, 'emit') as mock_emit:
            self.lift.close(self.lift)
            mock_emit.assert_called_once_with('error.close.already_closed')

    def test_close_success(self):
        '''A lift can close upon command.'''
        self.lift.open(self.lift)
        self.lift.close(self.lift)
        self.assertFalse(self.lift.open_doors)

    def test_arrive_status(self):
        '''A lift resets its destination upon arrival.'''
        self.lift.destination = self.top_floor
        self.lift.arrive()
        self.assertIsNone(self.lift.destination)

    def test_arrive_message(self):
        '''A lift notify its arrival with a message.'''
        with mock.patch.object(self.lift, 'emit') as mock_emit:
            self.lift.arrive()
            mock_emit.assert_called_once_with('lift.arrived')
