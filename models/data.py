from dataclasses import dataclass, field
from typing import Optional
from .constants import DroneState, ZoneType, Coolors


@dataclass
class Drone:
    name: str
    current_zone: str
    path: list[str] = []
    state: DroneState = field(default=DroneState.WAITING)
    transit_timer: int = field(default=0)
    destination: Optional[str] = field(default=None)


@dataclass
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
