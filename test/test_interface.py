'''
Test suite for the interface module.
'''

import os
import shutil
import unittest
import unittest.mock as mock

import simpleactors as sa

import lifts.interface as lif
from lifts.common import Message, Command, Direction
from lifts.lift import Lift
from lifts.floor import Floor


def mock_get_by_id(class_, uid):
    '''Mock simpleactors.get_by_id() by echoing it's call arguments.'''
    return class_, uid


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
                lif.FileInterface(self.test_folder)
            except Exception:
                pass
            mock_md.assert_called_once_with(self.test_folder)

    def test_init_create_new_files(self):
        '''Initiating the interface create two new empty files.'''
        iface = lif.FileInterface(self.test_folder)
        self.assertTrue(os.path.exists(iface.in_name))
        self.assertTrue(os.path.exists(iface.out_name))

    def test_init_cleanup(self):
        '''Initiating the interface calls clean_up().'''
        with mock.patch.object(lif.FileInterface, 'cleanup') as mock_cu:
            lif.FileInterface(self.test_folder)
            self.assertTrue(mock_cu.called)


class TestFileInterface(unittest.TestCase):

    '''Tests for the FileInterface class.'''

    test_folder = '/tmp/lifts_test'

    def setUp(self):
        self.iface = lif.FileInterface(self.test_folder)

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
        for expected in ('foo', '', 'bar'):
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

    @mock.patch.object(lif.FileInterface, 'send_message')
    def test_validation_empty_line(self, mock_sm):
        '''Validation fails for empty lines.'''
        self.iface.process_line('')
        calls = mock_sm.call_args_list
        self.assertEqual(1, len(calls))
        code = calls[0][0][0]
        message = calls[0][0][1]
        self.assertEqual(Message.error, code)
        self.assertTrue(message.startswith('Empty line'))

    @mock.patch.object(lif.FileInterface, 'send_message')
    def test_validation_unknown_command(self, mock_sm):
        '''Validation fails for unknown commands.'''
        self.iface.process_line('spam')
        calls = mock_sm.call_args_list
        self.assertEqual(1, len(calls))
        code = calls[0][0][0]
        message = calls[0][0][1]
        self.assertEqual(Message.error, code)
        self.assertTrue(message.startswith('Unknown command'))

    @mock.patch.object(lif.FileInterface, 'send_message')
    def test_validation_param_number(self, mock_sm):
        '''Validation fails for wrong number of parameters.'''
        self.iface.process_line('goto spam foo bar')
        calls = mock_sm.call_args_list
        self.assertEqual(1, len(calls))
        code = calls[0][0][0]
        message = calls[0][0][1]
        self.assertEqual(Message.error, code)
        self.assertTrue(message.startswith('Wrong number of parameters'))

    @mock.patch.object(lif.FileInterface, 'send_message')
    def test_validation_params(self, mock_sm):
        '''Validation fails for invalid parameters.'''
        self.iface.process_line('goto foo bar')
        calls = mock_sm.call_args_list
        self.assertEqual(1, len(calls))
        code = calls[0][0][0]
        message = calls[0][0][1]
        self.assertEqual(Message.error, code)
        self.assertTrue(message.startswith('Invalid parameters'))

    @mock.patch.object(lif, 'get_by_id', new=mock_get_by_id)
    def test_parse_ready_command(self):
        '''Line is correctly parsed for READY.'''
        actual = self.iface.process_line('ready')
        expected = [Command.ready]
        self.assertEqual(expected, actual, open(self.iface.out_name).read())

    @mock.patch.object(lif, 'get_by_id', new=mock_get_by_id)
    def test_parse_goto_command(self):
        '''Line is correctly parsed for GOTO.'''
        actual = self.iface.process_line('goto spam 0')
        expected = [Command.goto, (Lift, 'spam'), (Floor, 0)]
        self.assertEqual(expected, actual, open(self.iface.out_name).read())

    @mock.patch.object(lif, 'get_by_id', new=mock_get_by_id)
    def test_parse_open_command(self):
        '''Line is correctly parsed for OPEN.'''
        actual = self.iface.process_line('open spam up')
        expected = [Command.open, (Lift, 'spam'), Direction.up]
        self.assertEqual(expected, actual, open(self.iface.out_name).read())

    @mock.patch.object(lif, 'get_by_id', new=mock_get_by_id)
    def test_parse_open_command_no_direction(self):
        '''Line is correctly parsed for OPEN when given `none` as direction.'''
        actual = self.iface.process_line('open spam none')
        expected = [Command.open, (Lift, 'spam'), Direction.none]
        self.assertEqual(expected, actual, open(self.iface.out_name).read())

    @mock.patch.object(lif, 'get_by_id', new=mock_get_by_id)
    def test_parse_close_command(self):
        '''Line is correctly parsed for CLOSE.'''
        actual = self.iface.process_line('close spam')
        expected = [Command.close, (Lift, 'spam')]
        self.assertEqual(expected, actual, open(self.iface.out_name).read())

    def test_handle_(self):
        '''FileInterface can handle message X correctly.'''
        self.fail()
