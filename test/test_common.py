'''
Test suite for the common module.
'''

import unittest

import simpleactors as sa

from lifts.common import LiftsActor


class TestLiftsActor(unittest.TestCase):

    '''Tests for the LiftsActor class.'''

    def tearDown(self):
        sa.reset()

    def test_numeric_location(self):
        '''The `numeric_location` must be overridden in child classes.'''
        self.assertRaises(NotImplementedError, LiftsActor)
