"""
TSP Routing Optimization using Nearest-Neighbor heuristic and Simulated Annealing (SA) 2-opt swaps.
Minimizes total flight distance and energy expenditure for multi-drone tours.
"""

import math
import random
from typing import List, Dict, Any


def dist(p1: Dict[str, float], p2: Dict[str, float]) -> float:
    return math.hypot(p1["x"] - p2["x"], p1["y"] - p2["y"])


def path_length(path: List[Dict[str, float]]) -> float:
    if len(path) < 2:
        return 0.0
    return sum(dist(path[i], path[i+1]) for i in range(len(path) - 1))


def nearest_neighbor_tsp(start: Dict[str, float], points: List[Dict[str, float]]) -> List[Dict[str, float]]:
    """
    Greedy Nearest Neighbor initialization for TSP starting and ending at 'start'.
    """
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


def two_opt_swap(path: List[Dict[str, float]], i: int, j: int) -> List[Dict[str, float]]:
    """
    Reverses the path slice between indices i and j.
    """
    return path[:i] + path[i:j+1][::-1] + path[j+1:]


def simulated_annealing_tsp(
    path: List[Dict[str, float]],
    t_init: float = 100.0,
    alpha: float = 0.98,
    max_iter: int = 1500,
    seed: int = 42
) -> List[Dict[str, float]]:
    """
    Simulated Annealing TSP optimization.
    Uses 2-opt candidate moves with Metropolis probability acceptance e^(-delta/T)
    to escape local minima and find high-quality tours.
    """
    n = len(path)
    if n <= 3:
        return path[:]

    rng = random.Random(seed)
    best_path = path[:]
    best_len = path_length(best_path)
    current_path = path[:]
    current_len = best_len

    t = t_init

    for _ in range(max_iter):
        if t < 1e-4:
            break

        # Pick random 2-opt swap indices (preserve start and end depot)
        i = rng.randint(1, n - 3)
        j = rng.randint(i + 1, n - 2)

        candidate = two_opt_swap(current_path, i, j)
        candidate_len = path_length(candidate)
        diff = candidate_len - current_len

        # Metropolis acceptance criterion
        if diff < 0 or (rng.random() < math.exp(-diff / t)):
            current_path = candidate
            current_len = candidate_len
            if current_len < best_len:
                best_path = current_path[:]
                best_len = current_len

        t *= alpha

    return best_path
