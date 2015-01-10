'''
Test suite for the interface module.
'''

import unittest
import unittest.mock as mock

import simpleactors as sa

from lifts.interface import FileInterface


class TestFileInterface(unittest.TestCase):

    '''Tests for the FileInterface class.'''

    def setUp(self):
        pass

    def tearDown(self):
        sa.reset()

    def test_init_cleanup(self):
        '''Initiating the interface clean up old files.'''
        self.fail()

    def test_init_create_new_files(self):
        '''Initiating the interface create two new empty files.'''
        self.fail()

    def test_clean_up(self):
        '''Cleanup remove old interface files.'''
        self.fail()

    def test_can_read(self):
        '''FileInterface can read the input file one line at a time.'''
        self.fail()

    def test_empty_lines(self):
        '''The reader can handle correctly empty lines.'''
        self.fail()

    def test_can_write(self):
        '''FileInterface can write the output file.'''
        self.fail()

    def test_validation_unknown_command(self):
        '''Validation fails for unknown commands.'''
        self.fail()

    def test_validation_param_number(self):
        '''Validation fails for wrong number of parameters.'''
        self.fail()

    def test_validation_param_type(self):
        '''Validation fails for wrong type of parameters.'''
        self.fail()

    def test_validation_goto(self):
        '''Validation fail for bogus GOTO parameter.'''
        self.fail()

    def test_validation_open(self):
        '''Validation fail for bogus OPEN parameter.'''
        self.fail()

    def test_validation_close(self):
        '''Validation fail for bogus CLOSE parameter.'''
        self.fail()

    def test_handle_(self):
        '''FileInterface can handle message X correctly.'''
        self.fail()

    def test_parse_(self):
        '''FileInterface can parse message X correctly.'''
        self.fail()
