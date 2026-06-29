> Given a graph and a source node, Dijkstra's algorithm finds the absolute shortest path to a goal by exploring all possible directions based strictly on accumulated cost. In the context of this swarm engine, it acts as the **Heuristic Engine**, calculating the mathematical minimum traversal time while completely ignoring dynamic drone traffic.

## What is the Dijkstra Algorithm in this Architecture?

Standard Dijkstra's algorithm is a blind search. It explores a graph evenly in all directions like a ripple in a pond, maintaining a priority queue to ensure it always expands the shortest known path first.

In this architecture, Dijkstra (specifically implemented as a Uniform-Cost Search via `_get_ideal_cost`) does **not** calculate the final, collision-free paths. Instead, it serves as the static baseline calculator. It assumes the drone is the only object on the map and evaluates the raw topological physics of the network.
1. **Initialization**:
    - Start with a priority min-heap (`priority_queue`) containing the starting state: `(0, current_zone)`.
    - Initialize a `visited` set to permanently close nodes once their absolute fastest arrival time has been mathematically locked in. This prevents infinite cycles.
2. **While the `priority_queue` is not empty**:
    - Pop the state with the lowest **accumulated time cost** from the queue.
    - **Visited Check:** If the `zone_name` is already in the `visited` ledger, skip it. Otherwise, add it to the `visited` set.
    - **Goal Check:** If the `zone_name` is the `end_zone`, the absolute shortest traffic-free path has been found. Return the total integer `time_cost`.
    - **Neighbor Evaluation:** Generate all physically adjacent zones based on the map's static connections.
    - For each adjacent node:
        - **Apply Static Physics:** Calculate the new traversal time.
            - Add `+1` turn for entering `NORMAL` or `PRIORITY` zones.
            - Add `+2` turns for entering `RESTRICTED` zones.
            - Skip `BLOCKED` zones entirely.
        - **Queuing:** Push the new `(new_cost, neighbor_name)` tuple into the `priority_queue`. Because the queue is a min-heap, the algorithm is forced to continually explore the paths with the lowest accumulated penalties.
3. **If the `priority_queue` is empty**:
    - The destination is mathematically unreachable (e.g., completely walled off by `BLOCKED` zones). The engine returns `-1`.