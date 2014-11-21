from enum import Enum

LiftStatus = Enum('LiftStatus', 'moving loading ready')
PersonStatus = Enum('PersonStatus', 'busy moving done')
Dir = Enum('Dirs', 'up down')
Event = Enum('Event', 'call_button floor_button')
