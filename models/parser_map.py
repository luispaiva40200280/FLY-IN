# import re
from typing import List
from network import Map
from data import Connection
import os


class ParserMap:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.current_line_number = 1
        self.map: Map = Map()

    @staticmethod
    def _parse_nbr_drones(line: str) -> int:
        nbr_drones = line.split(':', 1)
        nbr = int(nbr_drones[1])
        return nbr

    @staticmethod
    def _parser_hubs() -> dict[frozenset[str], Connection]:
        connections: dict[frozenset[str], Connection] = {}
        return connections

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
        with open(self.filepath) as file:
            for line in file:
                if line.startswith("#"):
                    continue

        return self.map
