import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
from pathlib import Path
import numpy as np
from scipy.interpolate import griddata

def load_data():
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
    return None, None

def interpolate_independent_data(df_indep):
    """Interpolate Independent mode data using nearest neighbor interpolation"""
    print("Interpolating Independent mode data using nearest neighbor...")
    
    # Get unique values for interpolation grid
    poi_counts = sorted(df_indep['POIs'].unique())
    big_drones = sorted(df_indep['big_drones'].unique())
    small_drones = sorted(df_indep['small_drones'].unique())
    
    # Create complete grid for interpolation
    poi_grid, big_grid, small_grid = np.meshgrid(poi_counts, big_drones, small_drones, indexing='ij')
    
    # Prepare data points for interpolation
    points = df_indep[['POIs', 'big_drones', 'small_drones']].values
    values = df_indep['energy'].values
    
    # Flatten the grid for interpolation
    grid_points = np.column_stack([poi_grid.flatten(), big_grid.flatten(), small_grid.flatten()])
    
    # Perform nearest neighbor interpolation
    interpolated_energy = griddata(points, values, grid_points, method='nearest')
    
    # Reshape back to 3D array
    interpolated_energy = interpolated_energy.reshape(poi_grid.shape)
    
    # Create interpolated dataframe
    interpolated_data = []
    for i, poi in enumerate(poi_counts):
        for j, big in enumerate(big_drones):
            for k, small in enumerate(small_drones):
                interpolated_data.append({
                    'POIs': poi,
                    'big_drones': big,
                    'small_drones': small,
                    'energy': interpolated_energy[i, j, k]
                })
    
    df_interpolated = pd.DataFrame(interpolated_data)
    print(f"Interpolated data: {len(df_interpolated)} records")
    
    return df_interpolated

def create_poi_slider_heatmap(df_indep, df_ext):
    """Create interactive heatmap with POI slider"""
    
    # Interpolate Independent mode data
    df_indep_interpolated = interpolate_independent_data(df_indep)
    
    # Get unique POI counts
    poi_counts = sorted(df_indep_interpolated['POIs'].unique())
    print(f"Available POI counts: {poi_counts}")
    
    # Create figure with subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Independent Mode (Interpolated)', 'External Mode'),
        specs=[[{"type": "heatmap"}, {"type": "heatmap"}]]
    )
    
    # Create frames for each POI count
    frames = []
    
    for poi_count in poi_counts:
        # Filter data for this POI count
        indep_filtered = df_indep_interpolated[df_indep_interpolated['POIs'] == poi_count]
        ext_filtered = df_ext[df_ext['POIs'] == poi_count]
        
        # Create pivot tables
        indep_pivot = indep_filtered.pivot_table(
            index='small_drones', 
            columns='big_drones', 
            values='energy',
            aggfunc='mean'
        )
        
        ext_pivot = ext_filtered.pivot_table(
            index='small_drones', 
            columns='big_drones', 
            values='energy',
            aggfunc='mean'
        )
        
        # Create frame data
        frame_data = []
        
        # Independent mode heatmap (interpolated)
        frame_data.append(go.Heatmap(
            z=indep_pivot.values,
            x=indep_pivot.columns,
            y=indep_pivot.index,
            colorscale='viridis',
            colorbar=dict(title='Energy', x=0.45),
            hovertemplate='<b>Big Drones:</b> %{x}<br>' +
                         '<b>Small Drones:</b> %{y}<br>' +
                         '<b>Energy:</b> %{z:.2f}<br>' +
                         '<b>POIs:</b> ' + str(poi_count) + '<br>' +
                         '<b>Interpolated:</b> Yes<extra></extra>',
            name='Independent (Interpolated)'
        ))
        
        # External mode heatmap
        frame_data.append(go.Heatmap(
            z=ext_pivot.values,
            x=ext_pivot.columns,
            y=ext_pivot.index,
            colorscale='plasma',
            colorbar=dict(title='Energy', x=1.0),
            hovertemplate='<b>Big Drones:</b> %{x}<br>' +
                         '<b>Small Drones:</b> %{y}<br>' +
                         '<b>Energy:</b> %{z:.2f}<br>' +
                         '<b>POIs:</b> ' + str(poi_count) + '<extra></extra>',
            name='External'
        ))
        
        frames.append(go.Frame(
            data=frame_data,
            name=str(poi_count),
            layout=go.Layout(
                title=f'Energy Requirements - {poi_count} POIs (Independent Interpolated)',
                annotations=[
                    dict(
                        text=f"POIs: {poi_count}",
                        xref="paper", yref="paper",
                        x=0.5, y=1.02,
                        showarrow=False,
                        font=dict(size=16)
                    )
                ]
            )
        ))
    
    # Add initial frame (first POI count)
    initial_poi = poi_counts[0]
    indep_initial = df_indep_interpolated[df_indep_interpolated['POIs'] == initial_poi].pivot_table(
        index='small_drones', columns='big_drones', values='energy', aggfunc='mean'
    )
    ext_initial = df_ext[df_ext['POIs'] == initial_poi].pivot_table(
        index='small_drones', columns='big_drones', values='energy', aggfunc='mean'
    )
    
    # Add initial traces
    fig.add_trace(go.Heatmap(
        z=indep_initial.values,
        x=indep_initial.columns,
        y=indep_initial.index,
        colorscale='viridis',
        colorbar=dict(title='Energy', x=0.45),
        hovertemplate='<b>Big Drones:</b> %{x}<br>' +
                     '<b>Small Drones:</b> %{y}<br>' +
                     '<b>Energy:</b> %{z:.2f}<br>' +
                     '<b>POIs:</b> ' + str(initial_poi) + '<br>' +
                     '<b>Interpolated:</b> Yes<extra></extra>',
        name='Independent (Interpolated)'
    ), row=1, col=1)
    
    fig.add_trace(go.Heatmap(
        z=ext_initial.values,
        x=ext_initial.columns,
        y=ext_initial.index,
        colorscale='plasma',
        colorbar=dict(title='Energy', x=1.0),
        hovertemplate='<b>Big Drones:</b> %{x}<br>' +
                     '<b>Small Drones:</b> %{y}<br>' +
                     '<b>Energy:</b> %{z:.2f}<br>' +
                     '<b>POIs:</b> ' + str(initial_poi) + '<extra></extra>',
        name='External'
    ), row=1, col=2)
    
    # Add frames
    fig.frames = frames
    
    # Create slider
    sliders = [dict(
        steps=[dict(
            method="animate",
            args=[[frame.name],
                  dict(mode="immediate",
                       transition=dict(duration=300),
                       frame=dict(duration=300, redraw=True))],
            label=str(frame.name)
        ) for frame in frames],
        active=0,
        currentvalue=dict(prefix="POIs: "),
        len=0.9,
        x=0.1,
        xanchor="left",
        y=0,
        yanchor="top",
        transition=dict(duration=300, easing="cubic-in-out")
    )]
    
    # Update layout
    fig.update_layout(
        title='Interactive Energy Heatmap - Independent Mode Interpolated (Nearest Neighbor)',
        width=1600,
        height=700,
        sliders=sliders,
        updatemenus=[dict(
            type="buttons",
            direction="left",
            pad=dict(r=10, t=87),
            showactive=False,
            x=0.1,
            xanchor="right",
            y=0,
            yanchor="top",
            buttons=[
                dict(
                    args=[None, {"frame": {"duration": 500, "redraw": True},
                                "fromcurrent": True, "transition": {"duration": 300,
                                                                   "easing": "quadratic-in-out"}}],
                    label="Play",
                    method="animate"
                ),
                dict(
                    args=[[None], {"frame": {"duration": 0, "redraw": True},
                                  "mode": "immediate",
                                  "transition": {"duration": 0}}],
                    label="Pause",
                    method="animate"
                )
            ]
        )]
    )
    
    # Update axes
    fig.update_xaxes(title_text="Big Drones", row=1, col=1)
    fig.update_yaxes(title_text="Small Drones", row=1, col=1)
    fig.update_xaxes(title_text="Big Drones", row=1, col=2)
    fig.update_yaxes(title_text="Small Drones", row=1, col=2)
    
    return fig

