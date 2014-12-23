'''
Test suite for the lift module.
'''

import unittest
import unittest.mock as mock

import simpleactors as sa

from lifts.common import Direction
from lifts.lift import Lift


class TestLift(unittest.TestCase):

    '''Tests for the Lift class.'''

    def tearDown(self):
        sa.reset()

    def test_numeric_location(self):
        '''The numeric location of a lift is the current floor number.'''
        self.fail()

    def test_at_top(self):
        '''A lift knows when it is at the top floor it can reach.'''
        self.fail()

    def test_at_bottom(self):
        '''A lift knows when it is at the bottom floor it can reach.'''
        self.fail()

    def test_full(self):
        '''A lift can detect if it is full.'''
        self.fail()

    def test_is_moving(self):
        '''A lift can detect if it is moving.'''
        self.fail()

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
        self.fail()

    def test_goto_error_out_of_boundaries(self):
        '''A goto command will fail with destination out of top-bottom.'''
        self.fail()

    def test_goto_error_wrong_direction(self):
        '''A goto command will fail with lift moving in opposite direction.'''
        self.fail()

    def test_goto_error_update_past_floor(self):
        '''A goto update command will fail with new destination passed by.'''

    def test_goto_success_from_still(self):
        '''A goto command will succeed for a lift that is still.'''
        self.fail()

    def test_goto_success_update(self):
        '''A goto command can be overridden with new one in same direction.'''
        self.fail()

    def test_open_moving(self):
        '''An open command fails if the lift is still moving.'''
        self.fail()

    def test_open_already_open(self):
        '''An open command will fail for an already open lift.'''
        self.fail()

    def test_open_success(self):
        '''A lift can open upon command.'''
        self.fail()

    def test_close_already_closed(self):
        '''A close command will raies if the lift is already closed.'''
        self.fail()

    def test_close_success(self):
        '''A lift can close upon command.'''
        self.fail()

    def test_arrive(self):
        '''A lift update its status upon arrival.'''
        self.fail()
