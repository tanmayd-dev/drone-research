import json
import csv
import os
import math
from itertools import product

# Load config
with open('../config.json') as f:
    config = json.load(f)

with open(f"../{config['pois_file']}") as f:
    pois = json.load(f)

with open(f"../{config['obstacles_file']}") as f:
    obstacles = json.load(f)

MAP_W, MAP_H = config['map_size']
ENERGY_PER_SECOND = config['energy_per_second']
ENERGY_PER_DETECTION = config['energy_per_detection']
DRONE_SPEED = config['drone_speed']
ENERGY_PER_ACTION = config.get('energy_per_action', 50)
SMALL_DETECTION_RANGE = config.get('small_drone_detection_range', 5)
REGION_MARGIN = 2  # pixels

# Helper: Euclidean distance
def dist(a, b):
    return math.hypot(a['x'] - b['x'], a['y'] - b['y'])

# Helper: Split list into n nearly equal parts
def split_list(lst, n):
    k, m = divmod(len(lst), n)
    return [lst[i*k + min(i, m):(i+1)*k + min(i+1, m)] for i in range(n)]

def compute_grid(num_cells):
    cols = math.ceil(math.sqrt(num_cells))
    rows = math.ceil(num_cells / cols)
    return rows, cols

def grid_sweep_path(region, step):
    x0, y0, x1, y1 = region
    path = []
    x = x0
    direction = 1
    while x <= x1:
        if direction == 1:
            path.append({'x': x, 'y': y0})
            path.append({'x': x, 'y': y1})
        else:
            path.append({'x': x, 'y': y1})
            path.append({'x': x, 'y': y0})
        x += step
        direction *= -1
    return path

def nearest_neighbor_tsp(start, points):
    if not points:
        return [start, start]
    unvisited = points[:]
    path = [start]
    curr = start
    while unvisited:
        next_p = min(unvisited, key=lambda p: dist(curr, p))
        path.append(next_p)
        curr = next_p
        unvisited.remove(next_p)
    path.append(start)
    return path

def two_opt(path):
    best = path[:]
    improved = True
    while improved:
        improved = False
        for i in range(1, len(best) - 2):
            for j in range(i + 1, len(best) - 1):
                if j - i == 1:
                    continue
                new_path = best[:i] + best[i:j][::-1] + best[j:]
                if path_length(new_path) < path_length(best):
                    best = new_path
                    improved = True
        path = best
    return best

def path_length(path):
    return sum(dist(path[i], path[i+1]) for i in range(len(path)-1))

