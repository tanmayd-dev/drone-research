"""
Unit tests for Size-Balanced K-Means, Simulated Annealing TSP, and Adaptive Grid Partitioning.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import math
from simulation.common.clustering import size_balanced_kmeans, grid_partition
from simulation.common.tsp import nearest_neighbor_tsp, simulated_annealing_tsp, path_length


def test_size_balanced_kmeans():
    # 20 points, 4 clusters -> capacity = 5 points per cluster
    pois = [{"x": float(i * 10), "y": float(i * 10)} for i in range(20)]
    centers, clusters = size_balanced_kmeans(pois, k=4, max_iter=20)

    assert len(centers) == 4
    assert len(clusters) == 4
    total_assigned = sum(len(c) for c in clusters)
    assert total_assigned == 20

    # Check maximum cluster size does not exceed ceil(20/4) = 5
    for c in clusters:
        assert len(c) <= 5


def test_simulated_annealing_tsp():
    start = {"x": 0.0, "y": 0.0}
    # Square corners: optimal tour length is 400
    points = [{"x": 100.0, "y": 0.0}, {"x": 100.0, "y": 100.0}, {"x": 0.0, "y": 100.0}]

    nn_path = nearest_neighbor_tsp(start, points)
    sa_path = simulated_annealing_tsp(nn_path, max_iter=500)

    assert sa_path[0] == start
    assert sa_path[-1] == start
    assert len(sa_path) == 5  # start + 3 points + return start
    # Square perimeter is 400
    assert math.isclose(path_length(sa_path), 400.0, rel_tol=1e-3)


def test_grid_partition_4th_quadrant_coverage():
    # Points in all 4 quadrants, specifically including the 4th quadrant (bottom-right: x>500, y>500)
    pois = [
        {"x": 100.0, "y": 100.0, "id": "q2_top_left"},
        {"x": 800.0, "y": 100.0, "id": "q1_top_right"},
        {"x": 100.0, "y": 800.0, "id": "q3_bottom_left"},
        {"x": 850.0, "y": 850.0, "id": "q4_bottom_right"},  # 4th quadrant point
    ]

    for k in range(1, 9):
        centers, clusters = grid_partition(pois, num_regions=k, map_size=(1000, 1000))
        assert len(centers) == k
        assert len(clusters) == k
        assert sum(len(c) for c in clusters) == len(pois)

        q4_found = any(any(p["id"] == "q4_bottom_right" for p in c) for c in clusters)
        assert q4_found, f"4th quadrant point missed for k={k}"
