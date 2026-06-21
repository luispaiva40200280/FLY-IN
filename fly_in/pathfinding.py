from models.parser_map import MapError
from models.network import Map
from models.data import Drone
from models.constants import ZoneType
from collections import deque
import heapq


class AlgError(Exception):
    """
    Custom error for pathfinding algorithm
    """
    pass


class Navigator:
    def __init__(self, network: Map) -> None:
        """
        Initializes the pathfinding engine with the static map topology
        and the dynamic chronological collision calendars.

        Args:
            network (Map): The parsed graph containing all zones,
                connections, and drones.

        Attributes:
            map (Map): Stores the static topological data of the
                network to be navigated.

            zone_reservations (dict[tuple[str, int], int]):
                The 3D Node Capacity Calendar.
                Key: A tuple of (Zone Name, Chronological Turn).
                Value: The integer count of drones scheduled to occupy
                    that zone at that turn.

            edge_reservations (dict[tuple[frozenset[str], int], int]):
                The 3D Edge Capacity Calendar.
                Key: A tuple containing a frozenset of two connecting zones,
                    and the Chronological Turn the transition initiates.
                Value: The integer count of drones actively crossing that
                    specific edge.

            master_schedule (dict[str, list[str]]):
                The final output ledger.
                Key: The drone's string identifier (e.g., "D1").
                Value: The chronological, turn-by-turn list of zones the
                    drone will traverse.
        """
        self.map = network
        self.zone_reservations: dict[tuple[str, int], int] = {}
        self.edge_reservations: dict[tuple[frozenset[str], int], int] = {}
        self.master_schedule: dict[str, list[str]] = {}

    def solve(self) -> dict[str, list[str]]:
        """
        The main orchestration method.

        Calculates the the prioity for each drone and calls
        the space time star (A* algorithm) for each drone in that order
        and then regiters the path of de drone in the reservations with the
        turn and name of zone that the drone will acupate.
        Returns:
            Dictionary:  "name of the drone": list["hubs/zones names"]
                ex: { "D1": ["start", "waypoint1", "goal", "goal"] }
        """
        priority_queue = self._calculate_priorities()

        for drone in priority_queue:
            drone.path = self._space_time_a_star(drone)
            if not drone.path:
                raise AlgError(f"Deadlock: No valid path for {drone.name}")
            self._register_path(drone, drone.path)
        return self.master_schedule

    def _register_path(self, drone: Drone, path: list[str]) -> None:
        """
        Saves the calculated path and writes the capacity data
        into the collision calendars.

        Iterates chronologically through the drone's timeline.
        Secures the physical node capacity for every individual turn,
        and reserves the edge capacity strictly on the turns where the
        drone initiates a physical transition between two different zones.

        Args:
            drone (Drone): The drone object being routed.

            path (list[str]): The chronological list of
                zone names the drone will occupy.
        """
        self.master_schedule[drone.name] = path
        for turn in range(len(path)):
            curr_node = path[turn]
            nbr_drones_turn = (self.zone_reservations.get((curr_node, turn), 0)
                               + 1)
            # 1. Update Node Capacity Calendar
            self.zone_reservations[(curr_node, turn)] = nbr_drones_turn
            # 2. Update Edge Capacity Calendar (Only if moving)
            if turn > 0:
                prev_zone = path[turn - 1]
                if curr_node != prev_zone:
                    conn = frozenset([prev_zone, curr_node])
                    # The state engine checks connections on the
                    # exact turn the move initiates
                    conn_turn = self.edge_reservations.get((conn, turn), 0) + 1
                    self.edge_reservations[(conn, turn)] = conn_turn

    def _reconstruct_path(self, came_from: dict[tuple[str,  int],
                                                tuple[str, int]],
                          goal: tuple[str, int]) -> list[str]:
        """
        Traces the came_from dictionary backward from the goal to the start.
        Handles the 2-turn gap created by RESTRICTED zones to generate an
        unbroken chronological timeline.

        Args:
            came_from (dict): A mapping of a state to its parent Node/(zone).
                Format: (curr_zone, curr_turn): (prev_zone, prev_turn)

            goal (tuple): The final 3D state reached by the algorithm.
                        Format: (goal_zone, arrival_turn)

        Returns:
            list[str]: A turn-by-turn chronological schedule of the zones the
                    drone will occupy from Turn 0 to the final turn.
        """
        current_state = goal
        path_timeline: list[str] = []
        while current_state[1] > 0:
            prev_state = came_from[current_state]
            current_zone = current_state[0]
            current_time = current_state[1]
            prev_time = prev_state[1]
            path_timeline.append(current_zone)
            if current_time - prev_time == 2:
                path_timeline.append(current_zone)
            current_state = prev_state
        start_zone = current_state[0]
        path_timeline.append(start_zone)
        return path_timeline[::-1]

    def _space_time_a_star(self, drone: Drone) -> list[str]:
        """
        Executes a 3D Space-Time A* search to calculate the optimal,
        collision-free chronological path for a single drone.

        This algorithm extends standard A* by treating time as a
        third physical dimension. It evaluates potential moves against
        the global `reservations` and `edge_reservations` calendars to
        guarantee node capacities and edge-swap rules are respected at every
        discrete turn. It dynamically calculates temporal penalties
        (+1 or +2 turns) based on the Map's ZoneTypes.

        Local Variables:
            open_set (list): A priority min-heap queue storing future states
                    to explore. Sorted by F-score (Total estimated time).
            came_from (dict): A ledger tracking the chronological sequence
                    of states.
                    Maps (Current Zone, Time) -> (Previous Zone, Time).
            score (dict): A strict ledger recording the absolute fastest
                    elapsed time to reach a specific (Zone, Time) state.
                    Prevents infinite loops.

        Args:
            drone (Drone): The specific drone object being routed.
                    Provides the starting location for the search tree.

        Returns:
            list[str]: A turn-by-turn chronological schedule of the zones
                    the drone will occupy. Returns an empty list [] if the
                    drone is trapped in an unavoidable mathematical deadlock.

        Raises:
            AlgError: If the map lacks a defined end_hub,
                or if a required edge vanishes.
            MapError: If the algorithm attempts to evaluate
                a node that does not exist.
        """
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
                if zone_to_go.zone == ZoneType.BLOCKED:
                    continue
                elif z_name == current_zone:
                    arrival_time = current_time + 1
                elif zone_to_go.zone in (ZoneType.NORMAL, ZoneType.PRIORITY):
                    arrival_time = current_time + 1
                else:
                    arrival_time = current_time + 2

                nbr_drones = self.zone_reservations.get((z_name, arrival_time),
                                                        0)
                fnbr_drones = self.zone_reservations.get((current_zone,
                                                          current_time + 1), 0)
                if (nbr_drones >= zone_to_go.max_drones or
                        fnbr_drones >= zone_to_go.max_drones):
                    continue
                if current_zone != z_name:
                    edge = frozenset([current_zone, z_name])
                    conn_to_use = self.map.connections.get(edge)
                    if not conn_to_use:
                        raise AlgError(f"Not {z_name}-{drone.current_zone}")
                    edge_nbr = self.edge_reservations.get((edge, current_time
                                                           + 1), 0)
                    if edge_nbr >= conn_to_use.max_link_capacity:
                        continue
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
        """
        Calculates the ideal routing priority queue for the swarm using a
        longest-path-first heuristic. Executes a reverse Dijkstra search
        (_get_ideal_cost) for every drone to determine its absolute minimum
        traversal time to the end hub.

        The drones are then sorted in descending order based on this cost.
        Drones furthest from the goal are routed first to prevent closer
        drones from creating unavoidable traffic deadlocks.
        Ties are broken alphabetically by the drone's name.

        Returns:
            deque[Drone]: A double-ended queue containing only the Drone
                objects, ordered from highest ideal cost to lowest ideal cost.

        Raises:
            MapError: If the map lacks a defined end_hub, or if a drone
                is mathematically trapped in an isolated section of
                the map (cost == -1).
        """
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
        """
        Calculates the absolute minimum, traffic-free traversal time between
        two zones using a Uniform-Cost Search (simplified Dijkstra's algorithm)

        This method acts as the heuristic engine for the Space-Time
        architecture. It evaluates the map's static terrain (applying +1
        turn for NORMAL/PRIORITY zones and +2 turns for RESTRICTED zones,
        while dodging BLOCKED zones) but entirely ignores dynamic traffic,
        node capacities, and edge reservations.

        Args:
            current_zone (str): The name of the starting node for this search.
                end_zone (str): The name of the target destination node.

        Returns:
            int: The lowest possible chronological turn count required to
                reach the end_zone. Returns -1 if the end_zone is
            mathematically unreachable (e.g., trapped by BLOCKED nodes).

        Raises:
            ValueError: If the algorithm encounters a neighboring zone name
                that does not exist in the map's zone dictionary.
        """
        priority_queue: list = [(0, current_zone)]
        visited: set[str] = set()
        while priority_queue:
            time_cost, zone_name = heapq.heappop(priority_queue)
            if zone_name in visited:
                continue
            visited.add(zone_name)
            if zone_name == end_zone:
                return int(time_cost)
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
