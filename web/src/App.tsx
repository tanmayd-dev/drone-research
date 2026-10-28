import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { SimulationEngine, SimulationParams } from './simulation/engine';
import { SimulationCanvas } from './components/SimulationCanvas';
import { ControlPanel } from './components/ControlPanel';
import { TelemetryHUD } from './components/TelemetryHUD';
import { VisionExplorer } from './components/VisionExplorer';
import { DashboardsViewer } from './components/DashboardsViewer';
import { Point, POI, Obstacle, SimulationMode, FieldPreset } from './types';

function generateInitialPOIs(count: number, distribution: 'uniform' | 'clustered' | 'orchard' = 'clustered'): POI[] {
  const pois: POI[] = [];
  if (distribution === 'clustered') {
    // 3 infestation cluster epicenters
    const clusters = [
      { x: 300, y: 350 },
      { x: 700, y: 300 },
      { x: 500, y: 750 }
    ];
    for (let i = 0; i < count; i++) {
      const c = clusters[i % clusters.length];
      const r = Math.random() * 120;
      const theta = Math.random() * Math.PI * 2;
      pois.push({
        id: `poi-${i}`,
        x: Math.max(30, Math.min(970, c.x + r * Math.cos(theta))),
        y: Math.max(30, Math.min(970, c.y + r * Math.sin(theta))),
        detected: false,
        actionTaken: false
      });
    }
  } else if (distribution === 'orchard') {
    const spacing = 75;
    let idx = 0;
    for (let y = 100; y <= 900 && idx < count; y += spacing) {
      for (let x = 100; x <= 900 && idx < count; x += spacing) {
        pois.push({
          id: `poi-${idx++}`,
          x: x + (Math.random() * 16 - 8),
          y: y + (Math.random() * 16 - 8),
          detected: false,
          actionTaken: false
        });
      }
    }
  } else {
    for (let i = 0; i < count; i++) {
      pois.push({
        id: `poi-${i}`,
        x: 50 + Math.random() * 900,
        y: 50 + Math.random() * 900,
        detected: false,
        actionTaken: false
      });
    }
  }
  return pois;
}

