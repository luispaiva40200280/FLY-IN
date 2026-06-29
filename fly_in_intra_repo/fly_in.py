"""
Main execution script for the Fly-in drone routing simulation.

This script acts as the primary controller for the application.
It orchestrates the three core phases of the simulation pipeline:
    1. Parsing the static map topology from a provided text file.
    2. Calculating the optimal multi-agent pathfinding schedule using the
    Navigator.
    3. Executing the physical simulation turn-by-turn via the
    State Engine to validate physical constraints and output the results.
"""
from src.models.network import Map
from src.models.parser_map import ParserMap
from src.pathfinder.state_engine import StateEngine, SimulationError
from src.pathfinder.pathfinding import Navigator
from src.view.terminal_view import TerminalView
import sys


def main() -> None:
    """
    Entry point for the simulation controller.

    Reads the map filepath from the command-line arguments, initializes the
    network model, generates the master timeline for all drones,
    and iteratively steps through time to execute and validate the physics
    of the swarm.

    Command-Line Arguments:
        sys.argv[1] (str): The filepath to the map text file
            (e.g., 'maps/hard/01_maze_nightmare.txt').

    Outputs:
        Prints the parsing status, raw calculated timelines (for debugging),
        and turn-by-turn simulation actions to the standard output.

    Exceptions Handled:
        Exception: Catches and logs unexpected failures during the pathfinding
            phase.
        SimulationError: Catches fatal physics violations
            (e.g., capacity overflows) raised by the State Engine and
            terminates the simulation gracefully.
    """
    if len(sys.argv) == 1:
        print("Usage <python3> fly_in.py <<file_map_path>>")

    statics = False
    if "--statics" in sys.argv:
        statics = True
    try:
        file_path = sys.argv[1]
        network: Map = ParserMap().parser_map(file_path)
        schedule = Navigator(network).solve()
        engine = StateEngine(network)
        terminal = TerminalView(network)

        max_turns = max(len(timeline) for timeline in schedule.values())
        for turn in range(1, max_turns):
            moves = {}
            for drone_name, timeline in schedule.items():
                if turn < len(timeline):
                    target = timeline[turn]
                else:
                    target = timeline[-1]
                moves[drone_name] = target
            valid = engine.execute_turn(moves)
            if valid:
                print(f"=== Turn number: {engine.turn_counter} ===")
                terminal._render(valid, statics)
                print()
    except SimulationError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
