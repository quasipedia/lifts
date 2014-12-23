'''
Test suite for the Person class.
'''

import unittest
import unittest.mock as mock

import simpleactors as sa

from lifts.common import Direction
from lifts.person import Person


class MockFloor:

    def __init__(self, numeric_location):
        self.numeric_location = numeric_location


class MockLift:

    def __init__(self, location, direction, full):
        self.location = location
        self.direction = direction
        self.full = full
        self.at_top = False
        self.at_bottom = False

    @property
    def numeric_location(self):
        return self.location.numeric_location


class TestPerson(unittest.TestCase):

    def setUp(self):
        self.ground_floor = MockFloor(0)
        self.top_floor = MockFloor(10)
        self.lift = MockLift(self.ground_floor, Direction.up, False)
        # For get in tests...
        self.person_at_floor = Person('Foo', self.ground_floor, self.top_floor)
        # For get out tests...
        self.person_on_lift = Person('Bar', self.lift, self.top_floor)

    def tearDown(self):
        sa.reset()

    @mock.patch.object(Person, 'call_lift')
    def test_new_call(self, mock_call):
        '''A freshly spawn person will call a lift.'''
        Person('Spam', self.ground_floor, self.top_floor)
        mock_call.assert_called_once_with()

    def test_no_in_when_full(self):
        '''A person does not step in a full lift.'''
        self.lift.full = True
        with mock.patch.object(self.person_at_floor, 'emit') as mock_emit:
            self.person_at_floor.on_lift_open('lift.open', self.lift)
            self.assertFalse(mock_emit.called)

    def test_no_in_wrong_dir(self):
        '''A person does not step in a lift going the wrong direction.'''
        self.lift.direction = Direction.down
        with mock.patch.object(self.person_at_floor, 'emit') as mock_emit:
            self.person_at_floor.on_lift_open('lift.open', self.lift)
            self.assertFalse(mock_emit.called)

    def test_in_good_dir(self):
        '''A person step in a lift with correct direction.'''
        self.lift.direction = Direction.up  # Redoundant, but make test clearer
        with mock.patch.object(self.person_at_floor, 'emit') as mock_emit:
            self.person_at_floor.on_lift_open('lift.open', self.lift)
            mock_emit.assert_called_once_with('person.lift.on', self.lift)

    def test_in_no_dir(self):
        '''A person step in a lift with no direction.'''
        self.lift.direction = Direction.none
        with mock.patch.object(self.person_at_floor, 'emit') as mock_emit:
            self.person_at_floor.on_lift_open('lift.open', self.lift)
            mock_emit.assert_called_once_with('person.lift.on', self.lift)

    def test_out_correct_floor(self):
        '''A person step out of a lift at the correct floor.'''
        self.lift.location = self.top_floor
        with mock.patch.object(self.person_on_lift, 'emit') as mock_emit:
            self.person_on_lift.on_lift_open('lift.open', self.lift)
            expected = ('person.lift.off', self.lift)
            actual = mock_emit.mock_calls[0][1]
            self.assertEqual(expected, actual)

    def test_out_wrong_dir(self):
        '''A person step out of a lift going the wrong way.'''
        self.lift.direction = Direction.down
        with mock.patch.object(self.person_on_lift, 'emit') as mock_emit:
            self.person_on_lift.on_lift_open('lift.open', self.lift)
            expected = ('person.lift.off', self.lift)
            actual = mock_emit.mock_calls[0][1]
            self.assertEqual(expected, actual)

    def test_out_no_more_up(self):
        '''A person step out of a lift at top limit to go further up.'''
        self.lift.at_top = True
        with mock.patch.object(self.person_on_lift, 'emit') as mock_emit:
            self.person_on_lift.on_lift_open('lift.open', self.lift)
            expected = ('person.lift.off', self.lift)
            actual = mock_emit.mock_calls[0][1]
            self.assertEqual(expected, actual)

    def test_out_no_more_down(self):
        '''A person step out of a lift at bottom limit to go further down.'''
        self.lift.at_bottom = True
        self.lift.direction = Direction.down
        self.lift.location = self.top_floor
        self.person_on_lift.destination = self.ground_floor
        with mock.patch.object(self.person_on_lift, 'emit') as mock_emit:
            self.person_on_lift.on_lift_open('lift.open', self.lift)
            expected = ('person.lift.off', self.lift)
            actual = mock_emit.mock_calls[0][1]
            self.assertEqual(expected, actual)

    def test_arrived(self):
        '''A person emits `person.arrived` and KILL when at destination.'''
        self.lift.location = self.top_floor
        with mock.patch.object(self.person_on_lift, 'emit') as mock_emit:
            self.person_on_lift.arrive()
            expected = ('person.arrived', )
            actual = mock_emit.mock_calls[0][1]
            self.assertEqual(expected, actual)
            expected = (sa.KILL, self.person_on_lift)
            actual = mock_emit.mock_calls[1][1]
            self.assertEqual(expected, actual)

    def test_off_call_again(self):
        '''A person stepping off mid-trip will call a new lift.'''
        self.lift.at_top = True
        with mock.patch.object(self.person_on_lift, 'call_lift') as mock_call:
            self.person_on_lift.on_lift_open('lift.open', self.lift)
            mock_call.assert_called_once_with()
