import { Point, POI } from '../types';

export function euclideanDist(p1: Point, p2: Point): number {
  return Math.hypot(p1.x - p2.x, p1.y - p2.y);
}

/**
 * Size-Balanced K-Means clustering algorithm.
 * Enforces capacity constraint C = ceil(N / k) per cluster to ensure uniform
 * workload distribution and minimize overall makespan.
 */
export function sizeBalancedKMeans(
  pois: POI[],
  k: number,
  maxIter = 25
): { centers: Point[]; clusters: POI[][] } {
  if (pois.length === 0 || k <= 0) {
    return { centers: [], clusters: [] };
  }

  if (pois.length <= k) {
    const centers = pois.map(p => ({ x: p.x, y: p.y }));
    const clusters = pois.map(p => [p]);
    while (centers.length < k) {
      centers.push(centers[0] ? { ...centers[0] } : { x: 500, y: 500 });
      clusters.push([]);
    }
    return { centers, clusters };
  }

  // K-Means++ Initialization
  const centers: Point[] = [{ x: pois[0].x, y: pois[0].y }];
  for (let c = 1; c < k; c++) {
    const distSq = pois.map(p =>
      Math.min(...centers.map(center => euclideanDist(p, center) ** 2))
    );
    const totalDist = distSq.reduce((a, b) => a + b, 0);
    const r = Math.random() * totalDist;
    let cum = 0;
    let chosen = pois[pois.length - 1];
    for (let i = 0; i < pois.length; i++) {
      cum += distSq[i];
      if (r <= cum) {
        chosen = pois[i];
        break;
      }
    }
    centers.push({ x: chosen.x, y: chosen.y });
  }

  const capacity = Math.ceil(pois.length / k);
  let finalClusters: POI[][] = Array.from({ length: k }, () => []);

  for (let iter = 0; iter < maxIter; iter++) {
    // Generate all (poiIndex, centerIndex, distance) triplets
    const candidatePairs: { pIdx: number; cIdx: number; dist: number }[] = [];
    for (let p = 0; p < pois.length; p++) {
      for (let c = 0; c < k; c++) {
        candidatePairs.push({
          pIdx: p,
          cIdx: c,
          dist: euclideanDist(pois[p], centers[c])
        });
      }
    }

    // Greedy capacity assignment sorted by ascending distance
    candidatePairs.sort((a, b) => a.dist - b.dist);

    const assigned = new Set<number>();
    const clusters: POI[][] = Array.from({ length: k }, () => []);

    for (const pair of candidatePairs) {
      if (!assigned.has(pair.pIdx) && clusters[pair.cIdx].length < capacity) {
        assigned.add(pair.pIdx);
        clusters[pair.cIdx].push(pois[pair.pIdx]);
      }
    }

    // Residual assignment
    for (let p = 0; p < pois.length; p++) {
      if (!assigned.has(p)) {
        const leastLoaded = clusters
          .map((c, idx) => ({ count: c.length, idx }))
          .sort((a, b) => a.count - b.count)[0].idx;
        clusters[leastLoaded].push(pois[p]);
        assigned.add(p);
      }
    }

    // Update centroids
    let maxShift = 0;
    for (let c = 0; c < k; c++) {
      if (clusters[c].length > 0) {
        const avgX = clusters[c].reduce((sum, p) => sum + p.x, 0) / clusters[c].length;
        const avgY = clusters[c].reduce((sum, p) => sum + p.y, 0) / clusters[c].length;
        const shift = Math.hypot(centers[c].x - avgX, centers[c].y - avgY);
        if (shift > maxShift) maxShift = shift;
        centers[c] = { x: avgX, y: avgY };
      }
    }

    finalClusters = clusters;
    if (maxShift < 0.5) break;
  }

  return { centers, clusters: finalClusters };
}

/**
 * Grid Partitioning for Independent Mode.
 * Partitions the field into rows x cols rectangular tiles.
 */
export function gridPartition(
  pois: POI[],
  numRegions: number,
  mapWidth = 1000,
  mapHeight = 1000
): { regions: { x0: number; y0: number; x1: number; y1: number }[]; centers: Point[]; clusters: POI[][] } {
  if (numRegions <= 1) {
    const reg = { x0: 0, y0: 0, x1: mapWidth, y1: mapHeight };
    return {
      regions: [reg],
      centers: [{ x: mapWidth / 2, y: mapHeight / 2 }],
      clusters: [pois.slice()]
    };
  }

  // Adaptive row-by-row allocation ensuring 100% field coverage with zero dead zones
  const rows = Math.max(1, Math.round(Math.sqrt(numRegions)));
  const baseCols = Math.floor(numRegions / rows);
  const extra = numRegions % rows;

  const rowHeight = mapHeight / rows;
  const regions: { x0: number; y0: number; x1: number; y1: number }[] = [];
  const centers: Point[] = [];
  const clusters: POI[][] = Array.from({ length: numRegions }, () => []);

  let currentY = 0;
  for (let r = 0; r < rows; r++) {
    const colsInThisRow = baseCols + (r < extra ? 1 : 0);
    const colWidth = mapWidth / colsInThisRow;
    const y0 = currentY;
    const y1 = r === rows - 1 ? mapHeight : currentY + rowHeight;

    for (let c = 0; c < colsInThisRow; c++) {
      const x0 = c * colWidth;
      const x1 = c === colsInThisRow - 1 ? mapWidth : (c + 1) * colWidth;
      regions.push({ x0, y0, x1, y1 });
      centers.push({ x: (x0 + x1) / 2, y: (y0 + y1) / 2 });
    }
    currentY = y1;
  }

  for (const p of pois) {
    let assignedIdx = 0;
    for (let i = 0; i < regions.length; i++) {
      const reg = regions[i];
      if (p.x >= reg.x0 && p.x <= reg.x1 && p.y >= reg.y0 && p.y <= reg.y1) {
        assignedIdx = i;
        break;
      }
    }
    clusters[assignedIdx].push(p);
  }

  return { regions, centers, clusters };
}
