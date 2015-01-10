'''
The interface of lifts.
'''
import os

from simpleactors import on, INITIATE

from .common import LiftsActor, Message, Command

COMMANDS = {
    'READY': (0, ),
    'GOTO': (1, int),  # Floor number
    'OPEN': (2, str, str),  # lid, intention
    'CLOSE': (1, str),  # lid
}
MESSAGE_STRINGS = (
    'WORLD',
    'TURN',
    'READY',
    'LIFT_CALL',
    'FLOOR_REQUEST',
    'TRANSIT',
    'ARRIVED',
    'ERROR',
    'END',
    'STATS',
)
MESSAGE_TO_STRING = dict(zip(Message, MESSAGE_STRINGS))
STRING_TO_COMMAND = dict(zip(COMMANDS.keys(), Command))


class FileInterface(LiftsActor):

    '''
    A player interface using input and output files.

    Arguments:
        directory: the directory where to create the input/output files
    '''
    msg_components = ('command', 'lift', 'floor')

    def __init__(self, directory):
        super().__init__()
        directory = os.path.realpath(directory)
        self.in_name = os.path.join(directory, 'lifts.in')
        self.out_name = os.path.join(directory, 'lifts.out')
        self.cleanup()
        open(self.in_name, 'w')  # Create the file
        self.fin = open(self.in_name, 'r')
        self.fout = open(self.out_name, 'w')

    def cleanup(self):
        for fname in (self.in_name, self.out_name):
            try:
                os.remove(fname)
            except FileNotFoundError:
                pass

    def read(self):
        bookmark = self.fin.tell()
        line = self.fin.readline()
        if line:
            return line.strip()
        self.fin.seek(bookmark)

    def write(self, line):
        print(line.strip(), file=self.fout, flush=True)

    def _parse_and_validate(self, line):
        '''Parse and validate a received line, return None for failures.'''
        bits = line.split()
        # Is there any
        try:
            bits[0] = STRING_TO_COMMAND[bits[0]]
        except KeyError:
            msg = 'Unknown command "{}" in line "{}"'.format(bits[0], line)
            self.send_message(Message.error, msg)
            return None
        if bits[2] is not None:
            try:
                bits[2] = int(bits[2])
            except ValueError:
                msg = 'Cannot understand floor "{}" in line "{}"'.format(
                    bits[2], line)
                self.send_message(Message.error, msg)
                return None
        return bits[:3]

    def get_commands(self):
        while True:
            line = self.read()
            if line == '':  # empty line
                continue
            if line is None:  # end of file
                break
            payload = self._parse_and_validate(line)
            if payload is None:
                break
            yield payload

    def send_message(self, message, entity, *args):
        bits = [MESSAGE_TO_STRING[message]]
        if entity:
            bits.append(entity)
        bits += args
        self.write(' '.join(map(str, bits)))
