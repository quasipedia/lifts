'''
Test suite for the interface module.
'''

import os
import shutil
import unittest
import unittest.mock as mock

import simpleactors as sa

from lifts.interface import FileInterface


class TestFileInterfaceInitiation(unittest.TestCase):

    '''Tests for the FileInterface __init__ method.'''

    test_folder = '/tmp/foobar'

    def tearDown(self):
        try:
            shutil.rmtree(self.test_folder)
        except FileNotFoundError:
            pass

    def test_init_create_directory(self):
        '''Initiating the interface create the directory if missing.'''
        with mock.patch.object(os, 'makedirs') as mock_md:
            try:
                FileInterface(self.test_folder)
            except Exception:
                pass
            mock_md.assert_called_once_with(self.test_folder)

    def test_init_create_new_files(self):
        '''Initiating the interface create two new empty files.'''
        iface = FileInterface(self.test_folder)
        self.assertTrue(os.path.exists(iface.in_name))
        self.assertTrue(os.path.exists(iface.out_name))

    def test_init_cleanup(self):
        '''Initiating the interface calls clean_up().'''
        with mock.patch.object(FileInterface, 'cleanup') as mock_cu:
            FileInterface(self.test_folder)
            self.assertTrue(mock_cu.called)


class TestFileInterface(unittest.TestCase):

    '''Tests for the FileInterface class.'''

    test_folder = '/tmp/lifts_test'

    def setUp(self):
        self.iface = FileInterface(self.test_folder)

    def tearDown(self):
        sa.reset()
        shutil.rmtree(self.test_folder)

    def test_cleanup(self):
        '''Cleanup remove old interface files.'''
        self.iface.cleanup()
        self.assertFalse(os.path.exists(self.iface.in_name))
        self.assertFalse(os.path.exists(self.iface.out_name))

    def test_read(self):
        '''FileInterface can read the input file one line at a time.'''
        with open(self.iface.in_name, 'a') as file_:
            print('foo', file=file_)
            print('bar', file=file_)
        for expected in ('foo', 'bar'):
            self.assertEqual(expected, self.iface.read())

    def test_read_empty_lines(self):
        '''The reader can handle correctly empty lines.'''
        with open(self.iface.in_name, 'a') as file_:
            print('foo', file=file_)
            print('', file=file_)
            print('bar', file=file_)
        for expected in ('foo', None, 'bar'):
            self.assertEqual(expected, self.iface.read())

    def test_read_EOF(self):
        '''The reader can handle correctly EOF.'''
        with open(self.iface.in_name, 'a') as file_:
            print('foo', file=file_)
        for expected in ('foo', None, None):
            self.assertEqual(expected, self.iface.read())

    def test_can_write(self):
        '''FileInterface can write the output file.'''
        self.iface.write('spam')
        actual = open(self.iface.out_name).read()
        self.assertEqual('spam\n', actual)

    @mock.patch.object(FileInterface, 'send_message')
    def test_validation_unknown_command(self, mock_sm):
        '''Validation fails for unknown commands.'''
        self.iface._process_line('spam')
        mock_sm.assert_called_once_with('x')

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
