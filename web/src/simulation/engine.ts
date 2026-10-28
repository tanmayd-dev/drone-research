import { Point, POI, Obstacle, Drone, SimulationMode, SimulationTelemetry } from '../types';
import { AStarPathfinder } from './astar';
import { sizeBalancedKMeans, gridPartition } from './kmeans';
import { nearestNeighborTSP, simulatedAnnealingTSP, dist } from './tsp';

export interface SimulationParams {
  numBigDrones: number;
  numSmallDrones: number;
  droneSpeed: number;
  smallScanRadius: number;
  energyPerSecond: number;
  bigDroneTravelEnergyPerSec: number;
  energyPerAction: number;
  mapWidth: number;
  mapHeight: number;
}

const PALETTE = [
  '#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899', '#f97316', '#eab308', '#10b981', '#14b8a6'
];

export class SimulationEngine {
  public mode: SimulationMode;
  public params: SimulationParams;
  public pois: POI[];
  public obstacles: Obstacle[];
  public smallDrones: Drone[];
  public bigDrones: Drone[];
  public pathfinder: AStarPathfinder;
  public telemetry: SimulationTelemetry;
  public phase: 'survey' | 'action' | 'done';
  public elapsedTime: number;
  public regions: { x0: number; y0: number; x1: number; y1: number }[] = [];

  constructor(
    mode: SimulationMode,
    params: SimulationParams,
    pois: POI[],
    obstacles: Obstacle[]
  ) {
    this.mode = mode;
    this.params = params;
    this.pois = pois.map(p => ({ ...p, detected: false, actionTaken: false }));
    this.obstacles = obstacles;
    this.pathfinder = new AStarPathfinder(obstacles, params.mapWidth, params.mapHeight);
    this.phase = 'survey';
    this.elapsedTime = 0;

    this.telemetry = {
      totalEnergy: 0,
      surveyEnergy: 0,
      actionEnergy: 0,
      makespan: 0,
      totalDistance: 0,
      detectedCount: 0,
      servicedCount: 0,
      totalPOIs: pois.length
    };

    this.smallDrones = [];
    this.bigDrones = [];

    this.initializeDrones();
  }

  private generateSweepPath(
    region: { x0: number; y0: number; x1: number; y1: number },
    step: number
  ): Point[] {
    const path: Point[] = [];
    let x = region.x0 + Math.min(step / 2, (region.x1 - region.x0) / 2);
    let direction = 1;

    while (x <= region.x1) {
      if (direction === 1) {
        path.push({ x, y: region.y0 });
        path.push({ x, y: region.y1 });
      } else {
        path.push({ x, y: region.y1 });
        path.push({ x, y: region.y0 });
      }
      x += step;
      direction *= -1;
    }

    // Ensure the far boundary edge of the region is never left uncovered
    const rightEdge = region.x1 - Math.min(step / 3, 10);
    if (path.length > 0 && Math.abs(path[path.length - 1].x - rightEdge) > step / 2) {
      if (direction === 1) {
        path.push({ x: rightEdge, y: region.y0 });
        path.push({ x: rightEdge, y: region.y1 });
      } else {
        path.push({ x: rightEdge, y: region.y1 });
        path.push({ x: rightEdge, y: region.y0 });
      }
    }

    return path;
  }

