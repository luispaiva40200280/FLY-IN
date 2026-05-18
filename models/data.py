from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class DroneState(Enum):
    WAITING = 'waiting'
    IN_TRANSIT = 'in_transit'
    ARRIVED = 'arrived'


@dataclass
class Drone:
    name: str
    current_zone: str
    state: DroneState = field(default=DroneState.WAITING)


class ZoneType(Enum):
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'


@dataclass
class Zone:
    name: str
    x: int
    y: int
    max_drones: int = field(default=1)
    zone_type: ZoneType = field(default=ZoneType.NORMAL)
    zone_color: Optional[str] = field(default=None)


@dataclass
class Connection:
    zones: frozenset[str]
    max_link_capacity: int = 1
