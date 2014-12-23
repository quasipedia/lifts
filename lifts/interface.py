'''
The interface of lifts.
'''
import os

from simpleactors import on, Actor, INITIATE

from enums import Message, Command

COMMAND_STRINGS = (
    'MOVE',
    'OPEN',
    'CLOSE',
)
MESSAGE_STRINGS = (
    'WORLD',
    'TURN',
    'READY',
    'LIFT_CALL',
    'FLOOR_REQUEST',
    'TRANSIT',
    'STOP',
    'ERROR',
    'END',
    'STATS',
)
MESSAGE_TO_STRING = dict(zip(Message, MESSAGE_STRINGS))
STRING_TO_COMMAND = dict(zip(COMMAND_STRINGS, Command))


class FileInterface:

    msg_components = ('command', 'lift', 'floor')

    def __init__(self, fid):
        self.in_name = '{}.in'.format(fid)
        self.out_name = '{}.out'.format(fid)
        self.cleanup()
        open(self.in_name, 'w')  # Create the file if not there
        self.fin = open(self.in_name, 'r')
        self.fout = open(self.out_name, 'w')

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
        bits = line.split() + [None] * 3
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

    def cleanup(self):
        for fname in (self.in_name, self.out_name):
            try:
                os.remove(fname)
            except FileNotFoundError:
                pass


class FileInterface(Actor):

    @on(INITIATE)
    def init(self):
        pass
