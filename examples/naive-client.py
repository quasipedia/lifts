#! /usr/bin/env python3
'''
A very naïve client for the ``lifts`` AI challenge.
'''

import sys
import json


class Client:

    '''An AI client with very naïve behaviour.'''

    def __init__(self, message_fname, command_fname):
        self.messages = open(message_fname)
        self.commands = open(command_fname, 'w')
        self.simulation_is_over = False

    def send_command(self, *args):
        args[0] = args[0].upper()  # the command
        args = map(str, args[1:])  # the command payload
        print(' '.join(args), file=self.commands, flush=True)

    def process_world(self, message):
        '''Process the WORLD message.'''
        world = json.loads(message[1])
        self.lift_ids = [l['name'] for l in world['lifts']]

    def process_turn(self, message):
        '''Process the TURN message.'''
        send_command('ECHO', message)

    def process_ready(self, message):
        '''Process the READY message.'''
        send_command('ECHO', message)

    def process_lift_called(self, message):
        '''Process the LIFT_CALLED message.'''
        send_command('ECHO', message)

    def process_floor_requested(self, message):
        '''Process the FLOOR_REQUESTED message.'''
        send_command('ECHO', message)

    def process_transit(self, message):
        '''Process the TRANSIT message.'''
        send_command('ECHO', message)

    def process_reached(self, message):
        '''Process the REACHED message.'''
        send_command('ECHO', message)

    def process_error(self, message):
        '''Process the ERROR message.'''
        pass

    def process_ended(self, message):
        '''Process the ENDED message.'''
        self.simulation_is_over = True

    def process_stats(self, message):
        '''Process the STATS message.'''
        send_command('ECHO', message)

    def process_message(self):
        '''Retrieve and process a message.'''
        line = self.messages.readline()
        if not line:
            return
        message = line.split()
        getattr(self, 'process_{}'.format(message[0].lower()))(message)

    def run(self):
        '''Play the simulation.'''
        while not self.simulation_is_over:
            self.process_message()


def main():
    if len(sys.argv) != 3:
        print('USAGE: naive-client.py message-file commands-file')
        exit(1)
    client = Client(*sys.argv[1:])
    client.run()


if __name__ == '__main__':
    main()