  public initializeDrones(): void {
    const { numBigDrones, numSmallDrones, mapWidth, mapHeight, smallScanRadius, droneSpeed } = this.params;

    this.smallDrones = [];
    this.bigDrones = [];

    if (this.mode === 'independent') {
      const { regions, centers } = gridPartition(this.pois, numBigDrones, mapWidth, mapHeight);
      this.regions = regions;

      // Create Big Drones placed at centers of regional tiles
      for (let i = 0; i < numBigDrones; i++) {
        this.bigDrones.push({
          id: `big-${i}`,
          type: 'big',
          x: centers[i].x,
          y: centers[i].y,
          baseX: centers[i].x,
          baseY: centers[i].y,
          speed: droneSpeed,
          assignedRegion: i,
          path: [],
          pathIndex: 0,
          state: 'idle',
          energyConsumed: 0,
          distanceTraveled: 0,
          color: PALETTE[i % PALETTE.length],
          scanRadius: 0,
          trail: []
        });
      }

      // Distribute Small Drones among the Big Drones / regions
      const smallPerBig = Math.floor(numSmallDrones / numBigDrones);
      const rem = numSmallDrones % numBigDrones;

      let droneIdx = 0;
      for (let rIdx = 0; rIdx < numBigDrones; rIdx++) {
        const count = smallPerBig + (rIdx < rem ? 1 : 0);
        const region = regions[rIdx];
        const subW = (region.x1 - region.x0) / Math.max(1, count);

        for (let s = 0; s < count; s++) {
          const subX0 = region.x0 + s * subW;
          const subX1 = subX0 + subW;
          const sweep = this.generateSweepPath(
            { x0: subX0, y0: region.y0, x1: subX1, y1: region.y1 },
            smallScanRadius * 2
          );

          // Small drone starts and returns to the regional Big Drone depot
          const home = centers[rIdx];
          const fullPath = [home, ...sweep, home];

          this.smallDrones.push({
            id: `small-${droneIdx}`,
            type: 'small',
            x: home.x,
            y: home.y,
            baseX: home.x,
            baseY: home.y,
            speed: droneSpeed * 1.5,
            assignedRegion: rIdx,
            path: fullPath,
            pathIndex: 0,
            state: 'surveying',
            energyConsumed: 0,
            distanceTraveled: 0,
            color: PALETTE[rIdx % PALETTE.length],
            scanRadius: smallScanRadius,
            trail: []
          });
          droneIdx++;
        }
      }
    } else {
      // External Mode: Small drones launch from central controller depot
      const controllerDepot: Point = { x: mapWidth / 2, y: mapHeight / 2 };

      // Initialize Big Drones at central depot
      for (let i = 0; i < numBigDrones; i++) {
        this.bigDrones.push({
          id: `big-${i}`,
          type: 'big',
          x: controllerDepot.x,
          y: controllerDepot.y,
          baseX: controllerDepot.x,
          baseY: controllerDepot.y,
          speed: droneSpeed,
          assignedCluster: i,
          path: [],
          pathIndex: 0,
          state: 'idle',
          energyConsumed: 0,
          distanceTraveled: 0,
          color: PALETTE[i % PALETTE.length],
          scanRadius: 0,
          trail: []
        });
      }

      // Small Drones sweep vertical slices of the entire field
      const sliceW = mapWidth / Math.max(1, numSmallDrones);
      for (let s = 0; s < numSmallDrones; s++) {
        const sx0 = s * sliceW;
        const sx1 = sx0 + sliceW;
        const sweep = this.generateSweepPath(
          { x0: sx0, y0: 0, x1: sx1, y1: mapHeight },
          smallScanRadius * 2
        );

        const fullPath = [controllerDepot, ...sweep, controllerDepot];

        this.smallDrones.push({
          id: `small-${s}`,
          type: 'small',
          x: controllerDepot.x,
          y: controllerDepot.y,
          baseX: controllerDepot.x,
          baseY: controllerDepot.y,
          speed: droneSpeed * 1.5,
          path: fullPath,
          pathIndex: 0,
          state: 'surveying',
          energyConsumed: 0,
          distanceTraveled: 0,
          color: PALETTE[s % PALETTE.length],
          scanRadius: smallScanRadius,
          trail: []
        });
      }
    }
  }

  public planBigDroneTours(): void {
    const { mapWidth, mapHeight } = this.params;
    const detectedPOIs = this.pois.filter(p => p.detected);

    if (this.mode === 'independent') {
      const { clusters } = gridPartition(detectedPOIs, this.bigDrones.length, mapWidth, mapHeight);

      this.bigDrones.forEach((drone, idx) => {
        const cluster = clusters[idx] || [];
        cluster.forEach(p => (p.assignedBigDrone = idx));

        if (cluster.length > 0) {
          const rawTSP = nearestNeighborTSP({ x: drone.baseX, y: drone.baseY }, cluster);
          const saTSP = simulatedAnnealingTSP(rawTSP, 80, 0.95, 600);

          // Resolve obstacle avoidance via A* along tour
          const fullAvoidanceTour: Point[] = [];
          for (let step = 0; step < saTSP.length - 1; step++) {
            const seg = this.pathfinder.findPath(saTSP[step], saTSP[step + 1]);
            if (step > 0 && seg.length > 0) seg.shift();
            fullAvoidanceTour.push(...seg);
          }

          drone.path = fullAvoidanceTour;
          drone.pathIndex = 0;
          drone.state = 'acting';
        } else {
          drone.state = 'completed';
        }
      });
    } else {
      // External Mode: Size-Balanced K-Means
      const { clusters } = sizeBalancedKMeans(detectedPOIs, this.bigDrones.length);

      this.bigDrones.forEach((drone, idx) => {
        const cluster = clusters[idx] || [];
        cluster.forEach(p => (p.assignedBigDrone = idx));

        if (cluster.length > 0) {
          const rawTSP = nearestNeighborTSP({ x: drone.baseX, y: drone.baseY }, cluster);
          const saTSP = simulatedAnnealingTSP(rawTSP, 80, 0.95, 600);

          const fullAvoidanceTour: Point[] = [];
          for (let step = 0; step < saTSP.length - 1; step++) {
            const seg = this.pathfinder.findPath(saTSP[step], saTSP[step + 1]);
            if (step > 0 && seg.length > 0) seg.shift();
            fullAvoidanceTour.push(...seg);
          }

          drone.path = fullAvoidanceTour;
          drone.pathIndex = 0;
          drone.state = 'acting';
        } else {
          drone.state = 'completed';
        }
      });
    }

    this.phase = 'action';
  }

