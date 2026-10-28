import { Point, Obstacle } from '../types';

export function circleLineIntersect(
  p1: Point,
  p2: Point,
  circle: Point,
  radius: number
): boolean {
  const dx = p2.x - p1.x;
  const dy = p2.y - p1.y;

  if (dx === 0 && dy === 0) {
    return Math.hypot(p1.x - circle.x, p1.y - circle.y) <= radius;
  }

  const t = ((circle.x - p1.x) * dx + (circle.y - p1.y) * dy) / (dx * dx + dy * dy);
  const tClamped = Math.max(0, Math.min(1, t));

  const closestX = p1.x + tClamped * dx;
  const closestY = p1.y + tClamped * dy;

  return Math.hypot(circle.x - closestX, circle.y - closestY) < radius;
}

export class AStarPathfinder {
  private obstacles: Obstacle[];
  private mapWidth: number;
  private mapHeight: number;
  private resolution: number;
  private safetyClearance: number;

  constructor(
    obstacles: Obstacle[],
    mapWidth = 1000,
    mapHeight = 1000,
    resolution = 25,
    safetyClearance = 6
  ) {
    this.obstacles = obstacles;
    this.mapWidth = mapWidth;
    this.mapHeight = mapHeight;
    this.resolution = resolution;
    this.safetyClearance = safetyClearance;
  }

  public isLineCollisionFree(p1: Point, p2: Point): boolean {
    for (const obs of this.obstacles) {
      if (circleLineIntersect(p1, p2, obs, obs.radius + this.safetyClearance)) {
        return false;
      }
    }
    return true;
  }

  public isPointValid(x: number, y: number): boolean {
    if (x < 0 || x > this.mapWidth || y < 0 || y > this.mapHeight) return false;
    for (const obs of this.obstacles) {
      if (Math.hypot(x - obs.x, y - obs.y) <= obs.radius + this.safetyClearance) {
        return false;
      }
    }
    return true;
  }

  public findPath(start: Point, goal: Point): Point[] {
    // If straight line is clear, return direct line immediately
    if (this.isLineCollisionFree(start, goal)) {
      return [{ ...start }, { ...goal }];
    }

    const startGx = Math.round(start.x / this.resolution);
    const startGy = Math.round(start.y / this.resolution);
    const goalGx = Math.round(goal.x / this.resolution);
    const goalGy = Math.round(goal.y / this.resolution);

    const moves = [
      { dx: 1, dy: 0, cost: 1.0 },
      { dx: -1, dy: 0, cost: 1.0 },
      { dx: 0, dy: 1, cost: 1.0 },
      { dx: 0, dy: -1, cost: 1.0 },
      { dx: 1, dy: 1, cost: 1.414 },
      { dx: -1, dy: 1, cost: 1.414 },
      { dx: 1, dy: -1, cost: 1.414 },
      { dx: -1, dy: -1, cost: 1.414 },
    ];

    const openSet: { gx: number; gy: number; f: number; g: number }[] = [
      { gx: startGx, gy: startGy, f: 0, g: 0 }
    ];
    const cameFrom = new Map<string, { gx: number; gy: number }>();
    const gScore = new Map<string, number>();

    const key = (gx: number, gy: number) => `${gx},${gy}`;
    gScore.set(key(startGx, startGy), 0);

    const heuristic = (gx: number, gy: number) =>
      Math.hypot(gx - goalGx, gy - goalGy);

    let found = false;
    let iterations = 0;
    const maxIterations = 2500;

    while (openSet.length > 0 && iterations < maxIterations) {
      iterations++;
      // Pop lowest f score
      openSet.sort((a, b) => a.f - b.f);
      const current = openSet.shift()!;

      if (current.gx === goalGx && current.gy === goalGy) {
        found = true;
        break;
      }

      const currKey = key(current.gx, current.gy);
      if (current.g > (gScore.get(currKey) ?? Infinity)) continue;

      for (const m of moves) {
        const ngx = current.gx + m.dx;
        const ngy = current.gy + m.dy;
        const wx = ngx * this.resolution;
        const wy = ngy * this.resolution;

        if (!this.isPointValid(wx, wy)) continue;

        const nKey = key(ngx, ngy);
        const tentativeG = current.g + m.cost;

        if (tentativeG < (gScore.get(nKey) ?? Infinity)) {
          gScore.set(nKey, tentativeG);
          cameFrom.set(nKey, { gx: current.gx, gy: current.gy });
          const f = tentativeG + heuristic(ngx, ngy);
          openSet.push({ gx: ngx, gy: ngy, f, g: tentativeG });
        }
      }
    }

    const waypoints: Point[] = [];
    if (found) {
      let curr = { gx: goalGx, gy: goalGy };
      while (cameFrom.has(key(curr.gx, curr.gy))) {
        waypoints.push({ x: curr.gx * this.resolution, y: curr.gy * this.resolution });
        curr = cameFrom.get(key(curr.gx, curr.gy))!;
      }
      waypoints.reverse();
    } else {
      waypoints.push({ ...goal });
    }

    const fullPath = [{ ...start }, ...waypoints, { ...goal }];

    // String-pulling / Line-of-sight shortcutting
    const smoothed: Point[] = [fullPath[0]];
    let idx = 0;
    while (idx < fullPath.length - 1) {
      let nextIdx = idx + 1;
      for (let testIdx = fullPath.length - 1; testIdx > idx; testIdx--) {
        if (this.isLineCollisionFree(smoothed[smoothed.length - 1], fullPath[testIdx])) {
          nextIdx = testIdx;
          break;
        }
      }
      smoothed.push(fullPath[nextIdx]);
      idx = nextIdx;
    }

    return smoothed;
  }
}
