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
        print(' '.join(args), file=self.commands)

    def process_world(self, message):
        '''Process the WORLD command.'''
        world = json.loads(message[1])
        self.lift_ids = [l['name'] for l in world['lifts']]

    def process_started(self, message):
        '''Process the STARTED command.'''
        pass

    def process_ended(self, message):
        '''Process the ENDED command.'''
        self.simulation_is_over = True

    def process_lift_called(self, message):
        '''Process the LIFT_CALLED command.'''
        floor = int(message[1])
        for lift_id in self.lift_ids:
            send_command('move', lift_id, floor)

    def process_floor_requested(self, message):
        '''Process the FLOOR_REQUESTED command.'''
        raise NotImplementedError

    def process_error(self, message):
        '''Process the ERROR command.'''
        raise NotImplementedError

    def process_stats(self, message):
        '''Process the STATS command.'''
        raise NotImplementedError

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
