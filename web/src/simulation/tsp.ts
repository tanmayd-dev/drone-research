import { Point } from '../types';

export function dist(p1: Point, p2: Point): number {
  return Math.hypot(p1.x - p2.x, p1.y - p2.y);
}

export function pathLength(path: Point[]): number {
  if (path.length < 2) return 0;
  let len = 0;
  for (let i = 0; i < path.length - 1; i++) {
    len += dist(path[i], path[i + 1]);
  }
  return len;
}

export function nearestNeighborTSP(start: Point, points: Point[]): Point[] {
  if (points.length === 0) return [{ ...start }, { ...start }];

  const unvisited = points.map(p => ({ ...p }));
  const path: Point[] = [{ ...start }];
  let curr = start;

  while (unvisited.length > 0) {
    let bestIdx = 0;
    let bestDist = Infinity;
    for (let i = 0; i < unvisited.length; i++) {
      const d = dist(curr, unvisited[i]);
      if (d < bestDist) {
        bestDist = d;
        bestIdx = i;
      }
    }
    const next = unvisited.splice(bestIdx, 1)[0];
    path.push(next);
    curr = next;
  }

  path.push({ ...start });
  return path;
}

export function simulatedAnnealingTSP(
  path: Point[],
  tInit = 100,
  alpha = 0.96,
  maxIter = 1000
): Point[] {
  const n = path.length;
  if (n <= 3) return path.map(p => ({ ...p }));

  let currentPath = path.map(p => ({ ...p }));
  let bestPath = path.map(p => ({ ...p }));
  let currentLen = pathLength(currentPath);
  let bestLen = currentLen;

  let t = tInit;

  for (let iter = 0; iter < maxIter; iter++) {
    if (t < 1e-4) break;

    // Pick 2 random cut points (preserving fixed start and return endpoints)
    const i = 1 + Math.floor(Math.random() * (n - 3));
    const j = i + 1 + Math.floor(Math.random() * (n - 2 - i));

    // 2-opt swap (reversing segment i..j)
    const candidate = [
      ...currentPath.slice(0, i),
      ...currentPath.slice(i, j + 1).reverse(),
      ...currentPath.slice(j + 1)
    ];

    const candidateLen = pathLength(candidate);
    const diff = candidateLen - currentLen;

    // Metropolis acceptance criterion
    if (diff < 0 || Math.random() < Math.exp(-diff / t)) {
      currentPath = candidate;
      currentLen = candidateLen;

      if (currentLen < bestLen) {
        bestPath = candidate.map(p => ({ ...p }));
        bestLen = currentLen;
      }
    }

    t *= alpha;
  }

  return bestPath;
}
