from heapq import heappush, heappop

# Directions: Map movement commands to grid coordinates
DIRECTIONS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1)
}

# Parse grid from file
def parse_grid(filename):
    grid = []
    human_position = None
    agent_position = None
    keys = {}
    gems = []
    with open(filename, 'r') as f:
        for i, line in enumerate(f):
            row = list(line.strip().split())
            grid.append(row)
            for j, cell in enumerate(row):
                if cell == 'h':
                    human_position = (i, j)
                elif cell == 'm':
                    agent_position = (i, j)
                elif cell in 'brg':
                    keys[cell] = (i, j)
                elif cell == 'g':
                    gems.append((i, j))
    return grid, human_position, agent_position, keys, gems

# Read human instructions from file
def parse_human_instructions(filename):
    instructions = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("Move"):
                direction = line.split(" ")[-1]
                instructions.append(("MOVE", direction))
            elif "Instruction" in line:
                key_request = line.split()[-2][:-1].lower()  # Extract 'red', 'blue', or 'green'
                instructions.append(("REQUEST", key_request))
    return instructions

# Move human according to instructions
def move_human(human_pos, direction, grid):
    dx, dy = DIRECTIONS[direction]
    new_x, new_y = human_pos[0] + dx, human_pos[1] + dy
    if 0 <= new_x < len(grid) and 0 <= new_y < len(grid[0]) and grid[new_x][new_y] != 'W':
        return (new_x, new_y)
    return human_pos  # No movement if wall or out of bounds

# Check if agent can deliver requested key
def deliver_key(agent_position, human_position, collected_keys, requested_key):
    if agent_position == human_position and requested_key in collected_keys:
        print(f"Delivered {requested_key.upper()} key to the human.")
        collected_keys.remove(requested_key)
        return True
    return False

# Main pathfinding function
def pathfinding(grid, agent_position, human_position, keys, gems, instructions):
    # Initialize the state of keys
    collected_keys = set()
    path = [agent_position]
    
    for instruction_type, instruction in instructions:
        if instruction_type == "MOVE":
            # Move the human and check if agent needs to follow
            human_position = move_human(human_position, instruction, grid)
            print(f"Human moved to {human_position}")

        elif instruction_type == "REQUEST":
            # Check if agent has the requested key and is near the human
            requested_key = instruction[0]  # 'r' for red, 'g' for green, 'b' for blue
            print(f"Human requested the {requested_key.upper()} key")
            if deliver_key(agent_position, human_position, collected_keys, requested_key):
                continue  # Skip to next instruction if delivered successfully

        # Continue agent pathfinding logic to reach or follow the human
        # (Add agent pathfinding logic here to collect keys/gems as needed)
    
    return path

# Example usage
grid_file = 'Input_files/Grid_configurations/1_grid.txt'
human_file = 'Input_files/Human_actions/1_human.txt'
grid, human_position, agent_position, keys, gems = parse_grid(grid_file)
instructions = parse_human_instructions(human_file)

# Execute pathfinding and key delivery
pathfinding(grid, agent_position, human_position, keys, gems, instructions)
