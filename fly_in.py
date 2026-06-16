"""
main function that will run the application
"""
# import time
# import os
import sys
from models.parser_map import ParserMap
from fly_in.pathfinding import Navigator
from fly_in.state_engine import StateEngine, SimulationError


def main():
    if len(sys.argv) < 2:
        print("Usage: python fly_in.py <path_to_map.txt>")
        return

    filepath = sys.argv[1]

    # 1. Parse the Map
    print(f">>> PARSING MAP: {filepath} <<<")
    parser = ParserMap()
    network = parser.parser_map(filepath)

    # 2. Calculate the Master Schedule
    print("\n>>> CALCULATING OPTIMAL PATHS (Phase 1 & 2) <<<")
    navigator = Navigator(network)
    try:
        master_schedule = navigator.solve()
    except Exception as e:
        print(f"Pathfinding Failed: {e}")
        return

    # Print out the raw schedule for debugging
    for drone_name, timeline in master_schedule.items():
        print(f"{drone_name}: {timeline}")

    # 3. Execute the Simulation Engine
    print("\n>>> STARTING SIMULATION ENGINE (Phase 3) <<<")
    engine = StateEngine(network)
    # Find out how many turns the longest path takes
    max_turns = max(len(timeline) for timeline in master_schedule.values())
    # ... inside fly_in.py main() after Phase 3 ...

    try:
        # Loop through chronological time steps
        # Start at Turn 1, because index 0 is their starting position
        for turn in range(1, max_turns):
            print(f"\n--- TURN {turn} ---")
            # Build the dictionary mapping {"D1": "waypoint1", "D2": "start"}
            moves_this_turn = {}
            for drone_name, timeline in master_schedule.items():
                # If a drone's timeline is finished, it just waits at the goal
                if turn < len(timeline):
                    target = timeline[turn]
                else:
                    target = timeline[-1]
                moves_this_turn[drone_name] = target
            # Feed the slice of time to the engine
            engine.execute_turn(moves_this_turn)
            #time.sleep(1)
        print(f"TURNS => {turn}/{max_turns}")
    except SimulationError as e:
        print(f"\n[CRASH] The physics engine detected an illegal move: {e}")


if __name__ == "__main__":
    main()

"""
    print("\n>>> LAUNCHING VISUALIZER <<<")
    import arcade as arc
    from view.view_engine import NetworkView

    # Initialize the window
    window = arc.Window(2100, 800, "Fly-In Drone Swarm Simulation")

    # Instantiate the view, passing BOTH the map and the calculated schedule
    animation_view = NetworkView(network=network, schedule=master_schedule)
    window.show_view(animation_view)

    # Start the engine
    arc.run()
"""
