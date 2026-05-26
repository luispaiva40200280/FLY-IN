from typing import Optional
import sys
import arcade as arc
from models.data import Zone
from models.network import Map
from models.parser_map import ParserMap


class NetworkView(arc.View):
    """
    """
    def __init__(self, network: Map) -> None:
        super().__init__()
        self.map = network
        self.SCALE = 100
        self.OFFSET_X = 100
        self.OFFSET_Y = 300
        # Set the background color (requires arc.color or raw RGBA)
        arc.set_background_color(arc.color.EERIE_BLACK)

    def _get_screen_coords(self, grid_x: int, grid_y: int) -> tuple[int, int]:
        screen_x = (grid_x * self.SCALE) + self.OFFSET_X
        screen_y = (grid_y * self.SCALE) + self.OFFSET_Y
        return screen_x, screen_y

    def _draw_zones(self, zone: Optional[Zone]) -> None:
        if not zone:
            return
        # 1. Translate grid coordinates to pixel coordinates
        screen_x, screen_y = self._get_screen_coords(zone.x, zone.y)
        # 2. Draw a physical circle for the zone
        # (We will eventually map this to your Coolors enum)
        arc.draw_circle_filled(screen_x, screen_y, radius=20,
                               color=arc.color.AFRICAN_VIOLET)
        # 3. Draw the text offset ABOVE the circle and centered
        arc.draw_text(text=f"{zone.name}", x=screen_x, y=screen_y,
                      font_size=10, anchor_x="center", anchor_y="top")

    def on_draw(self) -> None:
        """Render the screen. Called roughly 60 times per second."""
        # 1. Clear the screen (Mandatory first step)
        self.clear()
        for zone in self.map.zones.values():
            self._draw_zones(zone)

        for f_set in self.map.connections.keys():
            # Unpack the frozenset
            name_a, name_b = f_set
            zone_a = self.map.zones.get(name_a)
            zone_b = self.map.zones.get(name_b)

            if not zone_a or not zone_b:
                continue

            # Calculate coordinates
            start_x, start_y = self._get_screen_coords(zone_a.x, zone_a.y)
            end_x, end_y = self._get_screen_coords(zone_b.x, zone_b.y)

            # Draw the edge
            arc.draw_line(start_x, start_y, end_x, end_y, arc.color.BLUE,
                          line_width=2)


if __name__ == "__main__":
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 600
    SCREEN_TITLE = "Graph Rendering Test"
    file = sys.argv[1]

    map_network = ParserMap().parser_map(filepath=file)
    window = arc.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    # Instantiate the test view
    test_view = NetworkView(network=map_network)

    # Tell the window to display this specific view
    window.show_view(test_view)

    # Start the 60FPS event loop
    arc.run()
