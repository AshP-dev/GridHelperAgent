import os
import heapq

# Define movement directions and commands
directions = {'UP': (-1, 0), 'DOWN': (1, 0), 'LEFT': (0, -1), 'RIGHT': (0, 1)}
key_door_map = {'b': 'B', 'r': 'R', 'g': 'G', 'y': 'Y'}  # Maps keys to doors

# Load grid from file
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

# Update human position based on action
def update_human_position(human_pos, action, detail):
    if action == 'Move':
        dx, dy = directions[detail]
        new_hx, new_hy = human_pos[0] + dx, human_pos[1] + dy
        return (new_hx, new_hy)
        
    return human_pos

# Parse human actions
def load_human_actions(filename, human_pos, grid):
    actions = []
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split(': ')
            if len(parts) < 2:
                continue
            if parts[0].startswith("Move"):
                action, direction = parts[0].split()
                direction = direction.upper()
                human_pos = update_human_position(human_pos, action, direction, grid)
                actions.append((action, direction))
            elif parts[0].startswith("Instruction"):
                instruction = parts[1].strip()
                if "unlock" in instruction:
                    # Find the closest door to the updated human position
                    closest_door, door_pos = find_closest_door(human_pos, grid)
                    if closest_door:
                        key_color = closest_door.lower()
                        actions.append(('Request', key_color))
                        actions.append(('Unlock', key_color))
                else:
                    key_color = instruction.split()[-2][0].lower()
                    actions.append(('Request', key_color))
            elif parts[0].startswith("Pick_up"):
                key_color = parts[0].split('_')[2][0].lower()
                actions.append(('Pick_up', key_color))
            elif parts[0].startswith("Unlock"):
                key_color = parts[0].split('_')[1][0].lower()
                actions.append(('Unlock', key_color))
    return actions, human_pos

def find_closest_door(human_pos, grid):
    rows, cols = len(grid), len(grid[0])
    min_distance = float('inf')
    closest_door = None
    door_pos = None
    for i in range(rows):
        for j in range(cols):
            cell = grid[i][j]
            if cell in key_door_map.values():
                distance = abs(human_pos[0] - i) + abs(human_pos[1] - j)
                if distance < min_distance:
                    min_distance = distance
                    closest_door = cell
                    door_pos = (i, j)
    return closest_door, door_pos

# Heuristic function for A*
def heuristic(start, end):
    return abs(start[0] - end[0]) + abs(start[1] - end[1])

# A* pathfinding function
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

    return path[::-1]  # Reverse path
    
    

# Simulation function with updated human position tracking
def simulate(grid, agent_pos, human_pos, actions, keys, result_file):
    collected_keys = set()
    print(f"Initial collected_keys: {collected_keys}")
    instruction_number = 1

    with open(result_file, "w") as f:
        print('012') 
        f.write(f"My_position {agent_pos}\n")
        
        for action, detail in actions:
            print(f'013: Action: {action}, Detail: {detail}')
            if action == 'Move':
                print('014')
                human_pos = update_human_position(human_pos, action, detail, grid)
                f.write(f"Human_position {human_pos}\n")
            elif action == 'Request':
                print('015')
                key = detail
                if key in keys:
                    print('023')
                    key_pos = keys[key]
                    path_to_key = find_path(grid, agent_pos, key_pos, collected_keys)
                    
                    for direction, pos in path_to_key:
                        f.write(f"Move {direction} {pos}\n")
                    
                    collected_keys.add(key)
                    print(f"Collected key: {key}, collected_keys: {collected_keys}")
                    f.write(f"Pick_up_{key.upper()}_key\n")
                    agent_pos = key_pos

                    # Track latest human position dynamically
                    path_to_human = find_path(grid, agent_pos, human_pos, collected_keys)
                    f.write(f"Locate_human: {human_pos}\n")
                    f.write("Move_to_Human:\n")
                    for direction, pos in path_to_human:
                        f.write(f"Move {direction} {pos}\n")
                    #agent_pos = human_pos

                    f.write(f"Drop_{key.upper()}_key\n")
                    collected_keys.remove(key)
                    print(f"Dropped key: {key}, collected_keys: {collected_keys}")
                    

            elif action == 'Pick_up':
                print('016')
                key = detail
                collected_keys.add(key)
                print(f"Picked up key: {key}, collected_keys: {collected_keys}")
                f.write(f"Pick_up_{key.upper()}_key\n")

            elif action == 'Unlock':
                print('017')
                key = detail
                if key in collected_keys:
                    f.write(f"Unlock_{key.upper()}_door\n")
                    collected_keys.remove(key)
                    print(f"Unlocked door with key: {key}, collected_keys: {collected_keys}")

            instruction_number += 1
            print('018')

# Main execution function
def main(grid_file, actions_file):
    print('021')
    grid, agent_pos, human_pos, keys = load_grid(grid_file)
    actions, human_pos = load_human_actions(actions_file, human_pos, grid)

    # Create output file based on the input file's name
    test_case_number = os.path.splitext(os.path.basename(grid_file))[0].split('_')[0]
    result_file = os.path.join("Results", f"{test_case_number}_result.txt")
    os.makedirs("Results", exist_ok=True)  # Ensure Results directory exists
    simulate(grid, agent_pos, human_pos, actions, keys, result_file)
    

# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python P2_testing.py <grid_file> <actions_file>")
    else:
        main(sys.argv[1], sys.argv[2])
