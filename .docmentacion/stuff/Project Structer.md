```bash
root/
├── Makefile # Mandatory: install, run, debug, clean, lint rules
├── README.md # Mandatory project documentation
├── requirements.txt # (Or pyproject.toml) for managing dependencies like mypy, flake8
├── tests/ # Highly recommended: test edge cases and maps here
│ ├── test_parser.py
│ └── test_pathfinding.py
└── fly_in/ # Main Python package directory
├── __init__.py
├── main.py # The entry point that ties everything together
│
├── parser/ # Strictly for reading and validating input
│ ├── __init__.py
│ ├── exceptions.py # Custom errors (e.g., InvalidZoneTypeError)
│ └── map_parser.py # Reads the file, returns raw data dictionaries/lists
│
├── models/ # The core Data Structures (Graph, Nodes, Edges)
│ ├── __init__.py
│ ├── zone.py # Class representing a Hub/Node (holds capacity, color)
│ ├── connection.py # Class representing an Edge (holds link capacity)
│ └── network.py # Class representing the Graph (holds all zones/connections)
│
├── pathfinding/ # The Algorithms
│ ├── __init__.py
│ ├── base.py # Base/Abstract class for algorithms
│ └── cbs.py # E.g., Conflict-Based Search or your chosen algorithm
│
├── engine/ # The Simulation Loop
│ ├── __init__.py
│ ├── simulator.py # Manages turns, validates capacity limits, moves drones
│ └── state.py # Tracks where every drone is at a given turn
│
└── utils/ # Helper functions
├── __init__.py
└── visualizer.py # Organizer of colors, ANSI codes, and terminal output
```

## Algorithms !!!
### 1. Space-Time A* (Cooperative Path-finding)

This is the baseline algorithm you should build first. It is capable of solving the "Easy" and "Medium" maps efficiently.

**The Concept** Instead of searching through a traditional graph where vertices are just locations, Space-Time A* searches in a "cell-time space". In this space, every vertex is defined as a pair consisting of a specific location and a specific time step (e.g., `(roof1, turn_3)`).

**How to Construct It**

1. **Prioritization:** Assign an arbitrary order to your drones (e.g., D1, then D2, then D3).
    
2. **The Reservation Table:** Create a centralized data structure (like a dictionary or set) that tracks occupied space-time pairs.
    
3. **Sequential Planning:** * Run A* for D1. It finds its path and reserves its nodes and edges in the Reservation Table for specific turns.
    
    - Run A* for D2. As D2 evaluates potential neighboring nodes, it must check the Reservation Table. If D1 is scheduled to be at `corridorA` at `turn 4`, D2 treats `corridorA` at `turn 4` as a temporary wall. To avoid a vertex collision, D2 must either wait in its current cell for a turn or route around the obstacle.
        
4. **Capacity Handling:** In your project, zones have a `max_drones` capacity. Instead of a binary "blocked or free" check, your Reservation Table must track how many drones are at a location at a given time, rejecting moves only when the count exceeds the limit.
    

**Critical Evaluation:** Space-Time A* is greedy. Because it plans sequentially, the first drone gets the absolute best path, while the last drone gets the worst. On narrow maps, an early drone might park in a dead-end, completely trapping subsequent drones. This algorithm will likely fail to meet the tight turn limits of your "Capacity Hell" or "Challenger" maps.

---

### 2. Conflict-Based Search (CBS)

To hit the optimal turn counts (such as the 45-turn record on the Challenger map), you must implement Conflict-Based Search. CBS is the industry standard for optimal MAPF.

**The Concept** CBS is a two-level algorithm. It does not try to pathfind all drones at once. Instead, it assumes everyone can take their optimal path, detects where they crash, and iteratively adds rules (constraints) to prevent those specific crashes.

**How to Construct It**

1. **The High-Level Tree (Constraint Tree):** * Start a root node containing zero constraints.
    
    - Generate a mathematically optimal path for every drone independently (ignoring all other drones and collisions).
        
    - Simulate the joint plan and look for the first conflict. A conflict occurs when two drones occupy the same zone at the same time (vertex conflict) or cross the same connection simultaneously (edge conflict).
        
2. **Branching:** * If Drone A and Drone B crash at `roof1` at `turn 3`, you split the High-Level Tree into two new branches (nodes).
    
    - **Branch 1:** Adds a rule: "Drone A is prohibited from being at `roof1` at `turn 3`".
        
    - **Branch 2:** Adds a rule: "Drone B is prohibited from being at `roof1` at `turn 3`".
        
3. **The Low-Level Search:**
    
    - For Branch 1, you recalculate the path _only_ for Drone A using Space-Time A*, forcing it to respect this new negative constraint.
        
4. **Iteration:**
    
    - The algorithm continues exploring the Constraint Tree using a Best-First Search strategy until it finds a node where the joint plan has zero conflicts.
        

**Critical Evaluation:** CBS guarantees an optimal solution. However, it can be computationally heavy, resulting in a large search tree if many drones conflict repeatedly. You will need to optimize your Python data structures (using efficient queues and minimizing object creation) to keep it running smoothly.

---

### Where to Study

To build this without relying on pre-written code, you should research the academic literature surrounding these concepts.

1. **Search Queries to Use:** Do not search for Python tutorials. Search for "Conflict-Based Search MAPF," "Space-Time A* algorithm," and "Multi-Agent Path Finding optimal makespan."
    
2. **Key Researchers:** Look up papers and lectures by **Sven Koenig** (his paper _"Overview of Multi-Agent Path Finding (MAPF)"_ is an excellent starting point) and **Ariel Felner**.
    
3. **Visual References:** Search for "CBS MAPF visualization" on YouTube. Understanding how the Constraint Tree branches visually will make implementing the logic significantly easier.