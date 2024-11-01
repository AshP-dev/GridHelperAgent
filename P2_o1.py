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
            elif cell in key_door_map.keys():
                keys[cell] = (i, j)  # store key locations
    return grid, agent_pos, human_pos, keys

# Update human position based on action
def update_human_position(human_pos, action, detail):
    if action == 'Move':
        dx, dy = directions[detail.upper()]
        new_hx, new_hy = human_pos[0] + dx, human_pos[1] + dy
        return (new_hx, new_hy)
    return human_pos

# Parse human actions
def load_human_actions(filename, human_pos):
    actions = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if not parts:
                continue

            if parts[0] == "Move":
                if len(parts) >= 2:
                    action = 'Move'
                    direction = parts[1].upper()
                    actions.append((action, direction))
                    human_pos = update_human_position(human_pos, action, direction)
                else:
                    print("Warning: Malformed Move line:", line)

            elif parts[0] == "Instruction:":
                if len(parts) >= 5 and parts[1] == "Pick" and parts[2] == "up":
                    key_color = parts[3].lower()
                    actions.append(('Request', key_color))
                else:
                    print("Warning: Unrecognized instruction:", ' '.join(parts[1:]))

            elif parts[0].startswith("Pick_up_"):
                key_info = parts[0].split('_')
                if len(key_info) >= 3:
                    key_color = key_info[2].lower()
                    actions.append(('Pick_up', key_color))
                else:
                    print("Warning: Malformed Pick_up line:", line)

            elif parts[0].startswith("Unlock_"):
                key_info = parts[0].split('_')
                if len(key_info) >= 2:
                    key_color = key_info[1].lower()
                    actions.append(('Unlock', key_color))
                else:
                    print("Warning: Malformed Unlock line:", line)

            else:
                print("Warning: Unrecognized action line:", line)
    return actions, human_pos

# Heuristic function for A*
def heuristic(start, end):
    return abs(start[0] - end[0]) + abs(start[1] - end[1])

# A* pathfinding function
def find_path(grid, start, goal, collected_keys):
    rows, cols = len(grid), len(grid[0])
    open_list = []
    closed_set = set()
    heapq.heappush(open_list, (heuristic(start, goal), start, []))  # (f_cost, position, path)

    while open_list:
        f_cost, current_pos, path = heapq.heappop(open_list)
        if current_pos == goal:
            return path

        closed_set.add(current_pos)

        for dir_name, (dx, dy) in directions.items():
            neighbor = (current_pos[0] + dx, current_pos[1] + dy)
            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols:
                if neighbor in closed_set:
                    continue
                cell = grid[neighbor[0]][neighbor[1]]

                if cell == 'W':
                    continue  # Wall

                if cell in key_door_map.values() and cell.lower() not in collected_keys:
                    continue  # Locked door

                new_path = path + [(dir_name, neighbor)]
                heapq.heappush(open_list, (f_cost + 1 + heuristic(neighbor, goal), neighbor, new_path))

    print("No path found from", start, "to", goal)
    return []

# Simulation function with updated human position tracking
def simulate(grid, agent_pos, human_pos, actions, keys, result_file):
    collected_keys = set()
    instruction_number = 1

    with open(result_file, "w") as f:
        f.write(f"My_position {agent_pos}\n")
        for action, detail in actions:
            if action == 'Move':
                human_pos = update_human_position(human_pos, action, detail)
                f.write(f"Human_position {human_pos}\n")

            elif action == 'Request':
                key = detail
                if key in keys:
                    key_pos = keys[key]
                    path_to_key = find_path(grid, agent_pos, key_pos, collected_keys)
                    for direction, pos in path_to_key:
                        f.write(f"Move {direction} {pos}\n")
                    collected_keys.add(key)
                    f.write(f"Pick_up_{key.upper()}_key\n")
                    agent_pos = key_pos

                    # Track latest human position dynamically
                    path_to_human = find_path(grid, agent_pos, human_pos, collected_keys)
                    f.write(f"Locate_human: {human_pos}\n")
                    f.write("Move_to_Human:\n")
                    for direction, pos in path_to_human:
                        f.write(f"Move {direction} {pos}\n")
                    agent_pos = human_pos

                    f.write(f"Drop_{key.upper()}_key\n")
                    collected_keys.remove(key)
                else:
                    print(f"Key '{key}' not found in the grid.")

            elif action == 'Pick_up':
                key = detail
                collected_keys.add(key)
                f.write(f"Pick_up_{key.upper()}_key\n")

            elif action == 'Unlock':
                key = detail
                door_cell = key_door_map.get(key, None)
                if door_cell and key in collected_keys:
                    f.write(f"Unlock_{key.upper()}_door\n")
                    collected_keys.remove(key)
                else:
                    print(f"Cannot unlock door with key '{key}'. Key not in collected_keys or invalid key.")

            instruction_number += 1

# Main execution function
def main(grid_file, actions_file):
    grid, agent_pos, human_pos, keys = load_grid(grid_file)
    actions, human_pos = load_human_actions(actions_file, human_pos)

    test_case_number = os.path.splitext(os.path.basename(grid_file))[0].split('_')[0]
    result_file = os.path.join("Results", f"{test_case_number}_result.txt")
    os.makedirs("Results", exist_ok=True)
    simulate(grid, agent_pos, human_pos, actions, keys, result_file)

# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python P2_testing.py <grid_file> <actions_file>")
    else:
        main(sys.argv[1], sys.argv[2])
# Main execution function
def main(grid_file, actions_file):
    grid, agent_pos, human_pos, keys = load_grid(grid_file)
    actions, human_pos = load_human_actions(actions_file, human_pos)

    # Extract test case number safely
    filename = os.path.splitext(os.path.basename(grid_file))[0]
    parts = filename.split('_')

    print(f"grid_file: {grid_file}")
    print(f"Filename: {filename}")
    print(f"Parts after split: {parts}")

    if len(parts) >= 1:
        test_case_number = parts[0]
    else:
        test_case_number = 'default'  # Assign a default value or handle the error

    result_file = os.path.join("Results", f"{test_case_number}_result.txt")
    os.makedirs("Results", exist_ok=True)
    simulate(grid, agent_pos, human_pos, actions, keys, result_file)

# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python P2_o1.py <grid_file> <actions_file>")
    else:
        main(sys.argv[1], sys.argv[2])