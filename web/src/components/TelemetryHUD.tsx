import React from 'react';
import { SimulationTelemetry, SimulationMode } from '../types';

interface TelemetryHUDProps {
  telemetry: SimulationTelemetry;
  mode: SimulationMode;
  secondaryTelemetry?: SimulationTelemetry; // For dual mode comparison
}

export const TelemetryHUD: React.FC<TelemetryHUDProps> = ({
  telemetry,
  mode,
  secondaryTelemetry
}) => {
  const energySavings = secondaryTelemetry
    ? ((secondaryTelemetry.totalEnergy - telemetry.totalEnergy) / Math.max(1, secondaryTelemetry.totalEnergy)) * 100
    : null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl text-slate-200">
      <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
          Telemetry & Energy Metrics
        </h3>
        {energySavings !== null && (
          <span
            className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${
              energySavings > 0
                ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                : 'bg-rose-950 text-rose-400 border border-rose-800'
            }`}
          >
            {energySavings > 0
              ? `Independent Saves ${Math.abs(energySavings).toFixed(1)}% Energy`
              : `External Saves ${Math.abs(energySavings).toFixed(1)}% Energy`}
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {/* Total Energy */}
        <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
          <div className="text-[11px] text-slate-400 font-medium">Total Energy</div>
          <div className="text-lg font-bold text-sky-400 font-mono mt-0.5">
            {Math.round(telemetry.totalEnergy).toLocaleString()}{' '}
            <span className="text-xs text-slate-500 font-sans">units</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-1">
            Survey: {Math.round(telemetry.surveyEnergy)} | Action: {Math.round(telemetry.actionEnergy)}
          </div>
        </div>

        {/* Mission Makespan */}
        <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
          <div className="text-[11px] text-slate-400 font-medium">Makespan (Time)</div>
          <div className="text-lg font-bold text-amber-400 font-mono mt-0.5">
            {telemetry.makespan.toFixed(1)}{' '}
            <span className="text-xs text-slate-500 font-sans">sec</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-1">
            Max drone flight duration
          </div>
        </div>

        {/* Total Distance */}
        <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
          <div className="text-[11px] text-slate-400 font-medium">Flight Distance</div>
          <div className="text-lg font-bold text-purple-400 font-mono mt-0.5">
            {Math.round(telemetry.totalDistance).toLocaleString()}{' '}
            <span className="text-xs text-slate-500 font-sans">px</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-1">
            Cumulative swarm travel
          </div>
        </div>

        {/* POIs Serviced */}
        <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
          <div className="text-[11px] text-slate-400 font-medium">POIs Actioned</div>
          <div className="text-lg font-bold text-emerald-400 font-mono mt-0.5">
            {telemetry.servicedCount}{' '}
            <span className="text-xs text-slate-500 font-sans">/ {telemetry.totalPOIs}</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-1">
            Detected: {telemetry.detectedCount}
          </div>
        </div>
      </div>

      {mode === 'dual' && secondaryTelemetry && (
        <div className="mt-3 pt-3 border-t border-slate-800 text-xs text-slate-400 flex flex-wrap gap-4">
          <div>
            <span className="text-slate-500">Independent Energy:</span>{' '}
            <strong className="text-slate-200">{Math.round(telemetry.totalEnergy).toLocaleString()}</strong>
          </div>
          <div>
            <span className="text-slate-500">External Energy:</span>{' '}
            <strong className="text-slate-200">{Math.round(secondaryTelemetry.totalEnergy).toLocaleString()}</strong>
          </div>
          <div>
            <span className="text-slate-500">Transit Energy Disparity:</span>{' '}
            <strong className="text-amber-400">
              {Math.abs(Math.round(secondaryTelemetry.surveyEnergy - telemetry.surveyEnergy)).toLocaleString()}
            </strong>
          </div>
        </div>
      )}
    </div>
  );
};
