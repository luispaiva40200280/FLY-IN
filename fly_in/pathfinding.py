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
        self.edge_reservations: dict[tuple[frozenset[str], int], int] = {}
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
        """
        Traces the came_from dictionary backward from the goal to the start.
        Handles the 2-turn gap created by RESTRICTED zones.
        """
        # 1. Initialize the tracker and the output list
        current_state = goal
        path_timeline: list[str] = []

        # 2. The Natural Break Condition
        # The start node at Turn 0 is NEVER recorded as a key in came_from.
        # When current_state reaches ("start", 0), this loop automatically terminates.
        while current_state in came_from:
            # Look one step backward in time
            prev_state = came_from[current_state]
            
            # Extract the data
            current_zone = current_state[0]
            current_time = current_state[1]
            prev_time = prev_state[1]

            # 3. Log the current step
            path_timeline.append(current_zone)

            # 4. The Physics Gap Catch
            # If the time difference is 2, it was a restricted zone.
            # We must duplicate the zone name to fill the chronological turn.
            if current_time - prev_time == 2:
                path_timeline.append(current_zone)

            # 5. Step backwards
            current_state = prev_state

        # 6. Finalize the Timeline
        # The loop broke before adding the Turn 0 starting zone, so we add it 
        # manually.
        start_zone = current_state[0]
        path_timeline.append(start_zone)
        
        # The list is currently [Goal, Waypoint, Start]. Reverse it.
        path_timeline.reverse()
        
        return path_timeline

    def _space_time_a_star(self, drone: Drone):  # -> list[tuple[str, int]]:
        if not self.map.end_hub:
            raise AlgError("No end hub on the map")
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

            for z_name in neighbors:
                zone_to_go = self.map.zones.get(z_name)
                if not zone_to_go:
                    raise MapError(f"{z_name} does not exsit in  the map")
                # IMPLEMENT: Calculate arrival_time (+1 or +2)
                if zone_to_go.zone == ZoneType.BLOCKED:
                    continue
                elif z_name == current_zone:
                    arrival_time = current_time + 1
                elif zone_to_go.zone in (ZoneType.NORMAL, ZoneType.PRIORITY):
                    arrival_time = current_time + 1
                else:
                    arrival_time = current_time + 2

                # IMPLEMENT: Check self.global_reservations for Node Capacity
                nbr_drones = self.reservations.get((z_name, arrival_time),
                                                   0)
                fnbr_drones = self.reservations.get((z_name, current_time + 1),
                                                    0)
                if (nbr_drones >= zone_to_go.max_drones or
                        fnbr_drones >= zone_to_go.max_drones):
                    continue
                # IMPLEMENT: Check self.global_reservations for Edge Swaps
                if current_zone != z_name:
                    edge = frozenset([current_zone, z_name])
                    conn_to_use = self.map.connections.get(edge)
                    if not conn_to_use:
                        raise AlgError(f"Not {z_name}-{drone.current_zone}")
                    edge_nbr = self.edge_reservations.get((edge, current_time
                                                           + 1), 0)
                    if edge_nbr >= conn_to_use.max_link_capacity:
                        continue
                # IMPLEMENT: Calculate f_score using _get_ideal_cost
                hcost = self._get_ideal_cost(z_name, self.map.end_hub)
                if hcost == -1:
                    continue
                f_scocre = arrival_time + hcost
                state_key = (z_name, arrival_time)
                if state_key in score and score[state_key] <= arrival_time:
                    continue
                score[state_key] = arrival_time
                # IMPLEMENT: Update came_from, g_score, and push to open_set
                came_from[state_key] = (current_zone, current_time)
                heapq.heappush(open_set, (f_scocre, arrival_time, z_name))
        return []

    def _calculate_priorities(self) -> deque[Drone]:
        """Phase 1: Returns a sorted list of drones based on Ideal Cost."""
        sorted_drones: list[tuple[int, Drone]] = []
        if not self.map.end_hub:
            raise MapError("The map those not have a end zone")
        for drone in self.map.drones:
            cost = self._get_ideal_cost(drone.current_zone, self.map.end_hub)
            if cost == -1:
                raise MapError(f"Impssible to solve the map for {drone.name}")
            sorted_drones.append((cost, drone))
        sorted_drones.sort(key=lambda d: (-d[0], d[1].name))
        queue: deque[Drone] = deque(item[1] for item in sorted_drones)
        return queue

    def _get_ideal_cost(self, current_zone: str, end_zone: str) -> int:
        priority_queue: list = [(0, current_zone)]
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
