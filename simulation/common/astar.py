"""
Grid-based A* Obstacle-Avoidance Pathfinder with Line-of-Sight Shortcut Smoothing.
Resolves conflict-free flight paths around circular obstacles for agricultural UAV routing.
"""

import math
import heapq
from typing import List, Tuple, Dict, Any, Optional


def circle_line_intersect(
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    circle_center: Tuple[float, float],
    radius: float
) -> bool:
    """
    Checks if line segment p1->p2 intersects or passes within radius of circle_center.
    """
    x1, y1 = p1
    x2, y2 = p2
    cx, cy = circle_center

    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:
        return math.hypot(x1 - cx, y1 - cy) <= radius

    # Projection factor t of circle_center onto line segment p1->p2
    t = ((cx - x1) * dx + (cy - y1) * dy) / (dx * dx + dy * dy)
    t_clamped = max(0.0, min(1.0, t))

    closest_x = x1 + t_clamped * dx
    closest_y = y1 + t_clamped * dy

    dist = math.hypot(cx - closest_x, cy - closest_y)
    return dist < radius


class AStarPathfinder:
    """
    A* search on a discretized grid representing the agricultural field.
    Navigates around circular obstacles and applies line-of-sight string pulling.
    """
    def __init__(
        self,
        obstacles: List[Dict[str, Any]],
        map_size: Tuple[int, int] = (1000, 1000),
        grid_resolution: int = 20,
        safety_clearance: float = 5.0
    ):
        self.obstacles = obstacles
        self.map_w, self.map_h = map_size
        self.res = grid_resolution
        self.clearance = safety_clearance

        self.cols = math.ceil(self.map_w / self.res) + 1
        self.rows = math.ceil(self.map_h / self.res) + 1

    def is_collision_free_line(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> bool:
        """
        Returns True if straight line from p1 to p2 does not intersect any obstacle.
        """
        for obs in self.obstacles:
            center = (obs["x"], obs["y"])
            eff_radius = obs.get("radius", 20.0) + self.clearance
            if circle_line_intersect(p1, p2, center, eff_radius):
                return False
        return True

    def is_point_valid(self, x: float, y: float) -> bool:
        """
        Checks if point is within map bounds and outside all obstacles.
        """
        if not (0 <= x <= self.map_w and 0 <= y <= self.map_h):
            return False
        for obs in self.obstacles:
            eff_radius = obs.get("radius", 20.0) + self.clearance
            if math.hypot(x - obs["x"], y - obs["y"]) <= eff_radius:
                return False
        return True

    def find_path(
        self,
        start: Dict[str, float],
        goal: Dict[str, float]
    ) -> List[Dict[str, float]]:
        """
        Computes shortest obstacle-free path between start and goal.
        Applies line-of-sight shortcutting to eliminate unnecessary grid hops.
        """
        p_start = (start["x"], start["y"])
        p_goal = (goal["x"], goal["y"])

        # Quick check: if direct line-of-sight is clear, return straight line
        if self.is_collision_free_line(p_start, p_goal):
            return [start, goal]

        # Convert to grid coordinates
        start_gx = round(p_start[0] / self.res)
        start_gy = round(p_start[1] / self.res)
        goal_gx = round(p_goal[0] / self.res)
        goal_gy = round(p_goal[1] / self.res)

        # 8-connectivity grid moves: (dx, dy, cost)
        moves = [
            (1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
            (1, 1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (-1, -1, 1.414)
        ]

        open_set: List[Tuple[float, float, int, int]] = []
        heapq.heappush(open_set, (0.0, 0.0, start_gx, start_gy))

        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
        g_score: Dict[Tuple[int, int], float] = {(start_gx, start_gy): 0.0}

        def heuristic(gx: int, gy: int) -> float:
            return math.hypot(gx - goal_gx, gy - goal_gy)

        found = False
        while open_set:
            _, current_g, cgx, cgy = heapq.heappop(open_set)

            if (cgx, cgy) == (goal_gx, goal_gy):
                found = True
                break

            if current_g > g_score.get((cgx, cgy), float('inf')):
                continue

            for dx, dy, step_cost in moves:
                ngx, ngy = cgx + dx, cgy + dy
                wx, wy = ngx * self.res, ngy * self.res

                if not self.is_point_valid(wx, wy):
                    continue

                tentative_g = current_g + step_cost
                if tentative_g < g_score.get((ngx, ngy), float('inf')):
                    g_score[(ngx, ngy)] = tentative_g
                    f_score = tentative_g + heuristic(ngx, ngy)
                    came_from[(ngx, ngy)] = (cgx, cgy)
                    heapq.heappush(open_set, (f_score, tentative_g, ngx, ngy))

        # Reconstruct path
        raw_waypoints = []
        if found:
            curr = (goal_gx, goal_gy)
            while curr in came_from:
                raw_waypoints.append({"x": float(curr[0] * self.res), "y": float(curr[1] * self.res)})
                curr = came_from[curr]
            raw_waypoints.reverse()
        else:
            # Fallback direct path if grid search was exhausted
            raw_waypoints = [goal]

        full_path = [start] + raw_waypoints + [goal]

        # String-pulling / line-of-sight smoothing
        smoothed = [full_path[0]]
        idx = 0
        while idx < len(full_path) - 1:
            next_idx = idx + 1
            # Look as far ahead as possible with direct line-of-sight
            for test_idx in range(len(full_path) - 1, idx, -1):
                pt_a = (smoothed[-1]["x"], smoothed[-1]["y"])
                pt_b = (full_path[test_idx]["x"], full_path[test_idx]["y"])
                if self.is_collision_free_line(pt_a, pt_b):
                    next_idx = test_idx
                    break
            smoothed.append(full_path[next_idx])
            idx = next_idx

        return smoothed
