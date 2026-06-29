import re
import sys
from typing import Any
from .constants import Coolors, ZoneType, DroneState
from .network import Map, Zone, Connection, Drone


class MapError(Exception):
    """
    Error class for map constructer
    """
    pass


class ParserMap:
    def __init__(self) -> None:
        self.map: Map = Map()
        self.line_nbr: int = 0

    def _parse_nbr_drones(self, line: str) -> int:
        """
        Parse the actal number of the drones for the
        network. Changes the str value to an int.

        Args:
            line (str): line to parse

        Raises:
            ValueError: For negative numbers
        Returns:
            nbr_drones (int): Number of drones that the network has
        """
        nbr_drones = line.split(':', 1)[1]
        if int(nbr_drones) < 1:
            raise ValueError("Nbr of drone can not be less than 1")
        return int(nbr_drones)

    @staticmethod
    def _parse_meta_data(metadata_str: str) -> dict[str, Any]:
        """
        General parser method for the metada data in a line.

        Args:
            metadata_str (str): Part of the line that holds the
                metadata information.

        Returns:
            metadata (dict): actual data for creating the objects necessary for
                the construction of the network.
        """
        metadata: dict[str, Any] = {}
        for data in metadata_str.split():
            if "=" not in data:
                raise ValueError("Error geting the metadata for the hub")
            else:
                key, value = data.split("=")
                if key == "max_drones":
                    metadata[key] = int(value)
                elif key == "zone":
                    metadata[key] = ZoneType(value)
                elif key == 'max_link_capacity':
                    metadata[key] = int(value)
                else:
                    metadata[key] = value
                if key == 'color':
                    try:
                        metadata[key] = Coolors[value.upper()]
                    except KeyError:
                        metadata[key] = Coolors["CYAN"]

        return metadata

    def _parser_hubs(self, line: str) -> 'Zone':
        """
        Method to parse each the zone data using regex to see
        what kind of data it has.

        Args:
            line (str): file line that holds the zone informacion

        Returns:
            new_zone (Zone): the instance of the object zone whith all the
                data necessary.
        """
        pattern: str = (r"^(start_hub|end_hub|hub):\s+([^\s\-]+)\s"
                        r"+(-?\d+)\s+(-?\d+)\s*(?:\[(.*?)\])?")
        data = re.search(pattern, line)
        if not data:
            raise ValueError("Couldnt extract the hub information")
        prefix, name, x, y, metadata_str = data.groups()
        if prefix == 'start_hub':
            self.map.start_hub = name
        if prefix == "end_hub":
            self.map.end_hub = name

        metadata: dict[str, Any] = {}
        if metadata_str:
            metadata = self._parse_meta_data(metadata_str)

        new_zone: Zone = Zone(name=name, x=int(x), y=int(y), **metadata)
        return new_zone

    def _parse_connections(self, line: str) -> None:
        """
        Parser for the creation of the connection of two zones in
        the map.

        Args:
            line (str): file line that holds the connection informacion
        """
        pattern = r"^(connection):\s+([^\s\-]+)-([^\s\-]+)\s*(?:\[(.*?)\])?"
        data_connec = re.search(pattern, line)
        if not data_connec:
            raise ValueError("Could'nt extract the Connction info...")
        _, zone_a, zone_b, metadata_str = data_connec.groups()
        if (zone_a not in self.map.zones) or (zone_b not in self.map.zones):
            raise ValueError(f" {zone_a}/{zone_b} not part of the map!")
        kwargs: dict[str, Any] = {}
        if metadata_str:
            kwargs = self._parse_meta_data(metadata_str)
        zones_connect = frozenset([zone_a, zone_b])
        connection: Connection = Connection(zones_connect,
                                            **kwargs)
        self.map.add_connection(connection=connection)

    def _check_map_complete(self) -> None:
        """
        Check map completion seing if the end and start zones
        exist in the parser and conferming there max dornes capacity to
        the max drones in the map.
        """
        if self.map.start_hub is None:
            raise MapError("Map needs to have an starting point")
        if self.map.end_hub is None:
            raise MapError("Map needs to have ending point")
        self.map.zones[self.map.start_hub].max_drones = self.map.nbr_drones
        self.map.zones[self.map.end_hub].max_drones = self.map.nbr_drones

    def _initialize_drones(self) -> None:
        """
        Creates the required number of Drone objects and places them
        at the starting hub.
        """
        for i in range(1, self.map.nbr_drones + 1):
            new_drone = Drone(
                name=f"D{i}",
                current_zone=self.map.start_hub or "start",
                state=DroneState.WAITING,
                path=[]
            )
            self.map.drones.append(new_drone)

    def parser_map(self, filepath: str) -> Map:
        """
        Principal method that opens the file and calls the
        auxilar methods necessary for each part of the map
        (Zones, Drones, Connections).

        Args:
            filepath (str): path for the file to parse

        Raises:
            ValueError: Invalid data for the drones nbrs

            MapErrror: Error for invalid Network.

            (FileExistsError, FileNotFoundError): Erros when opening
                and reading the files.

        Returns:
            map (Map): Network instance whith all the data necessary
        """
        try:
            with open(filepath) as file:
                for self.line_nbr, line in enumerate(file, start=1):
                    line = line.strip()
                    if line.startswith("#") or not line:
                        continue
                    if line.startswith('nb_drones'):
                        self.map.nbr_drones = self._parse_nbr_drones(line)
                    is_hub = re.match(r"^(start_hub|end_hub|hub):", line)
                    if is_hub:
                        zone = self._parser_hubs(line)
                        self.map.add_zone(zone)
                    if line.startswith("connection:"):
                        self._parse_connections(line)
            # Checking the all map !!
            self._check_map_complete()
            self._initialize_drones()
        except ValueError as e:
            print(f"{Coolors.RED} Error on {self.line_nbr} invalid value: {e}",
                  file=sys.stderr)
            sys.exit(1)
        except MapError as e:
            print(f"{Coolors.RED} Error: {e}")
            sys.exit(1)
        except (FileExistsError, FileNotFoundError) as e:
            print(f"{Coolors.RED} Error: {e}")
            sys.exit(1)
        return self.map
