```
root/
├── Makefile                # Mandatory: install, run, debug, clean, lint rules
├── README.md               # Mandatory project documentation
├── requirements.txt        # (Or pyproject.toml) for managing dependencies like mypy, flake8
├── tests/                  # Highly recommended: test edge cases and maps here
│   ├── test_parser.py
│   └── test_pathfinding.py
└── fly_in/                 # Main Python package directory
    ├── __init__.py
    ├── main.py             # The entry point that ties everything together
    │
    ├── parser/             # Strictly for reading and validating input
    │   ├── __init__.py
    │   ├── exceptions.py   # Custom errors (e.g., InvalidZoneTypeError)
    │   └── map_parser.py   # Reads the file, returns raw data dictionaries/lists
    │
    ├── models/             # The core Data Structures (Graph, Nodes, Edges)
    │   ├── __init__.py
    │   ├── zone.py         # Class representing a Hub/Node (holds capacity, color)
    │   ├── connection.py   # Class representing an Edge (holds link capacity)
    │   └── network.py      # Class representing the Graph (holds all zones/connections)
    │
    ├── pathfinding/        # The Algorithms
    │   ├── __init__.py
    │   ├── base.py         # Base/Abstract class for algorithms
    │   └── cbs.py          # E.g., Conflict-Based Search or your chosen algorithm
    │
    ├── engine/             # The Simulation Loop
    │   ├── __init__.py
    │   ├── simulator.py    # Manages turns, validates capacity limits, moves drones
    │   └── state.py        # Tracks where every drone is at a given turn
    │
    └── utils/              # Helper functions
        ├── __init__.py
        └── visualizer.py   # Organizer of colors, ANSI codes, and terminal output
```