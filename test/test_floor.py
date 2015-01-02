'''
Test suite for the floor module.
'''

import unittest
import unittest.mock as mock

import simpleactors as sa

from lifts.floor import Floor


class TestFloor(unittest.TestCase):

    '''Tests for the Floor class.'''

    def tearDown(self):
        sa.reset()

    def test_call_wrong_floor(self):
        '''A call is ignored if it does not happen at the concerned floor.'''
        self.fail()
