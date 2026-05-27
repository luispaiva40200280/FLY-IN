from models.data import Zone  # , Connection, Drone
from models.network import Map


class StateEngine:
    def __init__(self, map: Map) -> None:
        self.map = map
        self.drones = self.map.nbr_drones
        self.future_reservations: dict[Zone, int] = {}
        self.turn_counter = 0
