_This project has been created as part of the 42 curriculum by lpaiva_

## Description

> Design an efficient drone routing system that navigates multiple drones through connected zones while minimizing simulation turns and handling movement constraints

The objective for this project is to implement a __Multi-Agent Path Finding (MAPF)__ so it can solve a single map in the shorts amount of Turns as possible. Each map is construct with a group of zones (having two specific zones to be the end and the start of the map), a fixed number of drones, and every two zones are connected with a connection that has specific rules such as the max number of drones that can be on it in the same time.

**NETWORK (MAP) TYPOLOGY:** 
- Zones : Zone Type (cost of the travel in number of turns), Max Drones in simultaneous
- Connections: Max Drones that can travel in simultaneous
- Start Zone: Inicial zone of the map 
- End Zone: Last zone of the map
- Drone: Object that needs to travel between the first zone and the last respecting the map roles
#### Multi-Agent Path Finding (MAPF)
- Multi-Agent Path Finding (MAPF) is the computational problem of finding collision-free paths for multiple agents—such as robots, vehicles, or drones—from their respective starting locations to their target destinations within a shared environment. In the context of the **Fly-in** simulation, MAPF is implemented to route a swarm of autonomous drones through a complex graph of zones and connections. Because certain zones have strict capacity limits (bottlenecks) or require varying transit times (restricted airspace), standard path-finding algorithms like basic __A* or Dijkstra's__ are insufficient.

## Algorithms choices:
- **SPACE TIME A STAR (A* ALGORITHM)**: Standard A* searches across an X/Y geometric grid. Space-Time A* adds **Time** as the crucial third dimension. Because drones are dynamic moving obstacles, a node might be blocked at Turn 2, but completely open at Turn 3.
- **Dijkstra Algorithm**: It specifically implemented as a Uniform-Cost Search via `_get_ideal_cost`) does **not** calculate the final, collision-free paths. Instead, it serves as the static baseline calculator. It assumes the drone is the only object on the map and evaluates the raw topological physics of the network.
## Instructions
- To run this Application we use the make file to run `commands` necessary to run the scrips in the terminal
 
 **Makefile Rules:**
- To install the dependencies, run:

```shell
make install
```

- To run the simulation with a specific map, use the following command:

```shell
make run MAP=<map>
```

**Development Commands:**
- **`make debug`**: Runs the program with Python's debugger (`pdb`).
- **`make lint`**: Checks the codes' compliance with the rules of `flake8` and `mypy`.
- **`make lint-strict`** Checks the codes' compliance with the rules of `flake8` and `mypy` with the `--strict` flag.
- **`make clean`**: Removes caches and temporary files.
  
## Resources

### Web graphic 

### AI USAGE