def main():
    results = []
    for num_big in range(config['big_drone_range'][0], config['big_drone_range'][1]+1):
        for mult in range(config['small_drone_multiplier_range'][0], config['small_drone_multiplier_range'][1]+1):
            num_small = num_big * mult
            if num_small == 0:
                continue
            # Place big drones in a grid that covers the map
            rows, cols = compute_grid(num_big)
            big_drone_positions = []
            big_regions = []
            region_w = MAP_W / cols
            region_h = MAP_H / rows
            for i in range(num_big):
                row = i // cols
                col = i % cols
                # For the last region, stretch to the map edge
                x0 = col * region_w
                y0 = row * region_h
                x1 = (col+1) * region_w if (col < cols-1 or i != num_big-1) else MAP_W
                y1 = (row+1) * region_h if (row < rows-1 or i != num_big-1) else MAP_H
                if i == num_big-1:
                    x1 = MAP_W
                    y1 = MAP_H
                # Add margin except for outermost edges
                if col > 0:
                    x0 += REGION_MARGIN / 2
                if col < cols-1:
                    x1 -= REGION_MARGIN / 2
                if row > 0:
                    y0 += REGION_MARGIN / 2
                if row < rows-1:
                    y1 -= REGION_MARGIN / 2
                big_regions.append((x0, y0, x1, y1))
                x = (x0 + x1) / 2
                y = (y0 + y1) / 2
                big_drone_positions.append({'x': x, 'y': y})
            # Assign small drones to big drones
            small_drones_per_big = [num_small // num_big] * num_big
            for i in range(num_small % num_big):
                small_drones_per_big[i] += 1
            total_energy = 0
            detected_pois = [[] for _ in range(num_big)]
            # For each big drone, split its region among its small drones
            for i, (big_pos, region, n_small) in enumerate(zip(big_drone_positions, big_regions, small_drones_per_big)):
                if n_small == 0:
                    continue
                x0, y0, x1, y1 = region
                sub_w = (x1 - x0) / n_small
                for j in range(n_small):
                    sx0 = x0 + j * sub_w
                    sx1 = sx0 + sub_w
                    sweep_path = grid_sweep_path((sx0, y0, sx1, y1), SMALL_DETECTION_RANGE)
                    # Small drone starts/ends at big drone
                    path = [big_pos] + sweep_path + [big_pos]
                    path_dist = sum(dist(path[k], path[k+1]) for k in range(len(path)-1))
                    move_time = path_dist / DRONE_SPEED
                    total_energy += move_time * ENERGY_PER_SECOND
                    # Detect POIs within detection range of sweep, but only if POI center is in this region or margin logic
                    for poi in pois:
                        px, py = poi['x'], poi['y']
                        # Check if POI is in this region (excluding margin)
                        in_region = (sx0 <= px < sx1) and (y0 <= py < y1)
                        # If on the margin, assign to closest big drone
                        if not in_region:
                            # If on the border, check if within margin
                            if (abs(px - sx0) < REGION_MARGIN or abs(px - sx1) < REGION_MARGIN or abs(py - y0) < REGION_MARGIN or abs(py - y1) < REGION_MARGIN):
                                dists = [dist(poi, pos) for pos in big_drone_positions]
                                closest_idx = dists.index(min(dists))
                                if closest_idx != i:
                                    continue
                            else:
                                continue
                        for seg_idx in range(len(sweep_path)-1):
                            xA, yA = sweep_path[seg_idx]['x'], sweep_path[seg_idx]['y']
                            xB, yB = sweep_path[seg_idx+1]['x'], sweep_path[seg_idx+1]['y']
                            dx, dy = xB-xA, yB-yA
                            if dx == dy == 0:
                                dist_to_seg = math.hypot(px-xA, py-yA)
                            else:
                                t = max(0, min(1, ((px-xA)*dx + (py-yA)*dy)/(dx*dx+dy*dy)))
                                proj_x = xA + t*dx
                                proj_y = yA + t*dy
                                dist_to_seg = math.hypot(px-proj_x, py-proj_y)
                            if dist_to_seg <= SMALL_DETECTION_RANGE:
                                if poi not in detected_pois[i]:
                                    detected_pois[i].append(poi)
                                    total_energy += ENERGY_PER_DETECTION
                                break
            # After survey, big drone visits all its detected POIs (TSP order)
            for big_pos, pois_list in zip(big_drone_positions, detected_pois):
                if pois_list:
                    tsp_path = nearest_neighbor_tsp(big_pos, pois_list)
                    tsp_path = two_opt(tsp_path)
                    path_dist = path_length(tsp_path)
                    move_time = path_dist / DRONE_SPEED
                    total_energy += move_time * ENERGY_PER_SECOND
                    total_energy += len(pois_list) * ENERGY_PER_ACTION
            results.append([num_big, num_small, round(total_energy, 2)])
    # Write results to CSV
    with open('energy_results.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['num_big_drones', 'num_small_drones', 'total_energy'])
        writer.writerows(results)

    # Plotting
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        data = np.array(results)
        if data.size > 0:
            pivot = {}
            for row in results:
                big, small, energy = row
                pivot[(big, small)] = energy
            bigs = sorted(set(row[0] for row in results))
            smalls = sorted(set(row[1] for row in results))
            Z = np.zeros((len(smalls), len(bigs)))
            for i, s in enumerate(smalls):
                for j, b in enumerate(bigs):
                    Z[i, j] = pivot.get((b, s), np.nan)
            plt.figure(figsize=(8,6))
            plt.imshow(Z, aspect='auto', origin='lower',
                       extent=[min(bigs), max(bigs), min(smalls), max(smalls)],
                       cmap='viridis')
            plt.colorbar(label='Total Energy')
            plt.xlabel('Number of Big Drones')
            plt.ylabel('Number of Small Drones')
            plt.title('Energy vs. Big and Small Drones')
            plt.savefig('energy_plot.png')
            plt.close()
            # Interpolated plot
            try:
                from scipy.interpolate import griddata
                points = np.array([[row[0], row[1]] for row in results])
                values = np.array([row[2] for row in results])
                grid_bigs, grid_smalls = np.mgrid[min(bigs):max(bigs):200j, min(smalls):max(smalls):200j]
                grid_energy = griddata(points, values, (grid_bigs, grid_smalls), method='nearest')
                plt.figure(figsize=(8,6))
                plt.imshow(grid_energy.T, extent=(min(bigs), max(bigs), min(smalls), max(smalls)), origin='lower', aspect='auto', cmap='viridis')
                plt.colorbar(label='Total Energy (Interpolated)')
                plt.xlabel('Number of Big Drones')
                plt.ylabel('Number of Small Drones')
                plt.title('Energy vs. Big and Small Drones (Interpolated)')
                plt.savefig('energy_plot_interpolated.png')
                plt.close()
            except ImportError:
                print('scipy not installed; skipping interpolated plot.')
    except ImportError:
        print('matplotlib or numpy not installed; skipping plot.')

if __name__ == '__main__':
    main() 