def create_energy_comparison_slider(df_indep, df_ext):
    """Create a comparison view showing energy difference between modes"""
    
    # Interpolate Independent mode data
    df_indep_interpolated = interpolate_independent_data(df_indep)
    
    poi_counts = sorted(df_indep_interpolated['POIs'].unique())
    
    fig = go.Figure()
    
    # Create frames for each POI count
    frames = []
    
    for poi_count in poi_counts:
        # Filter data for this POI count
        indep_filtered = df_indep_interpolated[df_indep_interpolated['POIs'] == poi_count]
        ext_filtered = df_ext[df_ext['POIs'] == poi_count]
        
        # Create pivot tables
        indep_pivot = indep_filtered.pivot_table(
            index='small_drones', 
            columns='big_drones', 
            values='energy',
            aggfunc='mean'
        )
        
        ext_pivot = ext_filtered.pivot_table(
            index='small_drones', 
            columns='big_drones', 
            values='energy',
            aggfunc='mean'
        )
        
        # Calculate difference (External - Independent)
        # Align the pivot tables
        common_index = indep_pivot.index.intersection(ext_pivot.index)
        common_cols = indep_pivot.columns.intersection(ext_pivot.columns)
        
        indep_aligned = indep_pivot.loc[common_index, common_cols]
        ext_aligned = ext_pivot.loc[common_index, common_cols]
        
        difference = ext_aligned - indep_aligned
        
        # Create frame data
        frame_data = [go.Heatmap(
            z=difference.values,
            x=difference.columns,
            y=difference.index,
            colorscale='RdBu_r',  # Red-Blue diverging scale
            zmid=0,  # Center at zero
            colorbar=dict(title='Energy Difference (External - Independent)'),
            hovertemplate='<b>Big Drones:</b> %{x}<br>' +
                         '<b>Small Drones:</b> %{y}<br>' +
                         '<b>Energy Diff:</b> %{z:.2f}<br>' +
                         '<b>POIs:</b> ' + str(poi_count) + '<br>' +
                         '<b>Independent Interpolated:</b> Yes<extra></extra>'
        )]
        
        frames.append(go.Frame(
            data=frame_data,
            name=str(poi_count),
            layout=go.Layout(
                title=f'Energy Difference: External - Independent Mode ({poi_count} POIs, Independent Interpolated)',
                annotations=[
                    dict(
                        text=f"POIs: {poi_count}",
                        xref="paper", yref="paper",
                        x=0.5, y=1.02,
                        showarrow=False,
                        font=dict(size=16)
                    )
                ]
            )
        ))
    
    # Add initial frame
    initial_poi = poi_counts[0]
    indep_initial = df_indep_interpolated[df_indep_interpolated['POIs'] == initial_poi].pivot_table(
        index='small_drones', columns='big_drones', values='energy', aggfunc='mean'
    )
    ext_initial = df_ext[df_ext['POIs'] == initial_poi].pivot_table(
        index='small_drones', columns='big_drones', values='energy', aggfunc='mean'
    )
    
    # Align and calculate difference
    common_index = indep_initial.index.intersection(ext_initial.index)
    common_cols = indep_initial.columns.intersection(ext_initial.columns)
    
    indep_aligned = indep_initial.loc[common_index, common_cols]
    ext_aligned = ext_initial.loc[common_index, common_cols]
    
    difference = ext_aligned - indep_aligned
    
    fig.add_trace(go.Heatmap(
        z=difference.values,
        x=difference.columns,
        y=difference.index,
        colorscale='RdBu_r',
        zmid=0,
        colorbar=dict(title='Energy Difference (External - Independent)'),
        hovertemplate='<b>Big Drones:</b> %{x}<br>' +
                     '<b>Small Drones:</b> %{y}<br>' +
                     '<b>Energy Diff:</b> %{z:.2f}<br>' +
                     '<b>POIs:</b> ' + str(initial_poi) + '<br>' +
                     '<b>Independent Interpolated:</b> Yes<extra></extra>'
    ))
    
    # Add frames
    fig.frames = frames
    
    # Create slider
    sliders = [dict(
        steps=[dict(
            method="animate",
            args=[[frame.name],
                  dict(mode="immediate",
                       transition=dict(duration=300),
                       frame=dict(duration=300, redraw=True))],
            label=str(frame.name)
        ) for frame in frames],
        active=0,
        currentvalue=dict(prefix="POIs: "),
        len=0.9,
        x=0.1,
        xanchor="left",
        y=0,
        yanchor="top",
        transition=dict(duration=300, easing="cubic-in-out")
    )]
    
    # Update layout
    fig.update_layout(
        title='Energy Difference Between Modes - Independent Mode Interpolated (Nearest Neighbor)',
        width=1200,
        height=700,
        sliders=sliders,
        updatemenus=[dict(
            type="buttons",
            direction="left",
            pad=dict(r=10, t=87),
            showactive=False,
            x=0.1,
            xanchor="right",
            y=0,
            yanchor="top",
            buttons=[
                dict(
                    args=[None, {"frame": {"duration": 500, "redraw": True},
                                "fromcurrent": True, "transition": {"duration": 300,
                                                                   "easing": "quadratic-in-out"}}],
                    label="Play",
                    method="animate"
                ),
                dict(
                    args=[[None], {"frame": {"duration": 0, "redraw": True},
                                  "mode": "immediate",
                                  "transition": {"duration": 0}}],
                    label="Pause",
                    method="animate"
                )
            ]
        )]
    )
    
    fig.update_xaxes(title_text="Big Drones")
    fig.update_yaxes(title_text="Small Drones")
    
    return fig

