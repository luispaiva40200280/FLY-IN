"""
State engine needs clean up and code division
and docstrings explaining what each part does
"""
from ..models.network import Map, Drone
from ..models.constants import DroneState, ZoneType


class SimulationError(Exception):
    """
    Unique errror
    """
    pass


class StateEngine:
    def __init__(self, map: Map) -> None:
        """
        Initialize the state engine with the map.

        Args:
            map (Map): Graph built from the Zones, Connectionsand and Drones.

        Attributes:
            map (Map): The static layout of the environment and drone entities.

            future_reservations (dict): A 3D space-time ledger mapping
                (zone_name, turn_number) to the number of drones scheduled to
                occupy that airspace.Used to enforce capacity limits during
                multi-turn transits.

            turn_counter (int): The global clock tracking the current
                simulation turn.

        """
        self.map = map
        self.future_reservations: dict[tuple[str, int], int] = {}
        self.turn_counter: int = 0

    def _free_nodes_capacity(self, nodes_occupency: dict[str, int],
                             moves: dict[str, str]) -> None:
        """
        Method to free the capacity of a Zone.

        Checks if a drone is leaving a zone and decrements and updates
        the dictionary that traks the capacaty of the zones in each turn.

        Args:
            nodes_occupency (dict): A tracker for the nodes and there
                occupency on each turn

            moves (dict): Propesed move between two connected zones
        """
        for drone in self.map.drones:
            if drone.state == DroneState.IN_TRANSIT:
                continue
            target = moves.get(drone.name, drone.current_zone)
            if target != drone.current_zone:
                nodes_occupency[drone.current_zone] -= 1

    def _validate_moves(self, nodes_occupency: dict[str, int], moves:
                        dict[str, str]) -> list[tuple[Drone, str, DroneState]]:
        current_connection_usage: dict[frozenset[str], int] = {
            f_set: 0 for f_set in self.map.connections.keys()
        }
        """
        Validates moves between zones. Having in consideration the zones
        max number of drones in simultanius its type and waiting time and the
        max drones on the connection between those two zones.

        Args:
            nodes_occupency (dict): A tracker for the nodes and there
                occupency on each turn

            moves (dict): Propesed move between two connected zones

        Returns:
            list[Tuple[Drone, str, DroneState]]: A valid list of all the moves
                necessary for each drone to solve the map.
                (Drone, Destanaticion, Drone State)
        """
        valid_moves: list[tuple[Drone, str, DroneState]] = []
        for drone in self.map.drones:
            if drone.destination and drone.state == DroneState.IN_TRANSIT:
                drone.transit_timer -= 1
                if drone.transit_timer == 0:
                    nodes_occupency[drone.destination] += 1
                    valid_moves.append((drone, drone.destination,
                                        DroneState.ARRIVED))
                continue
            target = moves.get(drone.name, drone.current_zone)
            if target == drone.current_zone:
                continue
            fro_zet = frozenset([drone.current_zone, target])
            connection = self.map.connections.get(fro_zet)
            if connection:
                max_link = connection.max_link_capacity
                current_connection = current_connection_usage[fro_zet]
                if current_connection + 1 > max_link:
                    raise SimulationError(f"Capacity exceeded between \
{connection.zones}")
                current_connection_usage[fro_zet] += 1
            else:
                raise SimulationError(f"Error on the connection between \
{fro_zet}")

            zone_to_go = self.map.zones.get(target)
            if not zone_to_go:
                raise SimulationError(f"{target} is not in the map")
            if zone_to_go.zone == ZoneType.RESTRICTED:
                turn = self.turn_counter + 1
                future_count = self.future_reservations.get((target, turn), 0)
                if future_count + 1 > zone_to_go.max_drones:
                    raise SimulationError(f"Colicion on {zone_to_go.name} \
at turn {turn}")
                self.future_reservations[target, turn] = future_count + 1
                valid_moves.append((drone, target, DroneState.IN_TRANSIT))
            else:
                if nodes_occupency[target] + 1 > zone_to_go.max_drones:
                    raise SimulationError(f"Capacity Overflow: {target}")
                nodes_occupency[target] += 1
                valid_moves.append((drone, target, DroneState.ARRIVED))
        return valid_moves

    def _commit_move(self,
                     valid_moves: list[tuple[Drone, str, DroneState]]) -> None:
        """
        Permanently applies validated physical movements to the drone entities.

        Acts as the final execution phase of the simulation turn. It iterates
        through the list of pre-validated actions and mutates the internal
        attributes (state, location, and transit timers) of each drone to
        reflect physical reality.

        Args:
            valid_moves (list[tuple[Drone, str, DroneState]]): A list of tuples
                where each tuple contains:
                - Drone: The physical drone object to be mutated.
                - str: The string identifier of the target destination zone.
                - DroneState: The new state to apply (IN_TRANSIT or ARRIVED).
        """
        for move in valid_moves:
            drone, target, state = move
            if state == DroneState.IN_TRANSIT:
                drone.state = DroneState.IN_TRANSIT
                drone.destination = target
                drone.transit_timer = 1
            if state == DroneState.ARRIVED:
                drone.state = DroneState.ARRIVED
                drone.current_zone = target
                drone.transit_timer = 0
                drone.destination = None

    def execute_turn(self, moves: dict[str, str]) -> list[tuple[Drone, str,
                                                                DroneState]]:
        """
        Executes a single chronological tick of the simulation physics.

        Acts as the primary orchestrator for the State Engine. It resolves a
        turn by executing a strict three-phase pipeline:
        1. Compiles the baseline occupancy of all zones.
        2. Frees capacity for drones initiating a departure.
        3. Validates incoming moves against 3D space-time capacity constraints
           and permanently commits them to the drone entities.

        Args:
            moves (dict[str, str]): A dictionary mapping a drone's string
            identifier to its intended target zone for this microsecond
            (e.g., {"D1": "loop_a"}). If a drone is holding position,
            the target must equal its current_zone.

        Returns:
            list[tuple[Drone, str, DroneState]]: A ledger of all successfully
            validated and committed actions for this turn.
            Each tuple provides the mutated Drone object,
            its target zone string, and its new DroneState. This payload is
            formatted specifically for downstream consumption by the
            visualizer.

        Raises:
            SimulationError: If any proposed move in the `moves` dictionary
            violates the physical constraints of the map
            (e.g., node capacity overflow, edge capacity overflow,
            or multi-drone collisions in restricted airspace).
        """
        self.turn_counter += 1
        nodes_occupency: dict[str, int] = {zone.name: 0
                                           for zone in self.map.zones.values()}
        for drone in self.map.drones:
            if drone.state in (DroneState.ARRIVED, DroneState.WAITING):
                nodes_occupency[drone.current_zone] += 1
        self._free_nodes_capacity(nodes_occupency, moves)
        validated = self._validate_moves(nodes_occupency, moves)
        self._commit_move(validated)
        return validated
