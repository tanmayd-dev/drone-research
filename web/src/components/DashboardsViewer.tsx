import React from 'react';

export const DashboardsViewer: React.FC = () => {
  const categories = [
    {
      title: 'Interactive POI Sliders & Heatmaps',
      description: 'Continuous energy landscape across fleet sizes and POIs with interpolation.',
      links: [
        { name: 'Interactive POI Slider Heatmap (Interpolated)', file: 'interactive_poi_slider_heatmap_interpolated.html' },
        { name: 'Energy Comparison Slider (Interpolated)', file: 'energy_comparison_slider_interpolated.html' },
        { name: 'Comprehensive Multi-POI Dashboard', file: 'comprehensive_dashboard.html' },
        { name: 'Optimal Fleet Configurations Analysis', file: 'optimal_configurations.html' }
      ]
    },
    {
      title: '3D Energy Landscape Surfaces',
      description: 'Interactive 3D surfaces showing energy consumption over (Big Drones × Small Drones).',
      links: [
        { name: 'External Mode 3D Surface (50 POIs)', file: 'external_3d_50pois.html' },
        { name: 'External Mode 3D Surface (100 POIs)', file: 'external_3d_100pois.html' },
        { name: 'External Mode 3D Surface (200 POIs)', file: 'external_3d_200pois.html' },
        { name: 'Independent Mode 3D Surface (50 POIs)', file: 'independent_3d_50pois.html' },
        { name: 'Independent Mode 3D Surface (100 POIs)', file: 'independent_3d_100pois.html' },
        { name: 'Independent Mode 3D Surface (200 POIs)', file: 'independent_3d_200pois.html' }
      ]
    },
    {
      title: 'Side-by-Side Mode Comparisons',
      description: 'Heatmap delta comparisons demonstrating Independent vs External mode performance.',
      links: [
        { name: 'Comparison Heatmap (10 POIs)', file: 'comparison_heatmap_10pois.html' },
        { name: 'Comparison Heatmap (50 POIs)', file: 'comparison_heatmap_50pois.html' },
        { name: 'Comparison Heatmap (100 POIs)', file: 'comparison_heatmap_100pois.html' },
        { name: 'Comparison Heatmap (200 POIs)', file: 'comparison_heatmap_200pois.html' }
      ]
    },
    {
      title: 'Fleet Scaling Curves (Energy vs POIs)',
      description: 'Scaling trends across increasing workload for fixed fleet configurations.',
      links: [
        { name: 'Fleet (2 Big, 4 Small)', file: 'energy_vs_pois_2big_4small.html' },
        { name: 'Fleet (5 Big, 10 Small)', file: 'energy_vs_pois_5big_10small.html' },
        { name: 'Fleet (8 Big, 16 Small)', file: 'energy_vs_pois_8big_16small.html' },
        { name: 'Fleet (10 Big, 20 Small)', file: 'energy_vs_pois_10big_20small.html' }
      ]
    }
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl text-slate-200 max-w-4xl mx-auto">
      <div className="border-b border-slate-800 pb-4 mb-6">
        <h2 className="text-xl font-bold tracking-tight text-white mb-1">
          28 Analytical Plotly Energy Dashboards
        </h2>
        <p className="text-sm text-slate-400">
          Pre-computed parameter sweeps analyzing energy consumption across 1–50 Big Drones, 1–50 Small Drones, and 1–500 POIs.
        </p>
      </div>

      <div className="mb-6 p-4 bg-sky-950/30 border border-sky-800/60 rounded-xl flex items-center justify-between">
        <div>
          <div className="text-sm font-semibold text-white">Full Dashboards Gallery Index</div>
          <div className="text-xs text-slate-400">Access the categorized, searchable gallery with dark mode support.</div>
        </div>
        <a
          href="./visualizations/index.html"
          target="_blank"
          rel="noopener noreferrer"
          className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white font-semibold text-xs rounded-lg transition-colors shadow-md flex items-center gap-1.5"
        >
          ↗ Open Main Index
        </a>
      </div>

      <div className="space-y-6">
        {categories.map((cat, idx) => (
          <div key={idx} className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
            <h3 className="text-sm font-bold text-slate-200 mb-1">{cat.title}</h3>
            <p className="text-xs text-slate-400 mb-3">{cat.description}</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {cat.links.map((link, lIdx) => (
                <a
                  key={lIdx}
                  href={`./visualizations/${link.file}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 rounded-lg text-xs font-medium text-slate-300 hover:text-white transition-all flex items-center justify-between group"
                >
                  <span className="truncate">{link.name}</span>
                  <span className="text-slate-500 group-hover:text-sky-400 transition-colors ml-2">↗</span>
                </a>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
