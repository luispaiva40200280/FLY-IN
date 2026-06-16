To understand the logic of the State Engine without looking at code, it is best to imagine the engine as an incredibly strict **Air Traffic Controller (ATC)** managing a network of airports (Zones) and flight paths (Connections).

The ATC operates on a strict clock. Every "tick" of the clock is one Turn. The ATC cannot move planes one by one; they must look at every pilot’s requested flight plan, check the math for the entire network simultaneously, and then approve or deny the movements all at once.

Here is the exact flow of how the ATC processes a single turn, broken down step-by-step.

### The Setup: The Master Board and the Draft Board

Before a turn begins, the ATC has a **Master Board** on the wall showing exactly where every drone currently is.

When the pilots submit their requested moves for the next turn, the ATC does not touch the Master Board. Instead, they pull out a piece of paper—the **Draft Board**. They copy the current locations onto the Draft Board and use it to do their math. This ensures they don't accidentally ruin the real state of the world while calculating.

### Phase 1: The Departure (Checking Out)

**The Goal:** Free up space so new drones can enter full zones.

The ATC looks at the requested moves. If Drone 1 is at _Hub A_ and requests to fly to _Hub B_, the ATC immediately erases Drone 1 from _Hub A_ on the **Draft Board**.

- **Example:** _Hub A_ can only hold 1 drone. Because Drone 1 is leaving, the Draft Board now shows _Hub A_ has 0 drones. It is completely empty.
    
- **Why this matters:** If Drone 2 wants to enter _Hub A_ on this exact same turn, the ATC will see that _Hub A_ is empty on the Draft Board and allow it. This solves the "simultaneous movement" rule.
    

### Phase 2: The Validation (The Safety Checks)

**The Goal:** Ensure none of the requested moves break the laws of physics.

The ATC now looks at where the drones _want_ to go. They check these requests against three strict rules. If any rule is broken, the ATC blows a whistle, rejects the moves, and halts the simulation.

1. **The Flight Path Check (Connections):** The ATC checks the corridors. If a corridor is a narrow tunnel that only allows 1 drone at a time, and both Drone 1 and Drone 2 submit plans to fly through it simultaneously, the ATC flags a collision and rejects the turn.
    
2. **The Normal Zone Check:** Drone 2 wants to land at _Hub A_. The ATC looks at the Draft Board. Because Drone 1 left _Hub A_ during Phase 1, there is a free spot. The ATC pencils Drone 2 into _Hub A_ on the Draft Board. If there was no free spot, the ATC would reject the move.
    
3. **The Restricted Zone Check (Future Booking):** Drone 3 wants to fly to the _Mountain Base_, which is a "Restricted" zone. It takes 2 turns to get there.
    
    - **The Catch:** The ATC cannot check if the _Mountain Base_ is empty _today_, because Drone 3 won't arrive today. It will arrive tomorrow.
        
    - **The Solution:** The ATC opens a separate **Future Calendar**. They look at tomorrow's date. If the _Mountain Base_ is fully booked for tomorrow, they reject Drone 3's takeoff _today_. If there is space tomorrow, the ATC writes Drone 3's name on tomorrow's calendar to reserve the spot.
        

### Phase 3: The Commit (Making it Official)

**The Goal:** Finalize the turn and announce the results.

If the ATC finishes Phase 2 without finding any crashes or over-bookings, the moves are declared legal.

1. The ATC takes the **Draft Board** and pins it to the wall. It officially becomes the new **Master Board**.
    
2. The ATC updates the pilots. Drones that requested normal moves are told they have "ARRIVED." Drones that requested restricted moves are told they are "IN TRANSIT" (mid-air).
    
3. The ATC prints the official log for the turn (e.g., `D1-HubA D2-tunnel`). Drones that decided to stay parked on the runway are ignored and not printed.
    

### The Special Case: The "Mid-Air" Drones

What happens to Drone 3, which is flying to the restricted _Mountain Base_, when the next turn begins?

It becomes a "ghost" to the ATC during Phase 1 and Phase 2.

- **In Phase 1 (Departure):** Drone 3 is already in the air. It doesn't leave a hub today, so it doesn't free up any space on the Draft Board.
    
- **In Phase 2 (Validation):** The ATC sees that Drone 3 has a "flight timer" of 1 turn remaining. The ATC does not check capacities or ask for a flight plan. It simply forces Drone 3 to land at the _Mountain Base_, knowing that space was already guaranteed by the Future Calendar yesterday.
    

