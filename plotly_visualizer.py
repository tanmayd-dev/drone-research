import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
import numpy as np
from pathlib import Path

def load_and_prepare_data():
    """Load CSV data and prepare for visualization"""
    # Try different possible file names
    possible_files = [
        ('sweep_results_independent.csv', 'sweep_results_external.csv'),
        ('library sweep_results_independent.csv', 'library sweep_results_external.csv'),
        ('2-opt sweep_results_independent.csv', '2-opt sweep_results_external.csv')
    ]
    
    for indep_file, ext_file in possible_files:
        try:
            df_indep = pd.read_csv(indep_file)
            df_ext = pd.read_csv(ext_file)
            print(f"Loaded {len(df_indep)} independent mode records from {indep_file}")
            print(f"Loaded {len(df_ext)} external mode records from {ext_file}")
            return df_indep, df_ext
        except FileNotFoundError:
            continue
    
    print("Error: Could not find sweep results CSV files")
    print("Available files:")
    import os
    for file in os.listdir('.'):
        if file.endswith('.csv'):
            print(f"  - {file}")
    return None, None

def create_interactive_heatmap(df, mode_name, poi_count=None):
    """Create interactive heatmap for a specific mode and POI count"""
    if poi_count:
        df_filtered = df[df['POIs'] == poi_count]
        title = f"{mode_name} Mode - Energy Requirements ({poi_count} POIs)"
    else:
        df_filtered = df
        title = f"{mode_name} Mode - Energy Requirements (All POIs)"
    
    if df_filtered.empty:
        print(f"No data for {mode_name} mode with {poi_count} POIs")
        return None
    
    # Create pivot table
    pivot = df_filtered.pivot_table(
        index='small_drones', 
        columns='big_drones', 
        values='energy',
        aggfunc='mean'  # In case of multiple POI counts
    )
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='viridis',
        colorbar=dict(title='Energy'),
        hovertemplate='<b>Big Drones:</b> %{x}<br>' +
                     '<b>Small Drones:</b> %{y}<br>' +
                     '<b>Energy:</b> %{z:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Big Drones',
        yaxis_title='Small Drones',
        width=800,
        height=600
    )
    
    return fig

def create_poi_comparison_heatmap(df_indep, df_ext, poi_count):
    """Create side-by-side comparison heatmaps for both modes"""
    fig_indep = create_interactive_heatmap(df_indep, "Independent", poi_count)
    fig_ext = create_interactive_heatmap(df_ext, "External", poi_count)
    
    if fig_indep is None or fig_ext is None:
        return None
    
    # Create subplot
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Independent Mode', 'External Mode'),
        specs=[[{"type": "heatmap"}, {"type": "heatmap"}]]
    )
    
    # Add both heatmaps
    fig.add_trace(fig_indep.data[0], row=1, col=1)
    fig.add_trace(fig_ext.data[0], row=1, col=2)
    
    fig.update_layout(
        title=f'Energy Comparison - {poi_count} POIs',
        width=1600,
        height=600
    )
    
    return fig

def create_energy_vs_pois_plot(df_indep, df_ext, big_drones, small_drones):
    """Create line plot showing energy vs POIs for specific drone configuration"""
    # Filter data for specific drone configuration
    indep_filtered = df_indep[
        (df_indep['big_drones'] == big_drones) & 
        (df_indep['small_drones'] == small_drones)
    ].sort_values('POIs')
    
    ext_filtered = df_ext[
        (df_ext['big_drones'] == big_drones) & 
        (df_ext['small_drones'] == small_drones)
    ].sort_values('POIs')
    
    fig = go.Figure()
    
    # Add independent mode line
    fig.add_trace(go.Scatter(
        x=indep_filtered['POIs'],
        y=indep_filtered['energy'],
        mode='lines+markers',
        name='Independent Mode',
        line=dict(color='blue', width=2),
        marker=dict(size=6)
    ))
    
    # Add external mode line
    fig.add_trace(go.Scatter(
        x=ext_filtered['POIs'],
        y=ext_filtered['energy'],
        mode='lines+markers',
        name='External Mode',
        line=dict(color='red', width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title=f'Energy vs POIs (Big: {big_drones}, Small: {small_drones})',
        xaxis_title='Number of POIs',
        yaxis_title='Energy',
        width=1000,
        height=600,
        hovermode='x unified'
    )
    
    return fig

def create_3d_surface(df, mode_name, poi_count):
    """Create 3D surface plot for energy landscape"""
    df_filtered = df[df['POIs'] == poi_count]
    
    if df_filtered.empty:
        print(f"No data for {mode_name} mode with {poi_count} POIs")
        return None
    
    # Create pivot table
    pivot = df_filtered.pivot_table(
        index='small_drones', 
        columns='big_drones', 
        values='energy',
        aggfunc='mean'
    )
    
    # Create 3D surface
    fig = go.Figure(data=go.Surface(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='viridis',
        colorbar=dict(title='Energy')
    ))
    
    fig.update_layout(
        title=f'{mode_name} Mode - Energy Surface ({poi_count} POIs)',
        scene=dict(
            xaxis_title='Big Drones',
            yaxis_title='Small Drones',
            zaxis_title='Energy'
        ),
        width=800,
        height=600
    )
    
    return fig

def create_optimal_configuration_analysis(df_indep, df_ext):
    """Find and visualize optimal configurations"""
    # Find minimum energy for each POI count
    indep_min = df_indep.loc[df_indep.groupby('POIs')['energy'].idxmin()]
    ext_min = df_ext.loc[df_ext.groupby('POIs')['energy'].idxmin()]
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Independent Mode - Optimal Big Drones',
            'Independent Mode - Optimal Small Drones',
            'External Mode - Optimal Big Drones', 
            'External Mode - Optimal Small Drones'
        )
    )
    
    # Independent mode optimal big drones
    fig.add_trace(
        go.Scatter(x=indep_min['POIs'], y=indep_min['big_drones'], 
                  mode='lines+markers', name='Independent', line=dict(color='blue')),
        row=1, col=1
    )
    
    # Independent mode optimal small drones
    fig.add_trace(
        go.Scatter(x=indep_min['POIs'], y=indep_min['small_drones'], 
                  mode='lines+markers', name='Independent', line=dict(color='blue'), showlegend=False),
        row=1, col=2
    )
    
    # External mode optimal big drones
    fig.add_trace(
        go.Scatter(x=ext_min['POIs'], y=ext_min['big_drones'], 
                  mode='lines+markers', name='External', line=dict(color='red')),
        row=2, col=1
    )
    
    # External mode optimal small drones
    fig.add_trace(
        go.Scatter(x=ext_min['POIs'], y=ext_min['small_drones'], 
                  mode='lines+markers', name='External', line=dict(color='red'), showlegend=False),
        row=2, col=2
    )
    
    fig.update_layout(
        title='Optimal Drone Configurations by POI Count',
        width=1200,
        height=800
    )
    
    return fig

