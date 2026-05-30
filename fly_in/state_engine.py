from models.data import Zone  # , Connection, Drone
from models.network import Map
from models.constants import DroneState


class StateEngine:
    def __init__(self, map: Map) -> None:
        self.map = map
        self.future_reservations: dict[Zone, tuple[str, int]] = {}
        self.turn_counter: int = 0

    def execute_turn(self, moves: dict[str, Zone]) -> None:
        """
        proposed_moves:
        A dictionary mapping {Drone: TargetZone} for this turn.
        If a drone is waiting, TargetZone == drone.current_zone.
        """
        from collections import deque
        self.turn_counter += 1
        # this is for checking the state of the map in every turn
        # and see the zones that have and how may drones are in there
        nodes_occupency: dict[str, int] = {zone.name: 0 for zone in self.map.zones.values()}
        for drone in self.map.drones:
            if drone.state in (DroneState.ARRIVED, DroneState.WAITING):
                nodes_occupency[drone.current_zone] += 1

        # 2. Initialize CONNECTION buffer (stateless, guaranteed empty at
        # start of turn) Using the frozenset as the key matches your
        # network.py architecture
        current_connection_usage: dict[frozenset[str], int] = {
            f_set: 0 for f_set in self.map.connections.keys()
        }
        # =========================================================
        # PHASE 1: THE DEPARTURE (Freeing Capacity)
        # =========================================================
        for drone in self.map.drones:
            if drone.state == DroneState.IN_TRANSIT:
                continue
            target = moves.get(drone.name, drone.current_zone)
            if target != drone.current_zone:
                nodes_occupency[drone.current_zone] -= 1

        valid_moves: list = []
        turn_output: deque = deque()

        for drone in self.map.drones:
            pass
