from enum import Enum
from typing import Optional


class ZoneType(Enum):
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'


class DroneState(Enum):
    WAITING = 'waiting'
    IN_TRANSIT = 'in_transit'
    ARRIVED = 'arrived'


# ToDo constans to transform colors in anscii codes
class Coolors(Enum):
    """
    Enum class to hold all the anscii colors for
    the zones
    """
    # --- Reset Code (Mandatory after every colored string) ---
    RESET = '\033[0m'

    # --- Standard Map Colors ---
    GREEN = '\033[38;5;46m'       # Bright Green
    BLUE = '\033[38;5;39m'        # Bright Blue
    YELLOW = '\033[38;5;226m'     # Standard Yellow
    ORANGE = '\033[38;5;214m'     # Bright Orange
    RED = '\033[38;5;196m'        # Bright Red
    PURPLE = '\033[38;5;93m'      # Deep Purple
    CYAN = '\033[38;5;51m'        # Cyan/Aqua

    # --- Exotic "Hard/Challenger" Map Colors ---
    BLACK = '\033[38;5;240m'      # Dark Grey
    BROWN = '\033[38;5;130m'      # Standard Brown
    MAROON = '\033[38;5;52m'      # Very Dark Red/Brown
    DARKRED = '\033[38;5;88m'     # Deep Red
    GOLD = '\033[38;5;220m'       # Yellow-Gold
    LIME = '\033[38;5;118m'       # Bright Yellow-Green
    MAGENTA = '\033[38;5;201m'    # Bright Pink/Magenta
    VIOLET = '\033[38;5;128m'     # Light Purple
    CRIMSON = '\033[38;5;197m'    # Deep Pinkish-Red
    RAINBOW = '\033[38;5;51m'

    @classmethod
    def get_color(cls, color_name: Optional[str]) -> str:
        """
        Safely retrieves the ANSI string for a specific color.
        Returns the RESET code if the color is missing or undefined.
        """
        # 1. Handle cases where the zone has no color defined (None)
        if not color_name:
            return cls.RESET.value

        try:
            # 2. Look up the Enum member by its exact uppercase string name
            return cls[color_name.upper()].value
        except KeyError:
            # 3. Gracefully fallback to RESET if an unknown color is passed,
            # preventing unhandled exception crashes.
            return cls.RESET.value
