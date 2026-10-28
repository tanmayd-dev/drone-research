# Heterogeneous Multi-UAV Swarm Routing & Deep Anomaly Detection for Precision Agriculture

[![Paper DOI](https://img.shields.io/badge/DOI-10.1016%2Fj.rineng.2025.104081-blue.svg)](https://doi.org/10.1016/j.rineng.2025.104081)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-emerald.svg)](https://tanmayd-dev.github.io/drone-research/)
[![Build & Test](https://img.shields.io/badge/CI-Passing-brightgreen.svg)]()
[![Stack](https://img.shields.io/badge/Stack-PyTorch%20%7C%20React%20%7C%20TypeScript%20%7C%20Vite-indigo.svg)]()

> **Interactive Web Demonstration:** Explore live multi-drone flight simulations, obstacle avoidance, and the deep learning vision pipeline directly in your browser:  
> 👉 **[tanmayd-dev.github.io/drone-research](https://tanmayd-dev.github.io/drone-research/)**

---

## 📖 Overview

This repository provides an end-to-end framework and simulation platform for heterogeneous multi-UAV precision agriculture. It combines self-supervised deep learning canopy anomaly detection with workload-balanced, obstacle-aware coverage path planning.

The project builds upon research published in **Results in Engineering** (Elsevier, 2025; [DOI: 10.1016/j.rineng.2025.104081](https://doi.org/10.1016/j.rineng.2025.104081)), extending coverage path planning to a two-tier swarm hierarchy.

---

## 🚀 Key Innovations & System Pipeline

```
  ┌────────────────────────────────────────────────────────┐
  │         Phase 1: Small Scout Drone Aerial Survey       │
  │   (Lightweight boustrophedon sweep grid reconnaissance)│
  └───────────────────────────┬────────────────────────────┘
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │     Phase 2: Deep Learning Vision Anomaly Pipeline     │
  │  1. VQ-VAE (Discrete Codebook) learns healthy canopies │
  │  2. SegFormer extracts multi-scale transformer features│
  │  3. Pixel-wise MSE identifies reconstruction errors    │
  │  4. Otsu Adaptive Thresholding binarizes damaged zones │
  │  5. 8-Connected Components extracts POI Centroids      │
  └───────────────────────────┬────────────────────────────┘
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │      Phase 3: Multi-UAV Workload Balancing & Routing   │
  │  • Size-Balanced K-Means: Enforces capacity C=⌈N/k⌉    │
  │  • Simulated Annealing (SA) TSP: Escapes local minima   │
  │  • Grid A* Pathfinder: Collision-free around obstacles  │
  │  • Big Drone Dispatch: Administers targeted treatment   │
  └────────────────────────────────────────────────────────┘
```

### 1. Vision Anomaly Pipeline
* **Self-Supervised Anomaly Reconstruction:** Unlike traditional object detectors (e.g., YOLO) that require explicit bounding box labels and misidentify bare soil as damaged crops, our **VQ-VAE** learns healthy canopy representations. Damaged foliage (such as pine trees infested with Red Turpentine Beetles) produces sharp reconstruction discrepancies.
* **Accuracy Improvement:** Evaluated on real-world aerial imagery, achieving a **13.1 percentage point increase in mAP@50 over YOLO11**.

### 2. Multi-Tier Swarm Architecture
* **Tier 1 — Small Scout Swarm:** Agile, lightweight drones executing high-speed grid sweeps to spot Points of Interest (POIs).
* **Tier 2 — Big Heavy-Action Drones:** Higher-payload drones equipped with pesticides deployed along optimal tours to treat detected POIs.

### 3. Architectural Modes Evaluated
* **Independent Mode (Decentralized / Regional):** The agricultural field is divided into spatial grid sectors (one per Big Drone). Each Big Drone and its dedicated scout swarm scan and act locally.
* **External Mode (Centralized / Global Coordination):** Scouts report detections to a central depot. An external controller runs **Size-Balanced K-Means** and dispatches Big Drones to cluster centers.
* **Empirical Finding:** Independent Mode is significantly more energy-efficient for small drone reconnaissance because small drones launch from their local regional centers rather than incurring long transit flights from a central depot.

---

## 📁 Repository Structure

```
├── web/                               # Interactive Web App (Vite + React + Canvas + TypeScript)
│   ├── src/components/                # SimulationCanvas, ControlPanel, TelemetryHUD, VisionExplorer
│   └── src/simulation/                # In-browser A*, Size-Balanced K-Means, and SA-TSP engines
├── model/                             # Machine Learning Vision Pipeline
│   ├── train-model.ipynb              # PyTorch training & validation notebook
│   ├── vqvae.py                       # VQ-VAE model with Squeeze-and-Excitation (SE) blocks
│   ├── segformer.py                   # SegFormer semantic segmentation backbone
│   ├── otsu_detector.py               # Otsu adaptive thresholding and centroid extractor
│   ├── inference.py                   # CLI to detect POIs on aerial drone images
│   └── sample_data/                   # Sample test image patches
├── simulation/                        # Multi-UAV Algorithms & Energy Sweeps
│   ├── common/                        # Shared A* obstacle avoidance, K-Means, and SA-TSP
│   ├── independent_mode/              # Regional grid partition simulation runner
│   ├── external_mode/                 # Centralized Size-Balanced K-Means simulation runner
│   └── sweep_pois.py                  # Parameter sweep engine across 1–500 POIs
├── visualizations/                    # 28 Pre-Computed Interactive Plotly Dashboards
│   └── index.html                     # Searchable dashboard gallery with dark mode
├── tests/                             # Unit test suite verifying A*, K-Means, and TSP algorithms
└── .github/workflows/                 # CI and GitHub Pages automated deployment
```

---

## ⚡ Quick Start

### 1. Interactive Web Simulator (Browser)

Run the client-side simulation app locally:

```bash
cd web
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

To bundle the entire showcase (including the 28 Plotly dashboards):

```bash
npm run build:all
```

### 2. Python Simulation & Unit Tests

Run the test suite to verify A* obstacle avoidance, Size-Balanced K-Means, and Simulated Annealing TSP:

```bash
pytest tests/
```

Run simulation sweeps:

```bash
python sweep_pois.py
```

### 3. Deep Learning Vision Inference

Extract POI coordinates from an aerial field image:

```bash
python -m model.inference --image "web/public/field_sample.jpg" --output "detected_pois.json"
```

---

## 📊 Analytical Dashboards

The repository includes **28 pre-rendered interactive Plotly dashboards** located in `visualizations/`:
* **Heatmaps & 3D Landscapes:** Energy landscapes across Big Drones ($1-50$), Small Drones ($1-50$), and POIs ($1-500$).
* **Side-by-Side Comparisons:** Direct delta comparisons between Independent and External modes.
* **Interactive Sliders:** Dynamic sliders interpolating energy surfaces across continuous POI counts.

View all dashboards locally by opening [`visualizations/index.html`](./visualizations/index.html) or online on [GitHub Pages](https://tanmayd-dev.github.io/drone-research/visualizations/index.html).

---

## 📝 Citation

If you use this work, the simulation framework, or the vision pipeline, please cite the published foundational study:

```bibtex
@article{menon2025critical,
  title={Critical regions identification and coverage using optimal drone flight path planning for precision agriculture},
  author={Menon, Bharath Krishna and Deshpande, Tanmay and Pal, Amrit and Kothandaraman, Saravanan},
  journal={Results in Engineering},
  volume={25},
  pages={104081},
  year={2025},
  publisher={Elsevier},
  doi={10.1016/j.rineng.2025.104081}
}
```

---

## 📄 License

This project is licensed under the MIT License.
