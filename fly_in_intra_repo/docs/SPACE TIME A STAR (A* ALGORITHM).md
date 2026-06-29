> Given a graph, a source node and a goal node, the algorithm finds the shortest path (with respect to the given weights) from source to goal.

## What is Space-Time A* Search Algorithm?

Standard A* searches across an X/Y geometric grid. Space-Time A* adds **Time** as the crucial third dimension. Because drones are dynamic moving obstacles, a node might be blocked at Turn 2, but completely open at Turn 3.

The algorithm evaluates future states not just by asking _"How do I get to the goal?"_, but by asking _"How do I get to the goal at this specific point in time without causing a traffic collision?"_

### How the Space-Time A* Algorithm Works
1. **Initialization**:
    
    - Start with a [[Heap queue Data structure|priority min-heap]] (`open_set`) containing the starting state at Turn 0: `(0, 0, drone.current_zone)`.
        
    - Initialize a `came_from` dictionary to track the unbroken chain of states for path reconstruction.
        
    - Initialize a `score` dictionary to record the absolute fastest elapsed time to reach any specific 3D state `(Zone, Time)`.
        
2. **While the `open_set` is not empty**:
    
    - Pop the state with the lowest **F-score** from the queue. This is the `current_state`.
        
    - **Goal Check:** If the `current_zone` is the `end_hub`, the path has been found. Trace the `came_from` ledger backward to reconstruct the timeline and return it.
        
    - **Neighbor Evaluation:** Generate all possible moves for the current turn. This includes adjacent zones _and_ the option to wait in the current zone.
        
    - For each potential move (neighbor):
        
        - **Apply Movement Physics:** Calculate the new `arrival_time` (the **G-cost**). Add `+1` turn for NORMAL/PRIORITY zones or waiting. Add `+2` turns for RESTRICTED zones. Skip BLOCKED zones.
            
        - **Enforce Node Capacity:** Check the global `reservations` calendar. If the number of drones already scheduled to be in that zone at the `arrival_time` exceeds its `max_drones`, discard the path (Collision avoided).
            
        - **Enforce Edge Capacity:** If moving to a new zone, check the `edge_reservations` calendar. If the connection's `max_link_capacity` is exceeded at the turn of departure, discard the path.
            
        - **Calculate Costs:** * Compute **H-cost**: The ideal time remaining to reach the goal (ignoring traffic).
            
            - Compute **F-score**: `arrival_time` ($G$) + `hcost` ($H$).
                
        - **State Tracking:** If this specific `(Zone, arrival_time)` state has already been visited faster or at the same time, skip it. Otherwise, log it in `score`, update `came_from`, and push it to the `open_set`.
            
3. **If the `open_set` is empty**:
    
    - Every possible future timeline results in a collision or a dead end. The goal is unreachable due to mathematical deadlock; return a failure (empty list).
        
#### Data structures use:
- 
## A* Algorithm vs [[Dijkstra Algorithm| Dijkstra]]

While both algorithms guarantee the shortest mathematical path, they diverge fundamentally in their use of foresight.

- **Dijkstra's Algorithm (The Heuristic Engine):** In standard Dijkstra, the priority queue is sorted strictly by **G** (the time/cost it took to reach a specific node). It treats all geometric directions equally because it possesses no data regarding the goal's location. In this architecture, a simplified Dijkstra (`_get_ideal_cost`) runs in the background to calculate the absolute minimum traffic-free distance from every node to the goal.
    
- __A_ Algorithm (The Guided Search):_* A* alters the blind search by introducing **H** (the Heuristic). The formula becomes **F = G + H**. In this equation, H acts as a mathematical penalty that punishes paths for moving away from the target.
    

### The Cost Variables in Space-Time

> **F (Total Estimated Timeline)** = **G (Arrival Time from Start)** + **H (Ideal Remaining Time to Goal)** * **G (Arrival Time):** The exact, immutable chronological turn the drone reaches the current evaluated node from Turn 0.

- **H (Heuristic):** The estimated minimum time required to travel from the current evaluated node directly to the final goal, calculated by the background Dijkstra function.