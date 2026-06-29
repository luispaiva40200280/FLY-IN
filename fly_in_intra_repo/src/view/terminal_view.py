from ..models.network import Map, Drone
from ..models.constants import Coolors, DroneState
from ..models.parser_map import MapError


class TerminalView():
    def __init__(self, network: Map) -> None:
        """
        Inicialize the terminal viewer so it can fetch the informacion of
        the map that it showing the solution.

        Args:
            network (map): holds the information of the map including
                (Zones, Connections, Drones)
        """
        self.map = network

    def _statistics(self) -> None:
        """
        Prints a simple staticts for each turn in the terminal about the
        start and end zone and there accupance.
        """
        start = 0
        for drone in self.map.drones:
            if "start" in drone.current_zone:
                start += 1
        print(f"== {start}/{self.map.nbr_drones} are in the final zone ==")

        goal = 0
        for drone in self.map.drones:
            if "goal" in drone.current_zone:
                goal += 1
        print(f"== {goal}/{self.map.nbr_drones} are in the final zone ==")

    def _render(self,
                moves: list[tuple[Drone, str, DroneState]],
                statics: bool) -> None:
        """
        It renders the output in the terminal of the moves made by the drones
        in each turn.
        It uses the enum Coolors Class for each zone, connction that the drone
        passes to renser the text.

        Args:
            moves (list): A list of the moves for each drone in each turn
                (Drone, Destanation, Drone State)

            statics (bool): a bool variable to control the statics view in
                each turn (nbr of drones on the last and the start zone)
        """
        output: list[str] = []
        reset = Coolors.RESET
        for move in moves:
            drone, target, state = move
            curr_zone = self.map.zones.get(drone.current_zone)
            if not curr_zone:
                raise MapError(f"{drone.current_zone} not in the map")
            curr_color = curr_zone.color.value
            target_zone = self.map.zones.get(target)
            if not target_zone:
                raise MapError(f"{target} not in the map")
            target_color = target_zone.color.value
            if state == DroneState.IN_TRANSIT:
                turn = f"{drone.name}-{curr_color}{drone.current_zone}\
{reset.value}-{target_color}{target}{reset.value}"
            if state == DroneState.ARRIVED:
                turn = f"{drone.name}-{target_color}{target_zone.name}\
{reset.value}"
            output.append(turn)
        if output:
            print("\n".join(output))
        if statics:
            self._statistics()
