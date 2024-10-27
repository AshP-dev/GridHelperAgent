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
                key_color = parts[1].split()[-2][0].lower()  # e.g., 'r' for "red"
                actions.append(('Request', key_color))
            elif parts[0].startswith("Pick_up"):
                key_color = parts[0].split('_')[2][0].lower()  # e.g., 'r' for "RED"
                actions.append(('Pick_up', key_color))
            elif parts[0].startswith("Unlock"):
                key_color = parts[0].split('_')[1][0].lower()  # e.g., 'b' for "blue"
                actions.append(('Unlock', key_color))
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
                print(f"My_position {human_pos}")
        
        elif action == 'Request':
            key = detail
            if key in keys:
                key_pos = keys[key]
                path_to_key = find_path(grid, agent_pos, key_pos, collected_keys)
                for direction, pos in path_to_key:
                    print(f"{direction} {pos}")
                
                # Pick up the key
                collected_keys.add(key)
                print(f"Pick_up_{key.upper()}_key")
                agent_pos = key_pos  # Update agent's position to the key's location
                
                # Update human position based on remaining actions
                for remaining_action, remaining_detail in actions[instruction_number:]:
                    if remaining_action == 'Move':
                        dx, dy = directions[remaining_detail]
                        new_hx, new_hy = human_pos[0] + dx, human_pos[1] + dy
                        if grid[new_hx][new_hy] != 'W':  # Move human if not a wall
                            human_pos = (new_hx, new_hy)
                
                # Path to human
                path_to_human = find_path(grid, agent_pos, human_pos, collected_keys)
                for direction, pos in path_to_human:
                    print(f"{direction} {pos}")
                
                print(f"Locate_human: {human_pos}")
                print(f"Move_to_Human:")
                agent_pos = human_pos  # Update agent's position to the human's location

                # Drop the key
                print(f"Drop_{key.upper()}_key")
                collected_keys.remove(key)

        elif action == 'Pick_up':
            key = detail
            collected_keys.add(key)
            print(f"Pick_up_{key.upper()}_key")

        elif action == 'Unlock':
            key = detail
            if key in collected_keys:
                print(f"Unlock_{key.upper()}_door")
                collected_keys.remove(key)

        instruction_number += 1

    return agent_pos, human_pos

# Main execution function
def main(grid_file, actions_file):
    grid, agent_pos, human_pos, keys = load_grid(grid_file)
    actions = load_human_actions(actions_file)
    simulate(grid, agent_pos, human_pos, actions, keys)

# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python P2_testing.py <grid_file> <actions_file>")
    else:
        main(sys.argv[1], sys.argv[2])