def main():
    """Main function to create all visualizations"""
    print("Loading data...")
    df_indep, df_ext = load_and_prepare_data()
    
    if df_indep is None or df_ext is None:
        return
    
    # Get unique POI counts
    poi_counts = sorted(df_indep['POIs'].unique())
    print(f"Found POI counts: {poi_counts}")
    
    # Create output directory
    output_dir = Path('visualizations')
    output_dir.mkdir(exist_ok=True)
    
    # 1. Create heatmaps for different POI counts
    print("Creating heatmaps...")
    for poi_count in [10, 50, 100, 200, 500]:  # Key POI counts
        if poi_count in poi_counts:
            # Individual mode heatmaps
            fig_indep = create_interactive_heatmap(df_indep, "Independent", poi_count)
            if fig_indep:
                fig_indep.write_html(output_dir / f'independent_heatmap_{poi_count}pois.html')
            
            fig_ext = create_interactive_heatmap(df_ext, "External", poi_count)
            if fig_ext:
                fig_ext.write_html(output_dir / f'external_heatmap_{poi_count}pois.html')
            
            # Comparison heatmap
            fig_comp = create_poi_comparison_heatmap(df_indep, df_ext, poi_count)
            if fig_comp:
                fig_comp.write_html(output_dir / f'comparison_heatmap_{poi_count}pois.html')
    
    # 2. Create energy vs POIs plots for key configurations
    print("Creating energy vs POIs plots...")
    configs = [(2, 4), (5, 10), (8, 16), (10, 20)]
    for big, small in configs:
        fig = create_energy_vs_pois_plot(df_indep, df_ext, big, small)
        if fig:
            fig.write_html(output_dir / f'energy_vs_pois_{big}big_{small}small.html')
    
    # 3. Create 3D surface plots
    print("Creating 3D surface plots...")
    for poi_count in [50, 100, 200]:
        if poi_count in poi_counts:
            fig_indep_3d = create_3d_surface(df_indep, "Independent", poi_count)
            if fig_indep_3d:
                fig_indep_3d.write_html(output_dir / f'independent_3d_{poi_count}pois.html')
            
            fig_ext_3d = create_3d_surface(df_ext, "External", poi_count)
            if fig_ext_3d:
                fig_ext_3d.write_html(output_dir / f'external_3d_{poi_count}pois.html')
    
    # 4. Create optimal configuration analysis
    print("Creating optimal configuration analysis...")
    fig_opt = create_optimal_configuration_analysis(df_indep, df_ext)
    if fig_opt:
        fig_opt.write_html(output_dir / 'optimal_configurations.html')
    
    # 5. Create comprehensive dashboard
    print("Creating comprehensive dashboard...")
    create_comprehensive_dashboard(df_indep, df_ext, output_dir)
    
    print(f"\nAll visualizations saved to '{output_dir}' directory!")
    print("Open the HTML files in your browser to view interactive plots.")

def create_comprehensive_dashboard(df_indep, df_ext, output_dir):
    """Create a comprehensive dashboard with multiple views"""
    # Get some key POI counts
    poi_counts = sorted(df_indep['POIs'].unique())
    key_pois = [poi_counts[i] for i in range(0, len(poi_counts), len(poi_counts)//4)][:4]
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[f'{poi} POIs' for poi in key_pois],
        specs=[[{"type": "heatmap"}, {"type": "heatmap"}],
               [{"type": "heatmap"}, {"type": "heatmap"}]]
    )
    
    colors = ['viridis', 'plasma', 'inferno', 'magma']
    
    for i, poi_count in enumerate(key_pois):
        row = i // 2 + 1
        col = i % 2 + 1
        
        # Use independent mode data for this example
        df_filtered = df_indep[df_indep['POIs'] == poi_count]
        pivot = df_filtered.pivot_table(
            index='small_drones', 
            columns='big_drones', 
            values='energy',
            aggfunc='mean'
        )
        
        fig.add_trace(
            go.Heatmap(
                z=pivot.values,
                x=pivot.columns,
                y=pivot.index,
                colorscale=colors[i],
                colorbar=dict(title='Energy'),
                hovertemplate='<b>Big:</b> %{x}<br><b>Small:</b> %{y}<br><b>Energy:</b> %{z:.2f}<extra></extra>'
            ),
            row=row, col=col
        )
    
    fig.update_layout(
        title='Energy Requirements Dashboard - Independent Mode',
        width=1200,
        height=800
    )
    
    fig.write_html(output_dir / 'comprehensive_dashboard.html')

if __name__ == "__main__":
    main() 