function generateInitialObstacles(count: number): Obstacle[] {
  const obstacles: Obstacle[] = [];
  const coords = [
    { x: 500, y: 500, r: 45 },
    { x: 250, y: 250, r: 35 },
    { x: 750, y: 700, r: 40 },
    { x: 750, y: 250, r: 30 },
    { x: 250, y: 750, r: 35 },
    { x: 450, y: 200, r: 25 },
    { x: 600, y: 800, r: 30 }
  ];

  for (let i = 0; i < Math.min(count, coords.length); i++) {
    obstacles.push({
      id: `obs-${i}`,
      x: coords[i].x,
      y: coords[i].y,
      radius: coords[i].r
    });
  }

  while (obstacles.length < count) {
    obstacles.push({
      id: `obs-${obstacles.length}`,
      x: 100 + Math.random() * 800,
      y: 100 + Math.random() * 800,
      radius: 20 + Math.random() * 25
    });
  }

  return obstacles;
}

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'sim' | 'vision' | 'dashboards'>('sim');
  const [mode, setMode] = useState<SimulationMode>('dual');
  const [numBigDrones, setNumBigDrones] = useState<number>(3);
  const [numSmallDrones, setNumSmallDrones] = useState<number>(6);
  const [simSpeed, setSimSpeed] = useState<number>(1.5);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [editMode, setEditMode] = useState<'none' | 'poi' | 'obstacle'>('none');

  const [pois, setPois] = useState<POI[]>(() => generateInitialPOIs(45, 'clustered'));
  const [obstacles, setObstacles] = useState<Obstacle[]>(() => generateInitialObstacles(6));

  const params: SimulationParams = useMemo(() => ({
    numBigDrones,
    numSmallDrones,
    droneSpeed: 2.2,
    smallScanRadius: 28,
    energyPerSecond: 10,
    bigDroneTravelEnergyPerSec: 20,
    energyPerAction: 50,
    mapWidth: 1000,
    mapHeight: 1000
  }), [numBigDrones, numSmallDrones]);

  // Engines for simulation
  const [engineIndep, setEngineIndep] = useState<SimulationEngine>(
    () => new SimulationEngine('independent', params, pois, obstacles)
  );
  const [engineExt, setEngineExt] = useState<SimulationEngine>(
    () => new SimulationEngine('external', params, pois, obstacles)
  );

  const resetSimulation = useCallback(() => {
    setEngineIndep(new SimulationEngine('independent', params, pois, obstacles));
    setEngineExt(new SimulationEngine('external', params, pois, obstacles));
  }, [params, pois, obstacles]);

  // Handle configuration changes
  useEffect(() => {
    resetSimulation();
  }, [resetSimulation]);

  // Animation frame simulation tick
  const lastTimeRef = useRef<number>(performance.now());
  useEffect(() => {
    let animId: number;

    const tick = (now: number) => {
      const dt = Math.min(0.05, (now - lastTimeRef.current) / 1000);
      lastTimeRef.current = now;

      if (isPlaying) {
        if (mode === 'independent' || mode === 'dual') {
          engineIndep.update(dt * simSpeed);
        }
        if (mode === 'external' || mode === 'dual') {
          engineExt.update(dt * simSpeed);
        }
      }

      animId = requestAnimationFrame(tick);
    };

    animId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animId);
  }, [isPlaying, simSpeed, mode, engineIndep, engineExt]);

  const handleStep = () => {
    if (mode === 'independent' || mode === 'dual') engineIndep.update(0.05 * simSpeed);
    if (mode === 'external' || mode === 'dual') engineExt.update(0.05 * simSpeed);
  };

  const handleAddPOI = (pt: Point) => {
    const newPoi: POI = {
      id: `poi-${Date.now()}`,
      x: pt.x,
      y: pt.y,
      detected: false,
      actionTaken: false
    };
    setPois(prev => [...prev, newPoi]);
  };

  const handleAddObstacle = (pt: Point) => {
    const newObs: Obstacle = {
      id: `obs-${Date.now()}`,
      x: pt.x,
      y: pt.y,
      radius: 30
    };
    setObstacles(prev => [...prev, newObs]);
  };

  const handleApplyPreset = (preset: FieldPreset) => {
    const newPois = generateInitialPOIs(
      preset.numPOIs,
      preset.clusteringDistribution === 'orchard' ? 'orchard' :
      preset.clusteringDistribution === 'clustered' ? 'clustered' : 'uniform'
    );
    const newObs = generateInitialObstacles(preset.numObstacles);
    setPois(newPois);
    setObstacles(newObs);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-sky-500 selection:text-white">
      {/* Top Navbar */}
      <header className="border-b border-slate-800/80 bg-slate-900/90 backdrop-blur sticky top-0 z-30 px-4 lg:px-8 py-3.5">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center font-bold text-white shadow-md shadow-sky-500/20 text-sm">
              🚁
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-base tracking-tight text-white">Precision Drone Fleet Simulator</span>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-sky-950 text-sky-400 border border-sky-800">
                  Swarm Intelligence
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Heterogeneous Two-Tier Multi-UAV Swarm Routing</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex items-center gap-1.5 bg-slate-950/80 p-1 rounded-xl border border-slate-800 text-xs font-medium">
            <button
              onClick={() => setActiveTab('sim')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                activeTab === 'sim'
                  ? 'bg-sky-600 text-white font-semibold shadow'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              🎮 Live Simulation
            </button>
            <button
              onClick={() => setActiveTab('vision')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                activeTab === 'vision'
                  ? 'bg-sky-600 text-white font-semibold shadow'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              🔬 Vision Pipeline (VQ-VAE)
            </button>
            <button
              onClick={() => setActiveTab('dashboards')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                activeTab === 'dashboards'
                  ? 'bg-sky-600 text-white font-semibold shadow'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              📊 Energy Dashboards (28)
            </button>
          </nav>

          <div className="flex items-center gap-2">
            <a
              href="https://github.com/tanmayd-dev/drone-research"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium transition-colors border border-slate-700 flex items-center gap-1.5"
            >
              <span>GitHub</span>
              <span className="text-slate-500">↗</span>
            </a>
          </div>
        </div>
      </header>

      {/* Main Content Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 lg:p-6">
        {activeTab === 'sim' && (
          <div className="flex flex-col gap-5">
            {/* Telemetry HUD */}
            <TelemetryHUD
              telemetry={mode === 'external' ? engineExt.telemetry : engineIndep.telemetry}
              mode={mode}
              secondaryTelemetry={mode === 'dual' ? engineExt.telemetry : undefined}
            />

            {/* Layout: Canvases + Control Panel */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
              {/* Canvases */}
              <div className={mode === 'dual' ? 'lg:col-span-8 flex flex-col md:flex-row gap-4' : 'lg:col-span-8 flex justify-center'}>
                {mode === 'independent' && (
                  <SimulationCanvas
                    engine={engineIndep}
                    title="Independent Mode (Decentralized Grid Partitioning)"
                    editMode={editMode}
                    onAddPOI={handleAddPOI}
                    onAddObstacle={handleAddObstacle}
                    width={580}
                    height={580}
                  />
                )}

                {mode === 'external' && (
                  <SimulationCanvas
                    engine={engineExt}
                    title="External Mode (Centralized Size-Balanced K-Means)"
                    editMode={editMode}
                    onAddPOI={handleAddPOI}
                    onAddObstacle={handleAddObstacle}
                    width={580}
                    height={580}
                  />
                )}

                {mode === 'dual' && (
                  <>
                    <div className="flex-1">
                      <SimulationCanvas
                        engine={engineIndep}
                        title="Independent Mode (Grid)"
                        editMode={editMode}
                        onAddPOI={handleAddPOI}
                        onAddObstacle={handleAddObstacle}
                        width={370}
                        height={370}
                      />
                    </div>
                    <div className="flex-1">
                      <SimulationCanvas
                        engine={engineExt}
                        title="External Mode (K-Means)"
                        editMode={editMode}
                        onAddPOI={handleAddPOI}
                        onAddObstacle={handleAddObstacle}
                        width={370}
                        height={370}
                      />
                    </div>
                  </>
                )}
              </div>

              {/* Side Control Panel */}
              <div className="lg:col-span-4">
                <ControlPanel
                  mode={mode}
                  onModeChange={setMode}
                  numBigDrones={numBigDrones}
                  onNumBigDronesChange={setNumBigDrones}
                  numSmallDrones={numSmallDrones}
                  onNumSmallDronesChange={setNumSmallDrones}
                  simSpeed={simSpeed}
                  onSimSpeedChange={setSimSpeed}
                  isPlaying={isPlaying}
                  onTogglePlay={() => setIsPlaying(p => !p)}
                  onStep={handleStep}
                  onReset={resetSimulation}
                  onApplyPreset={handleApplyPreset}
                  editMode={editMode}
                  onEditModeChange={setEditMode}
                />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'vision' && <VisionExplorer />}
        {activeTab === 'dashboards' && <DashboardsViewer />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 px-6 text-center text-xs text-slate-500">
        <div>
          Autonomous Heterogeneous Drone Fleet Simulation & Deep Anomaly Detection.
        </div>
      </footer>
    </div>
  );
};