By separating the math into these three strict phases—erasing departures, validating arrivals against the draft, and committing the final reality—the engine flawlessly handles complex traffic jams without allowing drones to mathematically crash into each other.

## Pseudo Code 

```python
class StateEngine:
    function __init__(map):
        self.map = map
        self.drones = map.drones
        self.future_reservations = empty_dictionary() 
        self.turn_counter = 0

    function execute_turn(proposed_moves):
        """
        proposed_moves: A dictionary mapping {Drone: TargetZone} for this turn.
        If a drone is waiting, TargetZone == drone.current_zone.
        """
        self.turn_counter += 1
        
        # --- INITIALIZE DOUBLE BUFFERS ---
        # next_occupancy will track the net changes for the new turn
        next_occupancy = copy(self.map.current_zone_occupancy)
        current_connection_usage = initialize_empty_edge_counters()
        
        validated_moves = []
        turn_output = []

        # =========================================================
        # PHASE 1: THE DEPARTURE (Freeing Capacity)
        # =========================================================
        for drone in self.drones:
            # Drones currently mid-flight (restricted transit) already left their
            # zone last turn, so they don't free up capacity today.
            if drone.state == IN_TRANSIT:
                continue 

            target = proposed_moves[drone]
            
            # If the drone is moving to a NEW zone, free its current space immediately
            if target != drone.current_zone:
                next_occupancy[drone.current_zone] -= 1


        # =========================================================
        # PHASE 2: THE VALIDATION (Enforcing Physics)
        # =========================================================
        for drone in self.drones:
            
            # SCENARIO A: Drone is mid-flight. FSM forces it to arrive.
            if drone.state == IN_TRANSIT:
                drone.transit_timer -= 1
                if drone.transit_timer == 0:
                    next_occupancy[drone.destination] += 1
                    validated_moves.append((drone, drone.destination, ARRIVED))
                continue

            target = proposed_moves[drone]

            # SCENARIO B: Drone is intentionally waiting in place.
            if target == drone.current_zone:
                # We didn't subtract it in Phase 1, so we don't add it here.
                continue 

            # Fetch the connection (edge) the drone wants to use
            connection = self.map.get_connection(drone.current_zone, target)

            # SCENARIO C: Drone wants to move. Validate Connection Capacity.
            if current_connection_usage[connection] + 1 > connection.max_link_capacity:
                RAISE SimulationError(f"Collision: {connection.name} capacity exceeded")

            # SCENARIO D: Validate Destination Zone Capacity
            if target.type == RESTRICTED:
                # Restricted validation: Check future capacity (Turn + 1)
                target_turn = self.turn_counter + 1
                future_count = self.future_reservations.get((target, target_turn), 0)
                
                if future_count + 1 > target.max_drones:
                    RAISE SimulationError(f"Deadlock: {target.name} will be full on arrival")
                
                # Lock in the reservation and mark edge usage
                self.future_reservations[(target, target_turn)] = future_count + 1
                current_connection_usage[connection] += 1
                
                validated_moves.append((drone, connection, IN_TRANSIT))
                
            else:
                # Normal/Priority validation: Check immediate next_occupancy capacity
                if next_occupancy[target] + 1 > target.max_drones:
                    RAISE SimulationError(f"Capacity Overflow: {target.name} is full")
                
                # Mark edge usage and update zone capacity
                current_connection_usage[connection] += 1
                next_occupancy[target] += 1
                
                validated_moves.append((drone, target, ARRIVED))


        # =========================================================
        # PHASE 3: THE COMMIT (State Update & Output formatting)
        # =========================================================
        # If we reached this point without raising errors, the turn is 100% legal.
        
        self.map.current_zone_occupancy = next_occupancy

        for (drone, target_object, new_state) in validated_moves:
            
            if new_state == IN_TRANSIT:
                drone.state = IN_TRANSIT
                drone.current_zone = None
                drone.transit_timer = 1
                drone.destination = proposed_moves[drone] # Save where it's going
                # Format: D1-connection_name
                turn_output.append(f"D{drone.id}-{target_object.name}")
                
            elif new_state == ARRIVED:
                drone.state = ARRIVED
                drone.current_zone = target_object
                drone.destination = None
                # Format: D1-zone_name
                turn_output.append(f"D{drone.id}-{target_object.name}")

        # Print the space-separated output for this turn
        if turn_output is not empty:
            print(" ".join(turn_output))
```