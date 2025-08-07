import webbrowser
import os
from pathlib import Path

def open_visualizations():
    """Open all visualization files in the default browser"""
    viz_dir = Path('visualizations')
    
    if not viz_dir.exists():
        print("Visualizations directory not found. Run plotly_visualizer.py first.")
        return
    
    html_files = list(viz_dir.glob('*.html'))
    
    if not html_files:
        print("No HTML files found in visualizations directory.")
        return
    
    print(f"Found {len(html_files)} visualization files:")
    for i, file in enumerate(html_files, 1):
        print(f"{i:2d}. {file.name}")
    
    print("\nOpening all visualizations in your default browser...")
    
    # Prioritize the new interactive slider visualizations
    priority_files = ['interactive_poi_slider_heatmap.html', 'energy_comparison_slider.html']
    other_files = [f for f in html_files if f.name not in priority_files]
    
    # Open priority files first
    for file in html_files:
        if file.name in priority_files:
            try:
                abs_path = file.absolute().as_uri()
                webbrowser.open(abs_path)
                print(f"Opened: {file.name} (Interactive Slider)")
            except Exception as e:
                print(f"Error opening {file.name}: {e}")
    
    # Open other files
    for file in html_files:
        if file.name not in priority_files:
            try:
                abs_path = file.absolute().as_uri()
                webbrowser.open(abs_path)
                print(f"Opened: {file.name}")
            except Exception as e:
                print(f"Error opening {file.name}: {e}")
    
    print("\nAll visualizations opened! You can now:")
    print("- Use the POI slider to change POI counts dynamically")
    print("- Click 'Play' to animate through all POI counts")
    print("- Hover over heatmaps to see exact energy values")
    print("- Zoom and pan in 3D plots")
    print("- Compare different POI counts and drone configurations")
    print("- Analyze optimal configurations")
    print("\n🎯 NEW: Interactive POI Slider Features:")
    print("- Drag the slider to change POI count instantly")
    print("- Watch energy patterns change as POI count varies")
    print("- Compare Independent vs External modes side-by-side")
    print("- See energy differences with the comparison slider")

if __name__ == "__main__":
    open_visualizations() 