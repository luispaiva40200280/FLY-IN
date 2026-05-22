from enum import Enum


class ZoneType(Enum):
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'


class DroneState(Enum):
    WAITING = 'waiting'
    IN_TRANSIT = 'in_transit'
    ARRIVED = 'arrived'


# ToDo constans to transform colors in anscii codes
class Coolors(Enum):
    pass
