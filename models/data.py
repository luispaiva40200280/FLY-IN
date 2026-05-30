from dataclasses import dataclass, field
from typing import Optional
from .constants import DroneState, ZoneType, Coolors


@dataclass(frozen=True)
class Drone:
    name: str
    current_zone: str
    state: DroneState = field(default=DroneState.WAITING)


@dataclass(frozen=True)
class Zone:
    name: str
    x: int
    y: int
    max_drones: int = field(default=1)
    zone: ZoneType = field(default=ZoneType.NORMAL)
    color: Optional[Coolors] = field(default=Coolors.GREEN)


@dataclass(frozen=True)
class Connection:
    zones: frozenset[str]
    max_link_capacity: int = 1
