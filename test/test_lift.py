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
