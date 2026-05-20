from data import Zone, Connection
from typing import Optional


class Map:
    def __init__(self) -> None:
        self.nbr_drones: int = 0
        self.zones: dict[str, Zone] = {}
        self.connections: dict[frozenset[str], Connection] = {}
        # all conections that every zone have
        self.list_adjacents: dict[str, list[str]] = {}
        self.start_hub: Optional[str] = None
        self.end_hub: Optional[str] = None

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.name] = zone
        self.list_adjacents[zone.name] = []

    def add_connection(self, connection: Connection) -> None:
        zone_a_name, zone_b_name = connection.zones
        self.list_adjacents[zone_a_name].append(zone_b_name)
        self.list_adjacents[zone_b_name].append(zone_a_name)
        self.connections[connection.zones] = connection
