'''
Test suite for the interface module.
'''

import unittest
import unittest.mock as mock

import simpleactors as sa

from lifts.interface import FileInterface


class TestFileInterface(unittest.TestCase):

    '''Tests for the FileInterface class.'''

    def tearDown(self):
        sa.reset()

    def test_(self):
        self.fail()