  public update(dt: number): void {
    if (this.phase === 'done') return;

    this.elapsedTime += dt;
    const { energyPerSecond, bigDroneTravelEnergyPerSec, energyPerAction } = this.params;

    // 1. Advance Small Drones
    if (this.phase === 'survey') {
      let allSmallDone = true;

      for (const drone of this.smallDrones) {
        if (drone.pathIndex < drone.path.length - 1) {
          allSmallDone = false;
          const target = drone.path[drone.pathIndex + 1];
          const d = dist(drone, target);
          const moveDist = drone.speed * dt * 40;

          if (d <= moveDist) {
            drone.x = target.x;
            drone.y = target.y;
            drone.pathIndex++;
            drone.distanceTraveled += d;
          } else {
            const angle = Math.atan2(target.y - drone.y, target.x - drone.x);
            drone.x += Math.cos(angle) * moveDist;
            drone.y += Math.sin(angle) * moveDist;
            drone.distanceTraveled += moveDist;
          }

          drone.energyConsumed += (moveDist / (drone.speed * 40)) * energyPerSecond;

          // Trail logging
          if (drone.trail.length === 0 || dist(drone, drone.trail[drone.trail.length - 1]) > 15) {
            drone.trail.push({ x: drone.x, y: drone.y });
            if (drone.trail.length > 60) drone.trail.shift();
          }

          // POI detection check
          for (const poi of this.pois) {
            if (!poi.detected && dist(drone, poi) <= drone.scanRadius) {
              poi.detected = true;
              this.telemetry.detectedCount++;
            }
          }
        } else {
          drone.state = 'completed';
        }
      }

      if (allSmallDone) {
        this.planBigDroneTours();
      }
    }

    // 2. Advance Big Drones
    if (this.phase === 'action') {
      let allBigDone = true;

      for (const drone of this.bigDrones) {
        if (drone.path.length > 0 && drone.pathIndex < drone.path.length - 1) {
          allBigDone = false;
          const target = drone.path[drone.pathIndex + 1];
          const d = dist(drone, target);
          const moveDist = drone.speed * dt * 45;

          if (d <= moveDist) {
            drone.x = target.x;
            drone.y = target.y;
            drone.pathIndex++;
            drone.distanceTraveled += d;

            // Check if arrived at a POI for spraying action
            for (const poi of this.pois) {
              if (poi.detected && !poi.actionTaken && dist(drone, poi) < 8) {
                poi.actionTaken = true;
                this.telemetry.servicedCount++;
                drone.energyConsumed += energyPerAction;
                this.telemetry.actionEnergy += energyPerAction;
              }
            }
          } else {
            const angle = Math.atan2(target.y - drone.y, target.x - drone.x);
            drone.x += Math.cos(angle) * moveDist;
            drone.y += Math.sin(angle) * moveDist;
            drone.distanceTraveled += moveDist;
          }

          const travelRate = this.mode === 'external' ? bigDroneTravelEnergyPerSec : energyPerSecond;
          drone.energyConsumed += (moveDist / (drone.speed * 45)) * travelRate;

          if (drone.trail.length === 0 || dist(drone, drone.trail[drone.trail.length - 1]) > 20) {
            drone.trail.push({ x: drone.x, y: drone.y });
            if (drone.trail.length > 80) drone.trail.shift();
          }
        } else {
          drone.state = 'completed';
        }
      }

      if (allBigDone) {
        this.phase = 'done';
      }
    }

    // 3. Compute telemetry
    const smallEnergy = this.smallDrones.reduce((sum, d) => sum + d.energyConsumed, 0);
    const bigEnergy = this.bigDrones.reduce((sum, d) => sum + d.energyConsumed, 0);
    const smallDist = this.smallDrones.reduce((sum, d) => sum + d.distanceTraveled, 0);
    const bigDist = this.bigDrones.reduce((sum, d) => sum + d.distanceTraveled, 0);

    this.telemetry.surveyEnergy = smallEnergy;
    this.telemetry.totalEnergy = smallEnergy + bigEnergy;
    this.telemetry.totalDistance = smallDist + bigDist;
    this.telemetry.makespan = this.elapsedTime;
  }
}
