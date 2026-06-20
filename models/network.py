from typing import Optional
from .data import Zone, Connection, Drone


class Map:
    def __init__(self) -> None:
        """
        Docstring for __init__
        """
        self.nbr_drones: int = 1
        self.drones: list[Drone] = []
        self.zones: dict[str, Zone] = {}
        self.connections: dict[frozenset[str], Connection] = {}
        # all conections that every zone have
        self.list_adjacents: dict[str, list[str]] = {}
        self.start_hub: Optional[str] = None
        self.end_hub: Optional[str] = None

    def add_zone(self, zone: Zone) -> None:
        """
        Docstring for add_zone
        :param zone: Description
        :type zone: Zone
        """
        self.zones[zone.name] = zone
        self.list_adjacents[zone.name] = []

    def add_connection(self, connection: Connection) -> None:
        """
        Docstring for add_connection
        :param connection: Description
        :type connection: Connection
        """
        zone_a_name, zone_b_name = connection.zones
        self.list_adjacents[zone_a_name].append(zone_b_name)
        self.list_adjacents[zone_b_name].append(zone_a_name)
        self.connections[connection.zones] = connection
