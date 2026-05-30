from typing import Optional
from .data import Zone, Connection, Drone
from .constants import DroneState


class Map:
    def __init__(self) -> None:
        self.nbr_drones: int = 1
        self.drones: list[Drone] = []
        self.zones: dict[str, Zone] = {}
        self.connections: dict[frozenset[str], Connection] = {}
        # all conections that every zone have
        self.list_adjacents: dict[str, list[str]] = {}
        self.start_hub: Optional[str] = None
        self.end_hub: Optional[str] = None
        self._initialize_drones()

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.name] = zone
        self.list_adjacents[zone.name] = []

    def add_connection(self, connection: Connection) -> None:
        zone_a_name, zone_b_name = connection.zones
        self.list_adjacents[zone_a_name].append(zone_b_name)
        self.list_adjacents[zone_b_name].append(zone_a_name)
        self.connections[connection.zones] = connection

    def _initialize_drones(self) -> None:
        """
        Creates the required number of Drone objects and places them
        at the starting hub.
        """

        for i in range(1, self.nbr_drones + 1):
            new_drone = Drone(
                name=f"D{i}",
                current_zone=self.start_hub or "start",
                state=DroneState.WAITING
            )
            self.drones.append(new_drone)
