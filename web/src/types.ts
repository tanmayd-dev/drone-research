export interface Point {
  x: number;
  y: number;
}

export interface POI extends Point {
  id: string;
  detected: boolean;
  actionTaken: boolean;
  assignedBigDrone?: number;
  area?: number;
}

export type DroneType = 'small' | 'big';

export type DroneState = 'idle' | 'surveying' | 'dispatching' | 'acting' | 'returning' | 'completed';

export interface Drone {
  id: string;
  type: DroneType;
  x: number;
  y: number;
  baseX: number;
  baseY: number;
  speed: number;
  assignedRegion?: number;
  assignedCluster?: number;
  path: Point[];
  pathIndex: number;
  state: DroneState;
  energyConsumed: number;
  distanceTraveled: number;
  color: string;
  scanRadius: number;
  trail: Point[];
}

export type SimulationMode = 'independent' | 'external' | 'dual';

export interface SimulationTelemetry {
  totalEnergy: number;
  surveyEnergy: number;
  actionEnergy: number;
  makespan: number;
  totalDistance: number;
  detectedCount: number;
  servicedCount: number;
  totalPOIs: number;
}

export interface FieldPreset {
  name: string;
  description: string;
  numPOIs: number;
  clusteringDistribution: 'uniform' | 'clustered' | 'orchard';
}
