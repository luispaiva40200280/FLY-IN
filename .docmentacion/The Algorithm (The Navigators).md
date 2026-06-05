#### Option B: Space-Time A* Algorithm (The Navigator)

## Pseudo code 
``` python 
class Solver:
	FUNCTION pre_compute_priorities(drones):
    priority_list = []
    
    FOR EACH drone IN drones:
        # Run a simple, standard 2D Breadth-First Search (BFS)
        # Ignore all other drones and capacities.
        # Account for the +2 time cost of restricted zones.
        ideal_cost = simple_bfs(drone.start_zone, drone.goal_zone)
        
        ADD (drone, ideal_cost) TO priority_list
        
    # Sort the list. (e.g., Longest path goes first to claim highways)
    SORT priority_list BY ideal_cost DESCENDING
    
    RETURN priority_list
    
    FUNCTION space_time_a_star(drone, global_reservations):
    open_set = PriorityQueue()
    # A node is now a tuple: (Zone_Name, Current_Turn_Integer)
    start_node = (drone.start_zone, 0) 
    open_set.push(start_node)
    
    WHILE open_set IS NOT EMPTY:
        current_node = open_set.pop()
        current_zone = current_node.zone
        current_time = current_node.time
        
        IF current_zone == drone.goal_zone:
            RETURN reconstruct_path(current_node)
            
        FOR EACH neighbor IN get_adjacent_zones(current_zone) + [current_zone]:
            # Note: adding [current_zone] allows the drone to choose to "WAIT"
            
            # 1. Calculate temporal cost
            IF neighbor is RESTRICTED:
                arrival_time = current_time + 2
            ELSE:
                arrival_time = current_time + 1
                
            # 2. Check the global_reservations calendar
            IF global_reservations HAS capacity AT (neighbor, arrival_time):
                # 3. Check for edge swapping (two drones crossing a connection)
                IF NOT connection_is_blocked(current_zone, neighbor, current_time):
                    
                    next_node = (neighbor, arrival_time)
                    calculate_f_score(next_node)
                    open_set.push(next_node)
                    
    RETURN path_not_found_error
    
    FUNCTION register_path(drone, path, global_reservations):
    # path is a list of tuples: [(start, 0), (waypoint1, 1), (tunnel, 3), (goal, 4)]
    
    FOR EACH (zone, time) IN path:
        ADD 1 TO global_reservations[(zone, time)]
        
    master_schedule[drone.name] = path
```


### Calculating the ideal cost of each drone
### 1. The Ideal Cost Calculator (Dijkstra's Search)

You need a dedicated helper method that takes a single drone's starting location and returns the minimum time required to reach the `end_hub`.

**The Logic:**

- **The Min-Heap:** Use Python's built-in `heapq` module. A min-heap automatically sorts its contents so that the path with the lowest accumulated cost is always evaluated next.
    
- **The Queue Structure:** You push tuples into the heap formatted as `(current_time_cost, current_zone_name)`.
    
- **The Visited Set:** You must maintain a `set` of zone names that have already been evaluated. If you pop a zone from the heap that is already in the `visited` set, you immediately `continue` to prevent infinite loops.
    
- **Neighbor Evaluation:** For the current zone, loop through its neighbors using `self.map.list_adjacents`. Query your `self.map.zones` dictionary to check the neighbor's `ZoneType`.
    
    - If it is `RESTRICTED`, the new cost is `current_time_cost + 2`.
        
    - Otherwise, the new cost is `current_time_cost + 1`.
        
- **The Return:** The moment you pop a zone from the heap that equals `self.map.end_hub`, you immediately return its `current_time_cost`.
    

### 2. The Priority Sorter

Once the calculation method is built, the `_calculate_priorities` method orchestrates the swarm.

**The Logic:**

- Create an empty list (e.g., `priority_list`).
    
- Loop through every `drone` in `self.map.drones`.
    
- Pass the drone's `current_zone` into your Dijkstra helper method to get the `ideal_cost` integer.
    
- Append a tuple of `(drone, ideal_cost)` to the list.
    
- Sort the list. If you choose the **Longest Path First** strategy, you must sort the list in descending order based on the `ideal_cost` integer.
    
- Extract and return just the sorted `Drone` objects.
