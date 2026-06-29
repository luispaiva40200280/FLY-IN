"""
State engine needs clean up and code division
and docstrings explaining what each part does
"""
from models.network import Map
from models.constants import DroneState, ZoneType
from models.data import Drone


class SimulationError(Exception):
    """
    Unique errror
    """
    pass


class StateEngine:
    def __init__(self, map: Map) -> None:
        self.map = map
        self.future_reservations: dict[tuple[str, int], int] = {}
        self.turn_counter: int = 0

    # =========================================================
    # PHASE 1: THE DEPARTURE (Freeing Capacity)
    # ========================================================
    def _free_nodes_capacity(self, nodes_occupency: dict[str, int],
                             moves: dict[str, str]) -> None:
        for drone in self.map.drones:
            if drone.state == DroneState.IN_TRANSIT:
                continue
            target = moves.get(drone.name, drone.current_zone)
            if target != drone.current_zone:
                nodes_occupency[drone.current_zone] -= 1

    # =========================================================
    # PHASE 2: THE VALIDATION (Enforcing Physics)
    # =========================================================
    def _validate_moves(self, nodes_occupency: dict[str, int], moves:
                        dict[str, str]) -> list[tuple[Drone, str, DroneState]]:
        current_connection_usage: dict[frozenset[str], int] = {
            f_set: 0 for f_set in self.map.connections.keys()
        }
        """
        """
        valid_moves: list = []
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

    def execute_turn(self, moves: dict[str, str]) -> None:
        """
        proposed_moves:
        A dictionary mapping {Drone: TargetZone} for this turn.
        If a drone is waiting, TargetZone == drone.current_zone.
        """
        self.turn_counter += 1
        # this is for checking the state of the map in every turn
        # and see the zones that have and how may drones are in there
        nodes_occupency: dict[str, int] = {zone.name: 0
                                           for zone in self.map.zones.values()}
        for drone in self.map.drones:
            if drone.state in (DroneState.ARRIVED, DroneState.WAITING):
                nodes_occupency[drone.current_zone] += 1

        # 2. Initialize CONNECTION buffer (stateless, guaranteed empty at
        # start of turn) Using the frozenset as the key matches your
        # network.py architecture
        self._free_nodes_capacity(nodes_occupency, moves)
        try:
            valid_moves: list = self._validate_moves(nodes_occupency, moves)
            if valid_moves:
                self.turn_output(valid_moves)
        except SimulationError as e:
            print(f"Error: {e}")

    # =========================================================
    # PHASE 3: THE COMMIT (State Update & Output formatting)
    # =========================================================
    def turn_output(self, valid_moves: list) -> None:
        from collections import deque
        turn_output: deque = deque()
        for drone, destination, state in valid_moves:
            if state == DroneState.ARRIVED:
                turn_output.append(f"{drone.name}: {drone.current_zone}\
-{destination}")
                drone.current_zone = destination
                drone.destination = None
                drone.transit_timer = 0
                drone.state = DroneState.ARRIVED

            if state == DroneState.IN_TRANSIT:
                turn_output.append(f"{drone.name}: {drone.current_zone}\
-{destination}")
                drone.transit_timer = 1
                drone.state = DroneState.IN_TRANSIT
                drone.current_zone = None
                drone.destination = destination

        if turn_output:
            print("\n".join(turn_output))
