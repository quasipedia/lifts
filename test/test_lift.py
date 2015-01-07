'''
Test suite for the lift module.
'''

import unittest
import unittest.mock as mock
from pickle import dumps

import simpleactors as sa

from lifts.lift import Lift
from lifts.common import Direction


class MockFloor:

    def __init__(self, numeric_location):
        self.numeric_location = numeric_location


class TestLiftParams(unittest.TestCase):

    '''Tests for the validation of the parameters passed to the Lift class.'''

    def init_lift(self, capacity=2, transit_time=3, accel_time=6,
                  bottom_floor_number=0, top_floor_number=10, location=5):
        '''Utility function to initialise a lift.'''
        description = dict(
            lid='Spam',
            capacity=capacity,
            transit_time=transit_time,
            accel_time=accel_time,
            bottom_floor_number=bottom_floor_number,
            top_floor_number=top_floor_number)
        Lift(description, MockFloor(location))

    def test_integer(self):
        '''Capacity and shaft limits for a lift must be integers.'''
        self.assertRaises(ValueError, self.init_lift, capacity=1.5)
        self.assertRaises(ValueError, self.init_lift, top_floor_number=10.5)
        self.assertRaises(ValueError, self.init_lift, bottom_floor_number=0.5)

    def test_capacity(self):
        '''Capacity must be at least 1.'''
        self.assertRaises(ValueError, self.init_lift, capacity=0)

    def test_relative_times(self):
        '''Accel time must be longer than transit time.'''
        self.assertRaises(ValueError, self.init_lift, accel_time=3)

    def test_excursion(self):
        '''The lift must have some excursion.'''
        self.assertRaises(ValueError, self.init_lift, top_floor_number=0)

    def test_initial_location(self):
        '''Initial location of a lift must be within its excursion.'''
        self.assertRaises(ValueError, self.init_lift, location=11)


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
        self.floors = [MockFloor(f) for f in range(0, 11)]
        self.ground_floor = self.floors[0]
        self.top_floor = self.floors[10]
        for floor in self.floors:
            num = floor.numeric_location
            floor.below = self.floors[num - 1] if num > 0 else None
            floor.above = self.floors[num + 1] if num < 10 else None
        self.lift = Lift(description, self.ground_floor)
        self.maxDiff = None

    def tearDown(self):
        sa.reset()

    def test_numeric_location(self):
        '''The numeric location of a lift is the current floor number.'''
        self.assertEqual(0, self.lift.numeric_location)

    def test_string_representation(self):
        '''A lift's string representation is its lid.'''
        self.assertEqual('Lift: SpamLift', '{}'.format(self.lift))

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
        with mock.patch.object(self.lift, 'emit') as mock_emit:
            self.lift.destination = self.ground_floor
            self.lift.goto(self.lift, self.top_floor)
            mock_emit.assert_called_once_with(err_msg)
        with mock.patch.object(self.lift, 'emit') as mock_emit:
            self.lift.destination = self.top_floor
            self.lift.goto(self.lift, self.ground_floor)
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

    def test_open_ignore(self):
        '''An open command is ignored if it does not concern self.'''
        self.lift.open('<some-other-lift>')
        self.assertFalse(self.lift.open_doors)

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

    def test_open_with_intent(self):
        '''It is possible to "promise" a direction when opening doors.'''
        self.lift.open(self.lift, intent=Direction.up)
        self.assertEqual(self.lift.direction, Direction.up)

    def test_close_ignore(self):
        '''An close command is ignored if it does not concern self.'''
        self.lift.open_doors = True
        self.lift.close('<some-other-lift>')
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

    def test_close_reset_intention(self):
        '''Closing the doors reset the intentions.'''
        self.lift.open(self.lift, intent=Direction.up)
        self.lift.close(self.lift)
        self.assertEqual(Direction.none, self.lift.direction)

    def test_arrive_status(self):
        '''A lift resets its destination upon arrival.'''
        self.lift.destination = self.top_floor
        self.lift.arrive()
        self.assertIsNone(self.lift.destination)

    def test_arrive_message(self):
        '''A lift notify its arrival with a message.'''
        with mock.patch.object(self.lift, 'emit') as mock_emit:
            self.lift.arrive()
            mock_emit.assert_called_once_with('lift.arrive', floor=None)

    def test_turn_action_no_action(self):
        '''A lift will stay still during a turn if no destination.'''
        before = dumps(self.lift)
        self.lift.take_turn(1)
        after = dumps(self.lift)
        self.assertEqual(before, after)

    def test_turn_action_update_position_up(self):
        '''A lift will update its position during its turn [up].'''
        self.lift.destination = self.top_floor
        with mock.patch.object(self.lift, 'emit') as mock_emit:
            self.lift.take_turn(4)
            mock_emit.assert_called_once_with('lift.transit',
                                              floor=self.ground_floor.above)

    def test_turn_action_update_position_down(self):
        '''A lift will update its position during its turn [down].'''
        self.lift.destination = self.ground_floor
        self.lift.location = self.top_floor
        with mock.patch.object(self.lift, 'emit') as mock_emit:
            self.lift.take_turn(4)
            mock_emit.assert_called_once_with('lift.transit',
                                              floor=self.top_floor.below)

    def test_turn_action_reach_destination(self):
        '''A lift will stop and change its status if reach destination.'''
        self.lift.destination = self.floors[1]
        with mock.patch.object(self.lift, 'emit') as mock_emit:
            self.lift.take_turn(7)
            mock_emit.assert_called_once_with('lift.arrive',
                                              floor=self.ground_floor.above)
        self.assertFalse(self.lift.is_moving)

    def test_turn_multiple_transit_updates(self):
        '''A lift updates position multiple times in one turn if needed.'''
        self.lift.destination = self.top_floor
        with mock.patch.object(self.lift, 'emit') as mock_emit:
            self.lift.take_turn(7)
            expected = (
                (('lift.transit', ), {'floor': self.floors[1]}),
                (('lift.transit', ), {'floor': self.floors[2]}))
            self.assertSequenceEqual(expected, mock_emit.call_args_list)

    def test_turn_multiple_transit_updates_and_arrive(self):
        '''A lift can transit and arrive during the same turn.'''
        self.lift.destination = self.floors[2]
        with mock.patch.object(self.lift, 'emit') as mock_emit:
            self.lift.take_turn(10)
            expected = (
                (('lift.transit', ), {'floor': self.floors[1]}),
                (('lift.arrive', ), {'floor': self.floors[2]}))
            self.assertSequenceEqual(expected, mock_emit.call_args_list)
