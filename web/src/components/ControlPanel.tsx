import React from 'react';
import { SimulationMode, FieldPreset } from '../types';

interface ControlPanelProps {
  mode: SimulationMode;
  onModeChange: (m: SimulationMode) => void;
  numBigDrones: number;
  onNumBigDronesChange: (val: number) => void;
  numSmallDrones: number;
  onNumSmallDronesChange: (val: number) => void;
  simSpeed: number;
  onSimSpeedChange: (val: number) => void;
  isPlaying: boolean;
  onTogglePlay: () => void;
  onStep: () => void;
  onReset: () => void;
  onApplyPreset: (preset: FieldPreset) => void;
  editMode: 'none' | 'poi';
  onEditModeChange: (em: 'none' | 'poi') => void;
}

export const PRESETS: FieldPreset[] = [
  {
    name: 'RTB Pine Infestation',
    description: 'Realistic pine grove affected by Red Turpentine Beetles (clustered canopy damage)',
    numPOIs: 45,
    clusteringDistribution: 'clustered'
  },
  {
    name: 'Dense Orchard',
    description: 'High-density grid of fruit trees requiring high coverage pathing',
    numPOIs: 80,
    clusteringDistribution: 'orchard'
  },
  {
    name: 'Uniform Field',
    description: 'Uniformly distributed anomalies across the field boundary',
    numPOIs: 40,
    clusteringDistribution: 'uniform'
  },
  {
    name: 'Sparse Outcrop',
    description: 'Scattered anomalies testing long-range cluster routing',
    numPOIs: 20,
    clusteringDistribution: 'uniform'
  }
];

export const ControlPanel: React.FC<ControlPanelProps> = ({
  mode,
  onModeChange,
  numBigDrones,
  onNumBigDronesChange,
  numSmallDrones,
  onNumSmallDronesChange,
  simSpeed,
  onSimSpeedChange,
  isPlaying,
  onTogglePlay,
  onStep,
  onReset,
  onApplyPreset,
  editMode,
  onEditModeChange
}) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl text-slate-200 flex flex-col gap-5">
      {/* Simulation Mode Toggle */}
      <div>
        <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-2">
          Architecture / Mode
        </label>
        <div className="grid grid-cols-3 gap-2">
          <button
            onClick={() => onModeChange('independent')}
            className={`py-2 px-3 text-xs font-semibold rounded-lg transition-colors border ${
              mode === 'independent'
                ? 'bg-sky-600 text-white border-sky-500 shadow-md'
                : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
            }`}
          >
            Independent
          </button>
          <button
            onClick={() => onModeChange('external')}
            className={`py-2 px-3 text-xs font-semibold rounded-lg transition-colors border ${
              mode === 'external'
                ? 'bg-amber-600 text-white border-amber-500 shadow-md'
                : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
            }`}
          >
            External (K-Means)
          </button>
          <button
            onClick={() => onModeChange('dual')}
            className={`py-2 px-3 text-xs font-semibold rounded-lg transition-colors border ${
              mode === 'dual'
                ? 'bg-purple-600 text-white border-purple-500 shadow-md'
                : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
            }`}
          >
            Side-by-Side Dual
          </button>
        </div>
      </div>

      {/* Fleet Configuration Sliders */}
      <div className="flex flex-col gap-4">
        <div>
          <div className="flex justify-between text-xs font-medium mb-1">
            <span className="text-slate-300">Big Leader Sprayers (k)</span>
            <span className="text-sky-400 font-mono font-bold">{numBigDrones}</span>
          </div>
          <input
            type="range"
            min={1}
            max={8}
            value={numBigDrones}
            onChange={e => onNumBigDronesChange(Number(e.target.value))}
            className="w-full accent-sky-500 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
          />
        </div>

        <div>
          <div className="flex justify-between text-xs font-medium mb-1">
            <span className="text-slate-300">Small Scout Sweepers (N)</span>
            <span className="text-sky-400 font-mono font-bold">{numSmallDrones}</span>
          </div>
          <input
            type="range"
            min={1}
            max={24}
            value={numSmallDrones}
            onChange={e => onNumSmallDronesChange(Number(e.target.value))}
            className="w-full accent-sky-500 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
          />
        </div>

        <div>
          <div className="flex justify-between text-xs font-medium mb-1">
            <span className="text-slate-300">Simulation Speed</span>
            <span className="text-sky-400 font-mono font-bold">{simSpeed}x</span>
          </div>
          <input
            type="range"
            min={0.5}
            max={4}
            step={0.5}
            value={simSpeed}
            onChange={e => onSimSpeedChange(Number(e.target.value))}
            className="w-full accent-sky-500 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
          />
        </div>
      </div>

      {/* Playback Controls */}
      <div className="flex items-center gap-2 pt-2 border-t border-slate-800">
        <button
          onClick={onTogglePlay}
          className={`flex-1 py-2.5 px-4 rounded-lg font-semibold text-sm transition-all shadow-md flex items-center justify-center gap-2 ${
            isPlaying
              ? 'bg-amber-500 hover:bg-amber-600 text-slate-950'
              : 'bg-emerald-500 hover:bg-emerald-600 text-slate-950'
          }`}
        >
          {isPlaying ? '⏸ Pause' : '▶ Simulate'}
        </button>
        <button
          onClick={onStep}
          disabled={isPlaying}
          className="py-2.5 px-3 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 rounded-lg text-sm font-semibold border border-slate-700"
          title="Single Step"
        >
          ⏭ Step
        </button>
        <button
          onClick={onReset}
          className="py-2.5 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-sm font-semibold border border-slate-700"
          title="Reset Simulation"
        >
          🔄 Reset
        </button>
      </div>

      {/* Presets */}
      <div>
        <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-2">
          Field Scenarios
        </label>
        <div className="grid grid-cols-2 gap-2">
          {PRESETS.map(p => (
            <button
              key={p.name}
              onClick={() => onApplyPreset(p)}
              className="py-2 px-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-left rounded-lg transition-colors"
            >
              <div className="text-xs font-semibold text-slate-200">{p.name}</div>
              <div className="text-[10px] text-slate-400 truncate">{p.numPOIs} POIs · {p.clusteringDistribution}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Canvas Editing Mode */}
      <div className="pt-2 border-t border-slate-800">
        <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-2">
          Interactive Tool
        </label>
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => onEditModeChange(editMode === 'poi' ? 'none' : 'poi')}
            className={`py-1.5 px-2 text-xs rounded-lg border font-medium transition-colors ${
              editMode === 'poi'
                ? 'bg-red-500 text-white border-red-400'
                : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
            }`}
          >
            + Add Tree POI
          </button>
          <button
            onClick={() => onEditModeChange('none')}
            className={`py-1.5 px-2 text-xs rounded-lg border font-medium transition-colors ${
              editMode === 'none'
                ? 'bg-slate-700 text-white border-slate-600'
                : 'bg-slate-800 text-slate-400 border-slate-700 hover:bg-slate-700'
            }`}
          >
            Pan / Inspect
          </button>
        </div>
      </div>
    </div>
  );
};
