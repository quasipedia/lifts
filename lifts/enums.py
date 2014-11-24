from enum import Enum

Dir = Enum('Dirs', 'up down')
Event = Enum('Event', 'call_button floor_button')
LiftStatus = Enum('LiftStatus', 'moving open closed')
PersonStatus = Enum('PersonStatus', 'idle moving done')
Command = Enum('Command', 'move open close')
Message = Enum('Message', 'started ended lift_call floor_request error')
