import heapq

# Define movement directions and commands
directions = {'UP': (-1, 0), 'DOWN': (1, 0), 'LEFT': (0, -1), 'RIGHT': (0, 1)}
key_door_map = {'b': 'B', 'r': 'R', 'g': 'G', 'y': 'Y'}  # Maps keys to doors

# Step 1: Load the grid from grid.txt
def load_grid(filename):
    with open(filename, 'r') as file:
        grid = [list(line.strip()) for line in file.readlines()]
    agent_pos = None
    human_pos = None
    keys = {}
    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            if cell == 'm':
                agent_pos = (i, j)
            elif cell == 'h':
                human_pos = (i, j)
            elif cell in key_door_map:
                keys[cell] = (i, j)  # store key locations
    return grid, agent_pos, human_pos, keys

# Step 2: Parse human actions from human.txt
def load_human_actions(filename):
    actions = []
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split(': ')
            if len(parts) < 2:
                # Skip lines without expected format "T<number>: <instruction>"
                continue
            
            if parts[0].startswith("Move"):
                action, direction = parts[0].split()
                actions.append((action, direction))
            elif parts[0].startswith("Instruction"):
                # Extract requested key color
                key_color = parts[1].split()[-2][0].lower()  # e.g., 'y' for "yellow"
                actions.append(('Request', key_color))
    return actions

# Step 3: Pathfinding with A* to retrieve keys and move to human
def heuristic(start, end):
    return abs(start[0] - end[0]) + abs(start[1] - end[1])

def find_path(grid, start, goal, collected_keys):
    rows, cols = len(grid), len(grid[0])
    heap = [(0, start)]
    costs = {start: 0}
    parent_map = {start: None}

    while heap:
        _, current = heapq.heappop(heap)
        if current == goal:
            break

        for direction, (dx, dy) in directions.items():
            nx, ny = current[0] + dx, current[1] + dy
            if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] != 'W':
                cell = grid[nx][ny]
                if cell in key_door_map.values() and cell.lower() not in collected_keys:
                    continue  # Skip doors without keys
                new_cost = costs[current] + 1
                if (nx, ny) not in costs or new_cost < costs[(nx, ny)]:
                    costs[(nx, ny)] = new_cost
                    heapq.heappush(heap, (new_cost + heuristic((nx, ny), goal), (nx, ny)))
                    parent_map[(nx, ny)] = (current, direction)

    path = []
    current = goal
    while current != start:
        if current not in parent_map:
            return []  # No path
        parent, direction = parent_map[current]
        path.append((direction, current))
        current = parent

    return path[::-1]  # Reverse path to start from the beginning

# Step 4: Simulate the human actions
def simulate(grid, agent_pos, human_pos, actions, keys):
    collected_keys = set()
    instruction_number = 1  # Start numbering instructions

    for action, detail in actions:
        if action == 'Move':
            dx, dy = directions[detail]
            new_hx, new_hy = human_pos[0] + dx, human_pos[1] + dy
            if grid[new_hx][new_hy] != 'W':  # Move human if not a wall
                human_pos = (new_hx, new_hy)
                print(f"T{instruction_number}: My_position {human_pos}")
                instruction_number += 1
        
        elif action == 'Request':
            key = detail
            if key in keys:
                key_pos = keys[key]
                path_to_key = find_path(grid, agent_pos, key_pos, collected_keys)
                for direction, pos in path_to_key:
                    print(f"T{instruction_number}: Agent_{direction} {pos}")
                    instruction_number += 1
                
                # Pick up the key
                collected_keys.add(key)
                print(f"T{instruction_number}: Pick_up_{key.upper()}_key")
                instruction_number += 1
                agent_pos = key_pos  # Update agent's position to the key's location
                
                # Path to human
                path_to_human = find_path(grid, agent_pos, human_pos, collected_keys)
                for direction, pos in path_to_human:
                    print(f"T{instruction_number}: Agent_{direction} {pos}")
                    instruction_number += 1
                
                print(f"T{instruction_number}: Locate_human: {human_pos}")
                instruction_number += 1
                print(f"T{instruction_number}: Move_to_Human")
                instruction_number += 1
                agent_pos = human_pos  # Update agent's position to the human's location

    return agent_pos, human_pos

# Load grid and actions, then simulate
# Main execution 
grid, agent_pos, human_pos, keys = load_grid('Input_files/Grid_configurations/2_grid.txt')
actions = load_human_actions('Input_files/Human_actions/2_human.txt')
simulate(grid, agent_pos, human_pos, actions, keys)
