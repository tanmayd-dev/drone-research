import math
import numpy as np
from sklearn.cluster import KMeans
from functools import lru_cache
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

try:
    from numba import njit
    NUMBA = True
except ImportError:
    NUMBA = False

def dist(a, b):
    if isinstance(a, dict):
        return math.hypot(a['x'] - b['x'], a['y'] - b['y'])
    else:
        return np.linalg.norm(np.array(a) - np.array(b))

if NUMBA:
    @njit
    def dist_np(a, b):
        return np.sqrt(np.sum((a - b) ** 2))
else:
    def dist_np(a, b):
        return np.linalg.norm(a - b)

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

def ortools_tsp(coords):
    n = len(coords)
    if n <= 1:
        return list(range(n))
    dist_matrix = np.linalg.norm(coords[:, None, :] - coords[None, :, :], axis=2)
    dist_matrix = (dist_matrix * 1000).astype(int)
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)
    routing = pywrapcp.RoutingModel(manager)
    def distance_callback(from_index, to_index):
        return int(dist_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)])
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        index = routing.Start(0)
        route = []
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))
        return route
    else:
        return list(range(n))

def nearest_neighbor_tsp(start, points):
    if not points:
        return [start, start]
    coords = np.array([[p['x'], p['y']] for p in [start] + points])
    perm = ortools_tsp(coords)
    path = [ {'x': coords[i][0], 'y': coords[i][1]} for i in perm ]
    if path[0] != start:
        idx = path.index(start)
        path = path[idx:] + path[:idx]
    if path[-1] != start:
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

if NUMBA:
    @njit
    def path_length_np(path):
        total = 0.0
        for i in range(len(path)-1):
            total += dist_np(path[i], path[i+1])
        return total
else:
    def path_length_np(path):
        return sum(dist_np(path[i], path[i+1]) for i in range(len(path)-1))

def path_length(path):
    if path and isinstance(path[0], dict):
        return sum(dist(path[i], path[i+1]) for i in range(len(path)-1))
    else:
        return path_length_np(path)

