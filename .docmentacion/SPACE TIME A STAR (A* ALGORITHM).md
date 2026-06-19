> Given a graph, a source node and a goal node, the algorithm finds the shortest path (with respect to the given weights) from source to goal.


##  [What is A* Search Algorithm?](https://www.geeksforgeeks.org/dsa/a-search-algorithm/)
### How A* Search Algo works?
Here's how the A* search algorithm works:
1. ****Initialization****:
    - Start with an open list containing the start node. Initially this open set will have only the start node and all the costs will be only 0
    - Start with an empty closed list.
2. ****While the open list is not empty****:
    - Select the node with the lowest __f__ value from the open list. This node is the current node.
    - If the current node is the goal node, the path has been found; reconstruct the path and return it.
    - If not move the current node to the closed list.
    - For each neighbor of the current node:
        - If the neighbor is in the closed list or is a wall, skip it.
        - If the neighbor is not in the open list:
            - Compute its __g__ value (cost from the start node to the current node plus the cost from the current node to the neighbor).
            - Compute its __h__ value (heuristic estimate of the cost from the neighbor to the goal).
            - Add it to the open list with __f__=__g__+__h__ and set the parent of the neighbor to the current node.
        - If the neighbor is already in the open list:
            - If the new __g__ value is lower than the current __g__ value, update the neighbor's __g__ and __f__ values and update its parent to the current node.
3. ****If the open list is empty****:
    - The goal is unreachable; return failure.

- Informally speaking, A* Search algorithms, unlike other traversal techniques, it has “brains”. What it means is that it is really a smart algorithm which separates it from the other conventional algorithms. This fact is cleared in detail in below sections.  And it is also worth mentioning that many games and web-based maps use this algorithm to find the shortest path very efficiently (approximation).
- 


# A* algorithm vs Dijkstra 
[^1]
- In standard Dijkstra, the priority queue is sorted strictly by **G** (the time/cost it took to reach a specific node). It treats all geometric directions equally because it possesses no data regarding the goal's location.

- A* alters this by introducing **H** (the Heuristic). The formula becomes **F=G+H**. In this equation, H acts exactly as the penalty you described. It is a mathematical weight that punishes nodes for moving away from the target.
> F (final cost ) = G ( arrival time from the start) + H (minimal arrival time form a specific neighbor node) 


[^1]: A* is an extension of [****Dijkstra's algorithm****](https://www.geeksforgeeks.org/dsa/introduction-to-dijkstras-shortest-path-algorithm/) and uses heuristics to improve the efficiency of the search by prioritizing paths that are likely to be closer to the goal.
