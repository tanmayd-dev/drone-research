import React, { useRef, useEffect } from 'react';
import { SimulationEngine } from '../simulation/engine';
import { Point } from '../types';

interface SimulationCanvasProps {
  engine: SimulationEngine;
  onAddPOI?: (p: Point) => void;
  onAddObstacle?: (p: Point) => void;
  editMode: 'none' | 'poi' | 'obstacle';
  title?: string;
  width?: number;
  height?: number;
}

export const SimulationCanvas: React.FC<SimulationCanvasProps> = ({
  engine,
  onAddPOI,
  onAddObstacle,
  editMode,
  title,
  width = 650,
  height = 650
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      const scaleX = width / engine.params.mapWidth;
      const scaleY = height / engine.params.mapHeight;

      // 1. Draw Field Background Grid (Farmland texture)
      ctx.fillStyle = '#0f172a'; // Deep slate
      ctx.fillRect(0, 0, width, height);

      // Farmland grid pattern
      ctx.strokeStyle = '#1e293b';
      ctx.lineWidth = 1;
      const step = 50 * scaleX;
      for (let x = 0; x < width; x += step) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += step) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // 2. Mode Regions / Partitions
      if (engine.mode === 'independent' && engine.regions.length > 0) {
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.35)';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([4, 4]);

        for (const reg of engine.regions) {
          ctx.strokeRect(
            reg.x0 * scaleX,
            reg.y0 * scaleY,
            (reg.x1 - reg.x0) * scaleX,
            (reg.y1 - reg.y0) * scaleY
          );
        }
        ctx.setLineDash([]);
      }

      // 3. Draw Obstacles (Circular terrain anomalies / trees / pylons)
      for (const obs of engine.obstacles) {
        const ox = obs.x * scaleX;
        const oy = obs.y * scaleY;
        const or = obs.radius * scaleX;

        // Clearance zone halo
        ctx.beginPath();
        ctx.arc(ox, oy, or + 6 * scaleX, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(239, 68, 68, 0.08)';
        ctx.fill();
        ctx.strokeStyle = 'rgba(239, 68, 68, 0.3)';
        ctx.setLineDash([2, 2]);
        ctx.stroke();
        ctx.setLineDash([]);

        // Main obstacle body
        ctx.beginPath();
        ctx.arc(ox, oy, or, 0, Math.PI * 2);
        const grad = ctx.createRadialGradient(ox, oy, 2, ox, oy, or);
        grad.addColorStop(0, '#7f1d1d');
        grad.addColorStop(1, '#450a0a');
        ctx.fillStyle = grad;
        ctx.fill();
        ctx.strokeStyle = '#ef4444';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Warning hash
        ctx.fillStyle = '#fca5a5';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('⚠', ox, oy);
      }

      // 4. Draw Big Drone Tour Trajectories
      for (const drone of engine.bigDrones) {
        if (drone.path.length > 1) {
          ctx.beginPath();
          ctx.strokeStyle = drone.color;
          ctx.lineWidth = 2;
          ctx.setLineDash([6, 3]);

          const p0 = drone.path[0];
          ctx.moveTo(p0.x * scaleX, p0.y * scaleY);
          for (let i = 1; i < drone.path.length; i++) {
            const p = drone.path[i];
            ctx.lineTo(p.x * scaleX, p.y * scaleY);
          }
          ctx.stroke();
          ctx.setLineDash([]);
        }
      }

      // 5. Draw POIs (Points of Interest / Damaged Canopies)
      for (const poi of engine.pois) {
        const px = poi.x * scaleX;
        const py = poi.y * scaleY;

        if (poi.actionTaken) {
          // Serviced / Sprayed
          ctx.beginPath();
          ctx.arc(px, py, 5, 0, Math.PI * 2);
          ctx.fillStyle = '#10b981';
          ctx.fill();
          ctx.strokeStyle = '#34d399';
          ctx.lineWidth = 1.5;
          ctx.stroke();
        } else if (poi.detected) {
          // Detected: pulsating beacon
          ctx.beginPath();
          ctx.arc(px, py, 7, 0, Math.PI * 2);
          ctx.fillStyle = 'rgba(239, 68, 68, 0.35)';
          ctx.fill();

          ctx.beginPath();
          ctx.arc(px, py, 4, 0, Math.PI * 2);
          ctx.fillStyle = '#ef4444';
          ctx.fill();
          ctx.strokeStyle = '#fca5a5';
          ctx.lineWidth = 1;
          ctx.stroke();
        } else {
          // Undetected hidden canopy anomaly
          ctx.beginPath();
          ctx.arc(px, py, 3, 0, Math.PI * 2);
          ctx.fillStyle = 'rgba(148, 163, 184, 0.4)';
          ctx.fill();
        }
      }

      // 6. Draw Small Scout Drones
      for (const drone of engine.smallDrones) {
        if (drone.state !== 'completed') {
          const dx = drone.x * scaleX;
          const dy = drone.y * scaleY;

          // Scanning cone/radar
          ctx.beginPath();
          ctx.arc(dx, dy, drone.scanRadius * scaleX, 0, Math.PI * 2);
          ctx.fillStyle = 'rgba(56, 189, 248, 0.12)';
          ctx.fill();
          ctx.strokeStyle = 'rgba(56, 189, 248, 0.4)';
          ctx.lineWidth = 1;
          ctx.stroke();

          // Scout body
          ctx.beginPath();
          ctx.arc(dx, dy, 4.5, 0, Math.PI * 2);
          ctx.fillStyle = '#38bdf8';
          ctx.fill();
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }

      // 7. Draw Big Leader Sprayer Drones
      for (const drone of engine.bigDrones) {
        const dx = drone.x * scaleX;
        const dy = drone.y * scaleY;

        // Base station marker
        ctx.beginPath();
        ctx.arc(drone.baseX * scaleX, drone.baseY * scaleY, 6, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(249, 115, 22, 0.2)';
        ctx.fill();
        ctx.strokeStyle = drone.color;
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Big drone hexacopter icon
        ctx.beginPath();
        ctx.arc(dx, dy, 8, 0, Math.PI * 2);
        ctx.fillStyle = drone.color;
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Rotor arms
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(dx - 10, dy - 10);
        ctx.lineTo(dx + 10, dy + 10);
        ctx.moveTo(dx + 10, dy - 10);
        ctx.lineTo(dx - 10, dy + 10);
        ctx.stroke();
      }

      animId = requestAnimationFrame(render);
    };

    render();

    return () => cancelAnimationFrame(animId);
  }, [engine, width, height]);

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const clickX = ((e.clientX - rect.left) / width) * engine.params.mapWidth;
    const clickY = ((e.clientY - rect.top) / height) * engine.params.mapHeight;

    if (editMode === 'poi' && onAddPOI) {
      onAddPOI({ x: clickX, y: clickY });
    } else if (editMode === 'obstacle' && onAddObstacle) {
      onAddObstacle({ x: clickX, y: clickY });
    }
  };

  return (
    <div className="flex flex-col items-center bg-slate-900 border border-slate-800 rounded-xl p-3 shadow-xl">
      {title && (
        <div className="flex items-center justify-between w-full mb-2 px-1">
          <span className="text-sm font-semibold tracking-wide text-slate-200 uppercase">{title}</span>
          <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">
            {engine.phase.toUpperCase()}
          </span>
        </div>
      )}
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        onClick={handleCanvasClick}
        className={`rounded-lg cursor-${editMode !== 'none' ? 'crosshair' : 'default'} shadow-inner`}
      />
    </div>
  );
};
