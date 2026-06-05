from models.network import Map
from models.constants import DroneState, ZoneType
from models.parser_map import ParserMap
import sys
"""
State engine needs clean up and code division
and docstrings explaining what each part does
"""


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

    def execute_turn(self, moves: dict[str, str]) -> None:
        """
        proposed_moves:
        A dictionary mapping {Drone: TargetZone} for this turn.
        If a drone is waiting, TargetZone == drone.current_zone.
        """
        from collections import deque
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

        # =========================================================
        # PHASE 2: THE VALIDATION (Enforcing Physics)
        # =========================================================
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
            # validate the moves of each drone deppending on the max link
            # of each connection
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
                self.future_reservations[target, turn] = future_count
                valid_moves.append((drone, target, DroneState.IN_TRANSIT))
            else:
                # ---> THE MISSING SCENARIO E <---
                # 1. Verify immediate capacity for Normal/Priority zones
                if nodes_occupency[target] + 1 > zone_to_go.max_drones:
                    raise SimulationError(f"Capacity Overflow: {target}")
                # 2. Lock in the immediate reservation!
                nodes_occupency[target] += 1
                # 3. YOU MUST APPEND THE MOVE so Phase 3 can execute it
                valid_moves.append((drone, target, DroneState.ARRIVED))

        # =========================================================
        # PHASE 3: THE COMMIT (State Update & Output formatting)
        # =========================================================

        for drone, destination, state in valid_moves:
            if state == DroneState.ARRIVED:
                drone.current_zone = destination
                drone.destination = None
                drone.transit_timer = 0
                drone.state = DroneState.ARRIVED
                turn_output.append(f"{drone.name}-{destination}")

            if state == DroneState.IN_TRANSIT:
                drone.transit_timer = 1
                drone.state = DroneState.IN_TRANSIT
                drone.current_zone = None
                drone.destination = destination
                turn_output.append(f"{drone.name}-{destination}")

        if turn_output:
            print("\n".join(turn_output))


def run_simulation_test() -> None:
    print(">>> INITIALIZING MAP <<<")
    if len(sys.argv) < 2:
        print("no file provided")
        return
    try:
        file_map = sys.argv[1]
        parser = ParserMap()

        network = parser.parser_map(filepath=file_map)

        # 2. Boot the engine (which should now automatically spawn the drones)
        engine = StateEngine(network)
        print(">>> TURN 1: Staggering Departures <<<")
        turn_1_moves = {
            "D1": "waypoint1"
            # D2 omitted. Engine fallback sets target to 'start'
        }
        engine.execute_turn(turn_1_moves)

        print("\n>>> TURN 2: Simultaneous Shift <<<")
        turn_2_moves = {
            "D1": "waypoint2",
            "D2": "waypoint1"
        }
        engine.execute_turn(turn_2_moves)

        print("\n>>> TURN 3: First Arrival <<<")
        turn_3_moves = {
            "D1": "goal",
            "D2": "waypoint2"
        }
        engine.execute_turn(turn_3_moves)

        print("\n>>> TURN 4: Final Arrival <<<")
        turn_4_moves = {
            "D1": "goal",  # Explicitly commanding the wait
            "D2": "goal"
        }
        engine.execute_turn(turn_4_moves)

        print("\n>>> FINAL STATE VERIFICATION <<<")
        for drone in engine.map.drones:
            print(f"{drone.name} is {drone.state.name} \
at {drone.current_zone}")
    except SimulationError as e:
        print(e)


if __name__ == "__main__":
    run_simulation_test()
