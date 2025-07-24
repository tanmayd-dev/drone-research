# Drone Energy Simulation Project

## Overview
This project simulates and analyzes the energy requirements for different modes of operation of a cluster of big and small drones tasked with surveying and acting on points of interest (POIs) on a map. The project supports two modes:

- **Independent Mode:** Each big drone and its small drones operate independently in their own region.
- **External Mode:** An external controller collects all detected POIs and globally assigns big drones using k-means clustering and optimized pathing.

## Modes

### Independent Mode
- The map is divided into regions, one per big drone (with margins to avoid overlap).
- Each big drone releases small drones to grid search its region.
- POIs are detected by small drones within their region.
- Each big drone visits the POIs detected in its region using a TSP+2opt optimized path.
- **Big drone travel energy:** Set by `energy_per_second` in the config (default 10).

### External Mode
- Small drones perform a grid search as in independent mode.
- All detected POIs are collected by an external controller.
- The controller clusters POIs using k-means and assigns big drones to cluster centers.
- Each big drone visits its assigned POIs using a TSP+2opt optimized path.
- **Big drone travel energy:** Set to 20 (hardcoded in the code).

## Energy Calculation
- **Small drones:** Travel energy is set by `energy_per_second` in the config (default 10).
- **Big drones:**
  - Independent mode: travel energy is set by `energy_per_second` in the config (default 10).
  - External mode: travel energy is set to 20.
- Detection and action energy are as specified in the config.

## How to Run
1. Ensure you have Python 3 installed.
2. Place `config.json`, `pois.json`, and `obstacles.json` in the project root.
3. To run a mode, navigate to its directory and run:
   ```bash
   python main.py
   ```
4. The results will be saved to `energy_results.csv` in the mode's directory.

## Visualization
Each mode includes a Pygame simulation:
```bash
python pygame_sim.py
```
Use the arrow keys to change the number of big and small drones. Press S to save the current view as an image.

## Directory Structure
- `independent_mode/` — Independent mode code, simulation, and results
- `external_mode/` — External mode (formerly proposed mode) code, simulation, and results
- `config.json`, `pois.json`, `obstacles.json` — Configuration and input data

## Contact
For questions or contributions, please contact the project maintainer. 