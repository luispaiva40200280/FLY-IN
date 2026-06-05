from models.parser_map import MapError
from models.network import Map
from models.data import Drone
from models.constants import ZoneType
# from .state_engine import StateEngine
from collections import deque
import heapq


class AlgError(Exception):
    """
    Custom error for pathfinding algorithm
    """
    pass


class Navigator:
    def __init__(self, network: Map) -> None:
        self.map = network
        # The Pathfinder's version of the engine's physics board
        # Key: (Zone Name, Turn Integer) -> Value: Drones occupying it
        self.reservations: dict[tuple[str, int], int] = {}

        # The final output: { "D1": ["start", "waypoint1", "goal", "goal"] }
        self.master_schedule: dict[str, list[str]] = {}

    """
    def solve(self) -> dict[str, list[str]]:
        The main orchestration method.
        Executes Phase 1, Phase 2, and Phase 3 sequentially.
        # 1. Get sorted list of drones
        priority_queue: deque = self._calculate_priorities()
        # 2. Route them one by one
        for drone in priority_queue:
            path = self._space_time_a_star(drone)
            if not path:
                raise ValueError(f"Deadlock: No valid path for {drone.name}")
            # 3. Lock it in
            self._register_path(drone, path)

        return self.master_schedule
    """
    def _reconstruct_path(self, came_from: dict[tuple[str,  int],
                                                tuple[str, int]],
                          goal: tuple[str, int]):
        pass

    def _space_time_a_star(self, drone: Drone):  # -> list[tuple[str, int]]:
        open_set: list[tuple[int, int, str]] = [(0, 0, drone.current_zone)]
        came_from: dict[tuple[str,  int], tuple[str, int]] = {}
        score: dict[tuple[str, int], int] = {(drone.current_zone, 0): 0}
        while open_set:
            _, current_time, current_zone = heapq.heappop(open_set)
            if current_zone == self.map.end_hub:
                return self._reconstruct_path(came_from, (current_zone,
                                                          current_time))

            neighbors = (self.map.list_adjacents.get(current_zone, []) +
                         [current_zone])

            for zone_name in neighbors:
                zone_to_go = self.map.zones.get(zone_name)
                if not zone_to_go:
                    raise MapError(f"{zone_name} does not exsit in  the map")
                # IMPLEMENT: Calculate arrival_time (+1 or +2)
                if zone_to_go.zone == ZoneType.BLOCKED:
                    continue
                elif zone_name == current_zone:
                    arrival_time = current_time + 1
                elif zone_to_go.zone in (ZoneType.NORMAL, ZoneType.PRIORITY):
                    arrival_time = current_time + 1
                else:
                    arrival_time = current_time + 2

                # IMPLEMENT: Check self.global_reservations for Node Capacity
                nbr_drones = self.reservations.get((zone_name, arrival_time),
                                                   0)
                fnbr_drones = self.reservations.get((zone_name, arrival_time),
                                                    0)
                if (nbr_drones > zone_to_go.max_drones or
                        fnbr_drones > zone_to_go.max_drones):
                    continue
                # IMPLEMENT: Check self.global_reservations for Edge Swaps
                # IMPLEMENT: Calculate f_score using _get_ideal_cost
                # IMPLEMENT: Update came_from, g_score, and push to open_set
                pass
        # Return empty list if deadlock is mathematically unavoidable
        pass

    def _calculate_priorities(self) -> deque[Drone]:
        """Phase 1: Returns a sorted list of drones based on Ideal Cost."""
        sorted_drones: list[tuple[int, Drone]] = []
        if not self.map.end_hub:
            raise MapError("The map those not have a end zone")
        for drone in self.map.drones:
            cost = self._get_ideal_cost(drone, self.map.end_hub)
            if cost == -1:
                raise MapError(f"Impssible to solve the map for {drone.name}")
            sorted_drones.append((cost, drone))
        sorted_drones.sort(key=lambda d: (-d[0], d[1].name))
        queue: deque[Drone] = deque(item[1] for item in sorted_drones)
        return queue

    def _get_ideal_cost(self, drone: Drone, end_zone: str) -> int:
        priority_queue: list = [(0, drone.current_zone)]
        visited: set[str] = set()
        while priority_queue:
            time_cost, zone_name = heapq.heappop(priority_queue)
            if zone_name in visited:
                continue
            visited.add(zone_name)
            if zone_name == end_zone:
                return time_cost
            neighbors_zones = self.map.list_adjacents.get(zone_name, [])
            for neighbor in neighbors_zones:
                node = self.map.zones.get(neighbor)
                if not node:
                    raise ValueError("zone does not exist")
                if node.zone == ZoneType.BLOCKED:
                    continue
                if node.zone == ZoneType.RESTRICTED:
                    new_cost = time_cost + 2
                else:
                    new_cost = time_cost + 1
                heapq.heappush(priority_queue, (new_cost, node.name))
        return (-1)
