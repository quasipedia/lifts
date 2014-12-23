'''
Test suite for the Person class.
'''

import unittest

from lifts.common import Direction
from lifts.person import Person


class MockFloor:

    def __init__(self, numeric_location):
        self.numeric_location = numeric_location


class MockLift:

    def __init__(self, numeric_location, direction, full):
        self.numeric_location = numeric_location
        self.direction = direction
        self.full = full


class TestPerson(unittest.TestCase):

    def setUp(self):
        # For get in tests...
        self.curr_floor = MockFloor(0)
        self.dest_floor = MockFloor(10)
        self.person_in = Person('Joe', self.curr_floor, self.dest_floor)
        # For get out tests...
        self.lift = MockLift(0, Direction.up, False)
        self.person_out = Person('Out', self.lift, self.dest_floor)

    def test_new_call(self):
        '''A freshly spawn person will call a lift.'''
        self.fail()

    def test_no_in_when_full(self):
        '''A person does not step in a full lift.'''
        self.fail()

    def test_no_in_wrong_dir(self):
        '''A person does not step in a lift going the wrong direction.'''
        self.fail()

    def test_in_good_dir(self):
        '''A person step in a lift with correct direction.'''
        self.fail()

    def test_in_no_dir(self):
        '''A person step in a lift with no direction.'''
        self.fail()

    def test_out_correct_floor(self):
        '''A person step out of a lift at the correct floor.'''
        self.fail()

    def test_out_wrong_dir(self):
        '''A person step out of a lift going the wrong way.'''
        self.fail()

    def test_out_no_more_up(self):
        '''A person step out of a lift at top limit to go further up.'''
        self.fail()

    def test_out_no_more_down(self):
        '''A person step out of a lift at bottom limit to go further down.'''
        self.fail()

    def test_arrived(self):
        '''A person emits `person.arrived` and KILL when at destination.'''
        self.fail()

    def test_off_call_again(self):
        '''A person stepping off mid-trip will call a new lift.'''
        self.fail()