import re
from typing import List
from network import Map
from data import Connection
import sys


class ParserMap:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.current_line_number = 1
        self.map: Map = Map()

    def _parse_nbr_drones(self, line: str) -> None:
        nbr_drones = line.split(':', 1)
        self.map.nbr_drones = int(nbr_drones[1])

    @staticmethod
    def _parser_hubs(line: str) -> None:
        pass

    @staticmethod
    def _parse_connections() -> List[dict[str, Connection]]:
        list_connec: List[dict[str, Connection]] = []
        return list_connec

    def parser_map(self) -> Map:
        """
        1. Open file using 'with open(self.filepath, "r") as f:'
        2. Loop through lines: 'for self.current_line_number,
         line in enumerate(f, 1):'
        3. Strip whitespace and ignore comments
        4. Pass the line to the correct helper method
        """
        try:
            with open(self.filepath) as file:
                for nbr, line in enumerate(file):
                    if line.startswith("#"):
                        continue
                    if line.startswith('nb_drones'):
                        self._parse_nbr_drones(line)
                    is_hub = re.search("hub", line)
                    if is_hub:
                        self._parser_hubs(line)
        except ValueError:
            sys.exit(0)
        return self.map