def run_energy_sweep(config, pois):
    MAP_W, MAP_H = config['map_size']
    ENERGY_PER_SECOND = config['energy_per_second']
    ENERGY_PER_DETECTION = config['energy_per_detection']
    ENERGY_PER_ACTION = config.get('energy_per_action', 50)
    DRONE_SPEED = config['drone_speed']
    SMALL_DETECTION_RANGE = config.get('small_drone_detection_range', 5)
    REGION_MARGIN = 2
    BIG_DRONE_TRAVEL_ENERGY = config.get('big_drone_travel_energy', 20)
    SMALL_DRONE_RANGE = config.get('small_drone_range', [1, 20])
    results = []
    pois_np = np.array([[p['x'], p['y']] for p in pois]) if pois else np.empty((0,2))
    for num_big in range(config['big_drone_range'][0], config['big_drone_range'][1]+1):
        for num_small in range(SMALL_DRONE_RANGE[0], SMALL_DRONE_RANGE[1]+1):
            if num_small == 0:
                continue
            rows, cols = compute_grid(num_big)
            big_regions = []
            region_w = MAP_W / cols
            region_h = MAP_H / rows
            for i in range(num_big):
                row = i // cols
                col = i % cols
                x0 = col * region_w
                y0 = row * region_h
                x1 = (col+1) * region_w if (col < cols-1 or i != num_big-1) else MAP_W
                y1 = (row+1) * region_h if (row < rows-1 or i != num_big-1) else MAP_H
                if i == num_big-1:
                    x1 = MAP_W
                    y1 = MAP_H
                if col > 0:
                    x0 += REGION_MARGIN / 2
                if col < cols-1:
                    x1 -= REGION_MARGIN / 2
                if row > 0:
                    y0 += REGION_MARGIN / 2
                if row < rows-1:
                    y1 -= REGION_MARGIN / 2
                big_regions.append((x0, y0, x1, y1))
            small_drones_per_big = [num_small // num_big] * num_big
            for i in range(num_small % num_big):
                small_drones_per_big[i] += 1
            detected_pois = []
            top_left = {'x': 0, 'y': 0}
            total_energy = 0
            for i, (region, n_small) in enumerate(zip(big_regions, small_drones_per_big)):
                if n_small == 0:
                    continue
                x0, y0, x1, y1 = region
                sub_w = (x1 - x0) / n_small
                for j in range(n_small):
                    sx0 = x0 + j * sub_w
                    sx1 = sx0 + sub_w
                    sweep_path = grid_sweep_path((sx0, y0, sx1, y1), SMALL_DETECTION_RANGE)
                    path = [top_left] + sweep_path + [top_left]
                    path_np = np.array([[p['x'], p['y']] for p in path])
                    path_dist = path_length_np(path_np)
                    move_time = path_dist / DRONE_SPEED
                    total_energy += move_time * ENERGY_PER_SECOND
                    for poi_idx, poi in enumerate(pois):
                        px, py = poi['x'], poi['y']
                        in_region = (sx0 <= px < sx1) and (y0 <= py < y1)
                        if not in_region:
                            if (abs(px - sx0) < REGION_MARGIN or abs(px - sx1) < REGION_MARGIN or abs(py - y0) < REGION_MARGIN or abs(py - y1) < REGION_MARGIN):
                                region_centers = [{'x': (r[0]+r[2])/2, 'y': (r[1]+r[3])/2} for r in big_regions]
                                dists = [dist(poi, pos) for pos in region_centers]
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
                                t = max(0, min(1, ((px-xA)*dx + (py-xA)*dy)/(dx*dx+dy*dy)))
                                proj_x = xA + t*dx
                                proj_y = yA + t*dy
                                dist_to_seg = math.hypot(px-proj_x, py-proj_y)
                            if dist_to_seg <= SMALL_DETECTION_RANGE:
                                if poi not in detected_pois:
                                    detected_pois.append(poi)
                                total_energy += ENERGY_PER_DETECTION
                                break
            if detected_pois and len(detected_pois) >= num_big:
                kmeans_seed = hash((num_big, num_small)) % (2**32)
                X = np.array([[p['x'], p['y']] for p in detected_pois])
                kmeans = KMeans(n_clusters=num_big, random_state=kmeans_seed, n_init=10)
                labels = kmeans.fit_predict(X)
                centers = kmeans.cluster_centers_
                big_drone_positions = [{'x': float(c[0]), 'y': float(c[1])} for c in centers]
                big_drone_poi_chunks = [[] for _ in range(num_big)]
                for idx, label in enumerate(labels):
                    big_drone_poi_chunks[label].append(detected_pois[idx])
            elif detected_pois:
                big_drone_positions = detected_pois + [{'x': MAP_W/2, 'y': MAP_H/2} for _ in range(num_big - len(detected_pois))]
                big_drone_poi_chunks = [[p] for p in detected_pois] + [[] for _ in range(num_big - len(detected_pois))]
            else:
                big_drone_positions = [{'x': MAP_W/2, 'y': MAP_H/2} for _ in range(num_big)]
                big_drone_poi_chunks = [[] for _ in range(num_big)]
            for _, pois_list in zip(big_drone_positions, big_drone_poi_chunks):
                if pois_list:
                    tsp_path = nearest_neighbor_tsp({'x': 0, 'y': 0}, pois_list)
                    tsp_path = two_opt(tsp_path)
                    path_np = np.array([[p['x'], p['y']] for p in tsp_path])
                    path_dist = path_length_np(path_np)
                    move_time = path_dist / DRONE_SPEED
                    total_energy += move_time * BIG_DRONE_TRAVEL_ENERGY
                    total_energy += len(pois_list) * ENERGY_PER_ACTION
            results.append([num_big, num_small, round(total_energy, 2)])
    return results 