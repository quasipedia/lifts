'''
Test suite for the person module.
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
        self.passengers = set()

    @property
    def numeric_location(self):
        return self.location.numeric_location


class TestPersonIn(unittest.TestCase):

    '''Tests for `walk in` action of a person.'''

    def setUp(self):
        self.ground_floor = MockFloor(0)
        self.top_floor = MockFloor(10)
        self.lift = MockLift(self.ground_floor, Direction.up, False)
        # For get in tests...
        self.person = Person('Foo', self.ground_floor, self.top_floor)

    def tearDown(self):
        sa.reset()

    def test_string(self):
        '''The string representation of a Person is its pid.'''
        self.assertEqual('Person: Foo', '{}'.format(self.person))

    @mock.patch.object(Person, 'call_lift')
    def test_new_call(self, mock_call):
        '''A freshly spawn person will call a lift.'''
        Person('Spam', self.ground_floor, self.top_floor)
        mock_call.assert_called_once_with()

    @mock.patch.object(Person, 'arrive')
    def test_spawn_at_destination(self, mock_arrive):
        '''A person spawn at destination, immediately arrives.'''
        Person('Spam', self.ground_floor, self.ground_floor)
        mock_arrive.assert_called_once_with()

    def test_no_in_when_full(self):
        '''A person does not step in a full lift.'''
        self.lift.full = True
        with mock.patch.object(self.person, 'emit') as mock_emit:
            self.person.on_lift_open('lift.open', self.lift)
            self.assertFalse(mock_emit.called)

    def test_no_in_wrong_dir(self):
        '''A person does not step in a lift going the wrong direction.'''
        self.lift.direction = Direction.down
        with mock.patch.object(self.person, 'emit') as mock_emit:
            self.person.on_lift_open('lift.open', self.lift)
            self.assertFalse(mock_emit.called)

    def test_in_good_dir(self):
        '''A person step in a lift with correct direction.'''
        self.lift.direction = Direction.up  # Redoundant, but make test clearer
        with mock.patch.object(self.person, 'emit') as mock_emit:
            self.person.on_lift_open('lift.open', self.lift)
            mock_emit.assert_called_once_with('person.lift.on', self.lift)

    def test_in_no_dir(self):
        '''A person step in a lift with no direction.'''
        self.lift.direction = Direction.none
        with mock.patch.object(self.person, 'emit') as mock_emit:
            self.person.on_lift_open('lift.open', self.lift)
            mock_emit.assert_called_once_with('person.lift.on', self.lift)

    def test_in_add_passenger(self):
        '''The passenger list get updated on a person walking in.'''
        self.lift.direction = Direction.up  # Redoundant, but make test clearer
        self.person.on_lift_open('lift.open', self.lift)
        self.assertEqual({self.person}, self.lift.passengers)

    def test_in_change_location_to_lift(self):
        '''A passenger's location changes when getting in a lift.'''
        self.lift.direction = Direction.up  # Redoundant, but make test clearer
        self.person.on_lift_open('lift.open', self.lift)
        self.assertEqual(self.lift, self.person.location)


class TestPersonOut(unittest.TestCase):

    '''Tests for `walk out` action of a person.'''

    def setUp(self):
        self.ground_floor = MockFloor(0)
        self.top_floor = MockFloor(10)
        self.lift = MockLift(self.ground_floor, Direction.up, False)
        self.person = Person('Bar', self.lift, self.top_floor)
        self.lift.passengers = {self.person}

    def tearDown(self):
        sa.reset()

    def test_out_correct_floor(self):
        '''A person step out of a lift at the correct floor.'''
        self.lift.location = self.top_floor
        with mock.patch.object(self.person, 'emit') as mock_emit:
            self.person.on_lift_open('lift.open', self.lift)
            expected = ('person.lift.off', self.lift)
            actual = mock_emit.mock_calls[0][1]
            self.assertEqual(expected, actual)

    def test_out_wrong_dir(self):
        '''A person step out of a lift going the wrong way.'''
        self.lift.direction = Direction.down
        with mock.patch.object(self.person, 'emit') as mock_emit:
            self.person.on_lift_open('lift.open', self.lift)
            expected = ('person.lift.off', self.lift)
            actual = mock_emit.mock_calls[0][1]
            self.assertEqual(expected, actual)

    def test_out_no_more_up(self):
        '''A person step out of a lift at top limit to go further up.'''
        self.lift.at_top = True
        with mock.patch.object(self.person, 'emit') as mock_emit:
            self.person.on_lift_open('lift.open', self.lift)
            expected = ('person.lift.off', self.lift)
            actual = mock_emit.mock_calls[0][1]
            self.assertEqual(expected, actual)

    def test_no_out_intermediate_stop(self):
        '''A person does not step out at an intermediate stop.'''
        self.lift.location = MockFloor(5)
        with mock.patch.object(self.person, 'emit') as mock_emit:
            self.person.on_lift_open('lift.open', self.lift)
            print(mock_emit.mock_calls)
            self.assertFalse(mock_emit.called)

    def test_out_no_more_down(self):
        '''A person step out of a lift at bottom limit to go further down.'''
        self.lift.at_bottom = True
        self.lift.direction = Direction.down
        self.lift.location = self.top_floor
        self.person.destination = self.ground_floor
        with mock.patch.object(self.person, 'emit') as mock_emit:
            self.person.on_lift_open('lift.open', self.lift)
            expected = ('person.lift.off', self.lift)
            actual = mock_emit.mock_calls[0][1]
            self.assertEqual(expected, actual)

    def test_out_remove_passenger(self):
        '''The passenger list get updated on a person walking out.'''
        self.lift.location = self.top_floor
        self.lift.passengers = {self.person}
        self.person.on_lift_open('lift.open', self.lift)
        self.assertEqual(set(), self.lift.passengers)

    def test_out_change_location_to_floor(self):
        '''A passenger's location changes when getting in a lift.'''
        self.lift.location = self.top_floor
        self.lift.passengers = {self.person}
        self.person.on_lift_open('lift.open', self.lift)
        self.assertEqual(self.person.location, self.lift.location)

    def test_arrived(self):
        '''A person emits `person.arrived` and KILL when at destination.'''
        self.lift.location = self.top_floor
        with mock.patch.object(self.person, 'emit') as mock_emit:
            self.person.arrive()
            expected = ('person.arrived', )
            actual = mock_emit.mock_calls[0][1]
            self.assertEqual(expected, actual)
            expected = (sa.KILL, self.person)
            actual = mock_emit.mock_calls[1][1]
            self.assertEqual(expected, actual)

    def test_off_call_again(self):
        '''A person stepping off mid-trip will call a new lift.'''
        self.lift.at_top = True
        with mock.patch.object(self.person, 'call_lift') as mock_call:
            self.person.on_lift_open('lift.open', self.lift)
            mock_call.assert_called_once_with()
