from enum import Enum

LiftStatus = Enum('LiftStatus', 'moving loading ready')
PersonStatus = Enum('PersonStatus', 'busy moving done')
Dirs = Enum('Dirs', 'up down')
