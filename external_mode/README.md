# External Mode (with Central Controller)

## Overview
In External Mode, an external controller collects all detected POIs from the small drone grid search and assigns big drones using k-means clustering. Each big drone is placed at a cluster center and visits its assigned POIs using an optimized TSP+2opt path. Both the assignment and pathing are handled by the external controller for global efficiency.

## Algorithm Steps
1. **Small Drone Grid Search:**
   - The map is divided into regions (with margins) for grid search.
   - Small drones start at the center of their assigned region, perform a vertical grid sweep, and detect POIs within their detection range.
2. **POI Collection:**
   - All detected POIs are collected by the external controller.
3. **Big Drone Assignment (K-means):**
   - The external controller clusters all detected POIs using k-means (one cluster per big drone).
   - Each big drone is placed at its cluster center.
4. **Big Drone Path Optimization:**
   - Each big drone visits its assigned POIs using a TSP+2opt optimized path, starting and ending at the cluster center (simulation) or top left (main calculation).
5. **Energy Calculation:**
   - **Small drones:** Travel energy is set by `energy_per_second` in the config (default 10).
   - **Big drones:** Travel energy is set to 20 per second of movement (hardcoded in the code).
   - Detection and action energy are as specified in the config.

## How to Run
1. Ensure you have Python 3 installed.
2. Place `config.json`, `pois.json`, and `obstacles.json` in the parent directory.
3. Run the script:
   ```bash
   python main.py
   ```
4. The results will be saved to `energy_results.csv` in this directory.

## Visualization
To visualize the external mode simulation:
```bash
python pygame_sim.py
```
Use the arrow keys to change the number of big and small drones. Press S to save the current view as an image. 