'''
The interface of lifts.
'''
import os

from simpleactors import on, Actor, get_by_id

from .common import Message, Command, Direction
from .lift import Lift
from .floor import Floor

COMMANDS = {
    'READY': (),
    'GOTO': (Lift, Floor),  # lid, floor number
    'OPEN': (Lift, Direction),  # lid, intention
    'CLOSE': (Lift, ),  # lid
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
MESSAGE_TO_STRING = {getattr(Message, m.lower()): m for m in MESSAGE_STRINGS}
STRING_TO_COMMAND = {c: getattr(Command, c.lower()) for c in COMMANDS}


class FileInterface(Actor):

    '''
    A player interface using input and output files.

    Arguments:
        directory: the directory where to create the input/output files
    '''
    msg_components = ('command', 'lift', 'floor')

    def __init__(self, directory):
        super().__init__()
        directory = os.path.realpath(directory)
        if not os.path.exists(directory):
            os.makedirs(directory)
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
            return line.strip()  # Takes care of empty lines
        self.fin.seek(bookmark)

    def write(self, line):
        print(line.strip(), file=self.fout, flush=True)

    def process_line(self, line):
        '''Parse and validate a received line, return None for failures.'''
        bits = line.split()
        # Empty line
        if not bits:
            self.send_message(Message.error, 'Empty line')
            return
        # Unknown command
        command = bits.pop(0).upper()
        if command not in COMMANDS:
            msg = 'Unknown command "{}"'.format(command)
            self.send_message(Message.error, msg)
            return
        # Wrong number of parameters
        ptypes = COMMANDS[command]
        if len(bits) != len(ptypes):
            msg = 'Wrong number of parameters for "{}"'.format(line)
            self.send_message(Message.error, msg)
            return
        # Parse the parameters to objects
        new_bits = []
        for bit, type_ in zip(bits, ptypes):
            if type_ in (Floor, Lift):
                if type_ is Floor:
                    try:
                        bit = int(bit)
                    except ValueError:
                        bit = None
                new_bits.append(get_by_id(type_, bit))
            if type_ is Direction:
                try:
                    new_bits.append(getattr(Direction, bit.lower()))
                except AttributeError:
                    new_bits.append(None)
        # Wrong types of parameters
        if None in new_bits:
            msg = 'Invalid parameters for "{}"'.format(line)
            self.send_message(Message.error, msg)
            return
        return [STRING_TO_COMMAND[command]] + new_bits

    def get_commands(self):
        while True:
            line = self.read()
            if line is None:  # end of file
                break
            payload = self.process_line(line)
            if payload is None:  # invalid line
                continue
            yield payload

    def send_message(self, message, entity, *args):
        bits = [MESSAGE_TO_STRING[message]]
        if entity:
            bits.append(entity)
        bits += args
        self.write(' '.join(map(str, bits)))
