import React, { useState } from 'react';

export const VisionExplorer: React.FC = () => {
  const [activeStage, setActiveStage] = useState<number>(1);
  const [thresholdSlider, setThresholdSlider] = useState<number>(128);

  const stages = [
    {
      id: 1,
      title: '1. Aerial Drone Capture',
      desc: 'High-resolution RGB orthomosaic of forest canopy affected by Red Turpentine Beetles (RTB). Captured by small survey drones.'
    },
    {
      id: 2,
      title: '2. VQ-VAE Reconstruction',
      desc: 'Vector Quantized Variational Autoencoder reconstructs the healthy baseline canopy using a 256-entry discrete codebook.'
    },
    {
      id: 3,
      title: '3. Reconstruction Error Heatmap',
      desc: 'Per-pixel Mean Squared Error (MSE) between original input and reconstruction. High errors reveal diseased foliage.'
    },
    {
      id: 4,
      title: '4. Otsu Adaptive Thresholding',
      desc: 'Optimal dynamic thresholding T* maximizing between-class variance without manual lighting calibration.'
    },
    {
      id: 5,
      title: '5. Extracted POI Centroids',
      desc: '8-connected component analysis identifies discrete anomaly centroids, passed directly to the multi-UAV routing solver.'
    }
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl text-slate-200">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h2 className="text-xl font-bold tracking-tight text-white mb-1">
            Deep Learning Vision Pipeline: Anomaly Detection
          </h2>
          <p className="text-sm text-slate-400">
            Interactive exploration of the VQ-VAE + SegFormer + Otsu pipeline evaluated on Red Turpentine Beetle canopy infestations.
          </p>
        </div>

        {/* Stage Navigation Pills */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 mb-6">
          {stages.map(st => (
            <button
              key={st.id}
              onClick={() => setActiveStage(st.id)}
              className={`py-2 px-3 rounded-lg text-xs font-semibold text-left transition-all border ${
                activeStage === st.id
                  ? 'bg-sky-600 text-white border-sky-500 shadow-md ring-2 ring-sky-500/30'
                  : 'bg-slate-800 text-slate-400 border-slate-700 hover:bg-slate-700 hover:text-slate-200'
              }`}
            >
              <div className="font-bold">{st.id}. {st.title.split('. ')[1]}</div>
            </button>
          ))}
        </div>

        {/* Active Stage Description */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-4 mb-6">
          <h3 className="text-sm font-bold text-sky-400 mb-1">{stages[activeStage - 1].title}</h3>
          <p className="text-xs text-slate-300 leading-relaxed">{stages[activeStage - 1].desc}</p>
        </div>

        {/* Visual Stage Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
          <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden p-2 flex items-center justify-center min-h-[380px]">
            {activeStage === 1 && (
              <div className="text-center">
                <img
                  src="./field_sample.jpg"
                  alt="Captured Aerial Field"
                  className="rounded-lg max-h-[360px] object-cover mx-auto shadow-md"
                  onError={(e) => {
                    // Fallback to complete_run if field_sample fails
                    (e.target as HTMLImageElement).src = './complete_run.png';
                  }}
                />
                <span className="text-[11px] text-slate-500 block mt-2">Sample RTB Infested Pine Forest</span>
              </div>
            )}

            {activeStage === 2 && (
              <div className="text-center">
                <img
                  src="./model_architecture.png"
                  alt="VQ-VAE Architecture"
                  className="rounded-lg max-h-[360px] object-contain mx-auto shadow-md bg-white/5 p-2"
                />
                <span className="text-[11px] text-slate-500 block mt-2">VQ-VAE ResNet34 + SEBlock + Codebook</span>
              </div>
            )}

            {(activeStage === 3 || activeStage === 4) && (
              <div className="text-center">
                <img
                  src="./complete_run.png"
                  alt="Reconstruction Error & Otsu Threshold"
                  className="rounded-lg max-h-[360px] object-contain mx-auto shadow-md"
                />
                <span className="text-[11px] text-slate-500 block mt-2">
                  {activeStage === 3 ? 'Per-patch Reconstruction Error Heatmap' : 'Otsu Adaptive Binarization (Foreground vs Background)'}
                </span>
              </div>
            )}

            {activeStage === 5 && (
              <div className="text-center">
                <img
                  src="./poi_ext.png"
                  alt="POI Extraction"
                  className="rounded-lg max-h-[360px] object-contain mx-auto shadow-md"
                />
                <span className="text-[11px] text-slate-500 block mt-2">
                  Connected Component Centroids P = &#123;p_1, ..., p_n&#125;
                </span>
              </div>
            )}
          </div>

          {/* Interactive Controls & Mathematical Formulation */}
          <div className="flex flex-col gap-4">
            <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800 text-xs text-slate-300">
              <h4 className="font-bold text-slate-200 mb-2 uppercase tracking-wider text-[11px]">
                Mathematical Formulation
              </h4>
              {activeStage === 1 && (
                <p className="leading-relaxed">
                  Field image I is decomposed into uniform patches t of dimension 256 × 256 × 3 captured along the boustrophedon sweep passes.
                </p>
              )}
              {activeStage === 2 && (
                <div className="space-y-2">
                  <p>
                    Continuous latent representations are quantized into discrete codebook embeddings:
                  </p>
                  <code className="block bg-slate-900 p-2 rounded text-sky-300 font-mono text-[11px]">
                    z_q(x) = e_k, where k = argmin_j ||z_e(x) - e_j||_2
                  </code>
                  <p>
                    Squeeze-and-Excitation blocks selectively amplify canopy color and texture channels.
                  </p>
                </div>
              )}
              {activeStage === 3 && (
                <div className="space-y-2">
                  <p>Reconstruction discrepancy map calculated as channel-averaged MSE:</p>
                  <code className="block bg-slate-900 p-2 rounded text-amber-300 font-mono text-[11px]">
                    I_err(x, y) = 1/3 \sum_c (I(x, y, c) - I_recon(x, y, c))^2
                  </code>
                </div>
              )}
              {activeStage === 4 && (
                <div className="space-y-2">
                  <p>Optimal binarization threshold T* maximizes between-class variance:</p>
                  <code className="block bg-slate-900 p-2 rounded text-purple-300 font-mono text-[11px]">
                    \sigma_B^2(T) = \omega_0(T)\omega_1(T)[\mu_0(T) - \mu_1(T)]^2
                  </code>
                </div>
              )}
              {activeStage === 5 && (
                <div className="space-y-2">
                  <p>Discrete action waypoints extracted via 8-connected components:</p>
                  <code className="block bg-slate-900 p-2 rounded text-emerald-300 font-mono text-[11px]">
                    POIs = ConnectedComponents(I_thresh) \setminus \bigcup O_j
                  </code>
                  <p>Obstacle collision checks remove false positives located within terrain hazards.</p>
                </div>
              )}
            </div>

            {/* Interactive Threshold Sandbox */}
            <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
              <div className="flex justify-between text-xs font-semibold mb-2">
                <span className="text-slate-300">Otsu Threshold Sensitivity (T)</span>
                <span className="text-sky-400 font-mono">{thresholdSlider} / 255</span>
              </div>
              <input
                type="range"
                min={20}
                max={230}
                value={thresholdSlider}
                onChange={(e) => setThresholdSlider(Number(e.target.value))}
                className="w-full accent-sky-500 h-1.5 bg-slate-800 rounded-lg cursor-pointer mb-2"
              />
              <div className="flex justify-between text-[10px] text-slate-500">
                <span>More Sensitive (Includes mild stress)</span>
                <span>Strict (Severe damage only)</span>
              </div>
            </div>

            <div className="p-3 bg-sky-950/40 border border-sky-800/60 rounded-lg text-xs text-sky-200">
              💡 <strong>Empirical Result:</strong> The VQ-VAE + SegFormer pipeline achieved a <strong>13.1 percentage point increase in mAP@50</strong> over YOLO11 by eliminating false detections on bare soil and dry grass.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
