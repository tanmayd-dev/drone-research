# Independent Mode

## Overview
In Independent Mode, big drones are distributed evenly across the map. Each big drone releases a set of small drones to survey its local region. After surveying, small drones return to the same big drone that spawned them. Each big drone then independently visits every point of interest (POI) detected by its small drones.

## Algorithm Steps
1. **Big Drone Placement:**
   - The map is divided into regions, one per big drone (using a grid layout).
   - Each big drone is placed at the center of its region.
2. **POI Assignment:**
   - Each POI is assigned to the nearest big drone.
3. **Small Drone Deployment:**
   - Each big drone releases its assigned small drones.
   - Small drones are assigned POIs within their big drone's region.
   - Each small drone starts at the big drone, visits its assigned POIs, and returns to the big drone.
   - Energy is consumed for movement and for each detection.
4. **Big Drone Action:**
   - After all small drones return, each big drone visits all POIs detected by its small drones (in order).
   - Energy is consumed for movement.
5. **Energy Calculation:**
   - **Small drones:** Travel energy is set by `energy_per_second` in the config (default 10).
   - **Big drones:** Travel energy is also set by `energy_per_second` in the config (default 10).
   - Detection and action energy are as specified in the config.

**Note:** In external mode, big drone travel energy is set to 20 for comparison.

## How to Run
1. Ensure you have Python 3 installed.
2. Place `config.json`, `pois.json`, and `obstacles.json` in the parent directory.
3. Run the script:
   ```bash
   python main.py
   ```
4. The results will be saved to `energy_results.csv` in this directory. 