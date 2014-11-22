from enum import Enum

LiftStatus = Enum('LiftStatus', 'moving loading ready')
PersonStatus = Enum('PersonStatus', 'busy moving done')
Dir = Enum('Dirs', 'up down')
Event = Enum('Event', 'call_button floor_button')
Commands = Enum('Commands', 'move open close')
Messages = Enum('Messages', 'started ended lift_call floor_request error')
