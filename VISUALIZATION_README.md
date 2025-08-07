# Interactive Plotly Visualizations for Drone Energy Analysis

This project now includes comprehensive interactive visualizations using Plotly to analyze energy requirements across different drone configurations and POI counts.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements_visualization.txt
   ```

2. **Generate data (if not already done):**
   ```bash
   python sweep_pois.py
   ```

3. **Create visualizations:**
   ```bash
   python plotly_visualizer.py
   ```

4. **Open visualizations in browser:**
   ```bash
   python open_visualizations.py
   ```

## 📊 Available Visualizations

### 1. **Interactive Heatmaps**
- **Individual Mode Heatmaps**: Energy requirements for Independent and External modes
- **Comparison Heatmaps**: Side-by-side comparison of both modes
- **POI-Specific**: Heatmaps for different POI counts (10, 50, 100, 200, 500)
- **Features**: Hover for exact values, zoom, pan, color scale adjustment

### 2. **3D Surface Plots**
- **Energy Landscape**: 3D visualization of energy requirements
- **Interactive**: Rotate, zoom, pan, and explore the energy surface
- **POI Counts**: Available for 50, 100, and 200 POIs
- **Both Modes**: Independent and External mode surfaces

### 3. **Energy vs POIs Analysis**
- **Line Plots**: Energy consumption as POI count increases
- **Drone Configurations**: Pre-defined configurations (2,4), (5,10), (8,16), (10,20)
- **Mode Comparison**: Both Independent and External modes on same plot
- **Trend Analysis**: Identify scaling patterns

### 4. **Optimal Configuration Analysis**
- **Optimal Big Drones**: How many big drones are optimal for each POI count
- **Optimal Small Drones**: How many small drones are optimal for each POI count
- **Mode Comparison**: Compare optimal configurations between modes
- **Decision Support**: Help choose best drone fleet size

### 5. **Comprehensive Dashboard**
- **Multi-View**: Four different POI counts in one view
- **Color Coding**: Different color schemes for easy distinction
- **Overview**: Quick comparison across multiple scenarios

## 🎯 Key Features

### **Interactive Elements**
- **Hover Information**: Exact energy values, drone counts, and POI counts
- **Zoom & Pan**: Explore specific regions in detail
- **Color Scale**: Adjustable color schemes for better visibility
- **Export**: Save plots as PNG, SVG, or HTML

### **Data Insights**
- **Energy Efficiency**: Identify most efficient drone configurations
- **Scaling Patterns**: Understand how energy scales with POIs and drones
- **Mode Comparison**: Compare Independent vs External mode performance
- **Optimal Configurations**: Find best drone fleet sizes for different scenarios

### **Performance Analysis**
- **Energy Distribution**: Visualize energy requirements across configurations
- **Bottlenecks**: Identify inefficient configurations
- **Trends**: Spot patterns in energy consumption
- **Decision Making**: Support for fleet planning decisions

## 📁 File Structure

```
visualizations/
├── independent_heatmap_10pois.html      # Independent mode, 10 POIs
├── independent_heatmap_50pois.html      # Independent mode, 50 POIs
├── independent_heatmap_100pois.html     # Independent mode, 100 POIs
├── independent_heatmap_200pois.html     # Independent mode, 200 POIs
├── external_heatmap_10pois.html         # External mode, 10 POIs
├── external_heatmap_50pois.html         # External mode, 50 POIs
├── external_heatmap_100pois.html        # External mode, 100 POIs
├── external_heatmap_200pois.html        # External mode, 200 POIs
├── comparison_heatmap_10pois.html       # Side-by-side comparison, 10 POIs
├── comparison_heatmap_50pois.html       # Side-by-side comparison, 50 POIs
├── comparison_heatmap_100pois.html      # Side-by-side comparison, 100 POIs
├── comparison_heatmap_200pois.html      # Side-by-side comparison, 200 POIs
├── energy_vs_pois_2big_4small.html      # Energy vs POIs for 2 big, 4 small drones
├── energy_vs_pois_5big_10small.html     # Energy vs POIs for 5 big, 10 small drones
├── energy_vs_pois_8big_16small.html     # Energy vs POIs for 8 big, 16 small drones
├── energy_vs_pois_10big_20small.html    # Energy vs POIs for 10 big, 20 small drones
├── independent_3d_50pois.html           # 3D surface, Independent mode, 50 POIs
├── independent_3d_100pois.html          # 3D surface, Independent mode, 100 POIs
├── independent_3d_200pois.html          # 3D surface, Independent mode, 200 POIs
├── external_3d_50pois.html              # 3D surface, External mode, 50 POIs
├── external_3d_100pois.html             # 3D surface, External mode, 100 POIs
├── external_3d_200pois.html             # 3D surface, External mode, 200 POIs
├── optimal_configurations.html          # Optimal drone configurations analysis
└── comprehensive_dashboard.html         # Multi-view dashboard
```

## 🔧 Customization

### **Modifying POI Counts**
Edit `plotly_visualizer.py` and change the POI counts in the `main()` function:
```python
for poi_count in [10, 50, 100, 200, 500]:  # Modify this list
```

### **Adding New Drone Configurations**
Add new configurations to the `configs` list:
```python
configs = [(2, 4), (5, 10), (8, 16), (10, 20), (15, 30)]  # Add your configs
```

### **Changing Color Schemes**
Modify the `colorscale` parameter in heatmap functions:
```python
colorscale='viridis'  # Try 'plasma', 'inferno', 'magma', 'RdBu', etc.
```

## 📈 Usage Examples

### **Finding Optimal Configuration**
1. Open `optimal_configurations.html`
2. Look for the lowest energy values
3. Note the corresponding big/small drone counts
4. Use this for fleet planning

### **Comparing Modes**
1. Open `comparison_heatmap_100pois.html`
2. Hover over cells to see exact energy values
3. Compare Independent vs External mode performance
4. Identify which mode is more efficient for your scenario

### **Understanding Scaling**
1. Open `energy_vs_pois_5big_10small.html`
2. Observe how energy increases with POI count
3. Identify linear vs non-linear scaling patterns
4. Use this for capacity planning

## 🛠️ Technical Details

### **Dependencies**
- `plotly>=5.0.0`: Interactive plotting library
- `pandas>=1.3.0`: Data manipulation
- `numpy>=1.21.0`: Numerical computations

### **Data Format**
The visualizations expect CSV files with columns:
- `big_drones`: Number of big drones
- `small_drones`: Number of small drones  
- `POIs`: Number of points of interest
- `energy`: Total energy consumption

### **Performance**
- **Large Datasets**: Handles datasets with 100,000+ records
- **Memory Efficient**: Uses pandas for efficient data processing
- **Fast Rendering**: Plotly provides smooth interactive experience

## 🎨 Visualization Best Practices

### **For Presentations**
- Use high contrast color schemes
- Include hover information for exact values
- Export as PNG for static presentations
- Use 3D plots sparingly (they can be complex)

### **For Analysis**
- Compare multiple POI counts
- Look for patterns in optimal configurations
- Consider both energy efficiency and practical constraints
- Use the comprehensive dashboard for overview

### **For Decision Making**
- Focus on optimal configuration analysis
- Consider energy vs cost trade-offs
- Use mode comparison for strategy selection
- Validate findings with multiple POI scenarios

## 🚀 Future Enhancements

Potential improvements for the visualization system:
- **Real-time Updates**: Live visualization during simulation
- **Custom Filters**: Interactive filtering by drone ranges
- **Statistical Analysis**: Confidence intervals and error bars
- **Export Options**: PDF reports and automated analysis
- **Web Dashboard**: Deploy as web application for team access

---

**Happy Analyzing!** 🚁📊 