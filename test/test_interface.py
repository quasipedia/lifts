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

    def test_can_read(self):
        '''FileInterface can read the input file one line at a time.'''
        self.fail()

    def test_can_write(self):
        '''FileInterface can write the output file.'''
        self.fail()

    def test_clean_up(self):
        '''Old files are removed at the beginning of a new match.'''
        self.fail()

    def test_handle_(self):
        '''FileInterface can handle message X correctly.'''
        self.fail()

    def test_parse_(self):
        '''FileInterface can parse message X correctly.'''
        self.fail()
