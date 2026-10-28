"""
Workload Partitioning Algorithms for Multi-UAV Systems.
Implements Size-Balanced K-Means and Spatial Grid Partitioning to minimize makespan bottlenecks.
"""

import math
import random
from typing import List, Dict, Any, Tuple


def euclidean_dist(p1: Dict[str, float], p2: Dict[str, float]) -> float:
    return math.hypot(p1["x"] - p2["x"], p1["y"] - p2["y"])


def size_balanced_kmeans(
    pois: List[Dict[str, float]],
    k: int,
    max_iter: int = 30,
    seed: int = 42
) -> Tuple[List[Dict[str, float]], List[List[Dict[str, float]]]]:
    """
    Size-Balanced K-Means clustering algorithm.
    Enforces capacity constraint C = ceil(N / k) per cluster to ensure equitable
    workload distribution and prevent single-drone makespan bottlenecks.
    """
    if not pois or k <= 0:
        return [], []

    if len(pois) <= k:
        centers = [{"x": p["x"], "y": p["y"]} for p in pois]
        clusters = [[p] for p in pois]
        while len(centers) < k:
            centers.append(centers[0] if centers else {"x": 500.0, "y": 500.0})
            clusters.append([])
        return centers, clusters

    rng = random.Random(seed)
    # Initialize centers using K-means++ heuristic
    centers = [rng.choice(pois)]
    for _ in range(1, k):
        dists = [min(euclidean_dist(p, c) ** 2 for c in centers) for p in pois]
        total_d = sum(dists)
        if total_d > 0:
            probs = [d / total_d for d in dists]
            r = rng.random()
            cum = 0.0
            chosen = pois[-1]
            for p, prob in zip(pois, probs):
                cum += prob
                if r <= cum:
                    chosen = p
                    break
            centers.append(chosen)
        else:
            centers.append(rng.choice(pois))

    capacity = math.ceil(len(pois) / k)

    for _ in range(max_iter):
        # Compute all (poi_idx, center_idx, distance) pairs
        distances = []
        for p_idx, p in enumerate(pois):
            for c_idx, c in enumerate(centers):
                distances.append((euclidean_dist(p, c), p_idx, c_idx))

        # Sort by ascending distance (greedy capacity assignment)
        distances.sort(key=lambda item: item[0])

        assigned_poi = set()
        cluster_counts = [0] * k
        clusters: List[List[Dict[str, float]]] = [[] for _ in range(k)]

        for d, p_idx, c_idx in distances:
            if p_idx not in assigned_poi and cluster_counts[c_idx] < capacity:
                assigned_poi.add(p_idx)
                cluster_counts[c_idx] += 1
                clusters[c_idx].append(pois[p_idx])

        # Handle any edge remaining unassigned POIs
        for p_idx, p in enumerate(pois):
            if p_idx not in assigned_poi:
                # Find cluster with remaining capacity or lowest count
                avail_idx = min(range(k), key=lambda idx: len(clusters[idx]))
                clusters[avail_idx].append(p)
                assigned_poi.add(p_idx)

        # Update centroids
        new_centers = []
        max_shift = 0.0
        for c_idx in range(k):
            if clusters[c_idx]:
                avg_x = sum(p["x"] for p in clusters[c_idx]) / len(clusters[c_idx])
                avg_y = sum(p["y"] for p in clusters[c_idx]) / len(clusters[c_idx])
                shift = math.hypot(centers[c_idx]["x"] - avg_x, centers[c_idx]["y"] - avg_y)
                max_shift = max(max_shift, shift)
                new_centers.append({"x": avg_x, "y": avg_y})
            else:
                new_centers.append(centers[c_idx])

        centers = new_centers
        if max_shift < 0.5:
            break

    return centers, clusters


def grid_partition(
    pois: List[Dict[str, float]],
    num_regions: int,
    map_size: Tuple[int, int] = (1000, 1000)
) -> Tuple[List[Dict[str, float]], List[List[Dict[str, float]]]]:
    """
    Independent mode grid spatial partition.
    Divides map into num_regions non-overlapping rectangles covering 100% of the field.
    """
    if num_regions <= 1:
        cx = map_size[0] / 2.0
        cy = map_size[1] / 2.0
        return [{"x": cx, "y": cy}], [pois[:]]

    map_w, map_h = map_size
    rows = max(1, round(math.sqrt(num_regions)))
    base_cols = num_regions // rows
    extra = num_regions % rows

    row_h = map_h / rows
    regions = []
    centers = []
    clusters: List[List[Dict[str, float]]] = [[] for _ in range(num_regions)]

    curr_y = 0.0
    for r in range(rows):
        cols_in_row = base_cols + (1 if r < extra else 0)
        col_w = map_w / cols_in_row
        y0 = curr_y
        y1 = map_h if r == rows - 1 else curr_y + row_h

        for c in range(cols_in_row):
            x0 = c * col_w
            x1 = map_w if c == cols_in_row - 1 else (c + 1) * col_w
            regions.append((x0, y0, x1, y1))
            centers.append({"x": (x0 + x1) / 2.0, "y": (y0 + y1) / 2.0})

        curr_y = y1

    for p in pois:
        assigned_idx = 0
        for i, (x0, y0, x1, y1) in enumerate(regions):
            if x0 <= p["x"] <= x1 and y0 <= p["y"] <= y1:
                assigned_idx = i
                break
        clusters[assigned_idx].append(p)

    return centers, clusters