def main():
    """Main function to create interactive slider visualizations"""
    print("Loading data...")
    df_indep, df_ext = load_data()
    
    if df_indep is None or df_ext is None:
        return
    
    # Create output directory
    output_dir = Path('visualizations')
    output_dir.mkdir(exist_ok=True)
    
    print("Creating interactive POI slider heatmap with Independent mode interpolation...")
    fig_heatmap = create_poi_slider_heatmap(df_indep, df_ext)
    fig_heatmap.write_html(output_dir / 'interactive_poi_slider_heatmap_interpolated.html')
    
    print("Creating energy comparison slider with Independent mode interpolation...")
    fig_comparison = create_energy_comparison_slider(df_indep, df_ext)
    fig_comparison.write_html(output_dir / 'energy_comparison_slider_interpolated.html')
    
    print(f"\nInteractive visualizations with interpolation saved to '{output_dir}' directory!")
    print("Files created:")
    print("- interactive_poi_slider_heatmap_interpolated.html: Side-by-side heatmaps with POI slider (Independent interpolated)")
    print("- energy_comparison_slider_interpolated.html: Energy difference comparison with POI slider (Independent interpolated)")
    print("\nFeatures:")
    print("- Independent mode data interpolated using nearest neighbor method")
    print("- Smoother transitions between POI counts")
    print("- Use the slider to change POI count")
    print("- Click 'Play' to animate through all POI counts")
    print("- Hover for exact energy values")
    print("- Zoom and pan to explore specific regions")

if __name__ == "__main__":
    main() 