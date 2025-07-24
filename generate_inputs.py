import json
import random

# Load config
with open('config.json') as f:
    config = json.load(f)

MAP_W, MAP_H = config['map_size']

# User-specified or default values
NUM_POIS = config.get('num_pois', 20)
NUM_OBSTACLES = config.get('num_obstacles', 10)
OBSTACLE_MIN_RADIUS = config.get('obstacle_min_radius', 10)
OBSTACLE_MAX_RADIUS = config.get('obstacle_max_radius', 30)

# Generate POIs
pois = [
    {"x": random.randint(0, MAP_W), "y": random.randint(0, MAP_H)}
    for _ in range(NUM_POIS)
]

# Generate obstacles
obstacles = [
    {
        "x": random.randint(0, MAP_W),
        "y": random.randint(0, MAP_H),
        "radius": random.randint(OBSTACLE_MIN_RADIUS, OBSTACLE_MAX_RADIUS)
    }
    for _ in range(NUM_OBSTACLES)
]

with open('pois.json', 'w') as f:
    json.dump(pois, f, indent=2)

with open('obstacles.json', 'w') as f:
    json.dump(obstacles, f, indent=2)

print(f"Generated {NUM_POIS} POIs and {NUM_OBSTACLES} obstacles.") 