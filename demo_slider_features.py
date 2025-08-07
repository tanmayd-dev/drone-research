import webbrowser
from pathlib import Path

def demo_slider_features():
    """Demo the new interactive POI slider features"""
    
    print("🎯 Interactive POI Slider Demo")
    print("=" * 50)
    
    viz_dir = Path('visualizations')
    
    # Check if the new slider files exist
    slider_files = [
        'interactive_poi_slider_heatmap_interpolated.html',
        'energy_comparison_slider_interpolated.html',
        'interactive_poi_slider_heatmap.html',
        'energy_comparison_slider.html'
    ]
    
    print("Looking for interactive slider visualizations...")
    
    for file_name in slider_files:
        file_path = viz_dir / file_name
        if file_path.exists():
            print(f"✅ Found: {file_name}")
        else:
            print(f"❌ Missing: {file_name}")
    
    print("\n🚀 Opening Interactive POI Slider Visualizations...")
    
    # Open the interpolated slider visualization (priority)
    main_slider_interpolated = viz_dir / 'interactive_poi_slider_heatmap_interpolated.html'
    if main_slider_interpolated.exists():
        try:
            abs_path = main_slider_interpolated.absolute().as_uri()
            webbrowser.open(abs_path)
            print("✅ Opened: Interactive POI Slider Heatmap (Independent Interpolated)")
        except Exception as e:
            print(f"❌ Error opening interpolated main slider: {e}")
    
    # Open the interpolated comparison slider
    comparison_slider_interpolated = viz_dir / 'energy_comparison_slider_interpolated.html'
    if comparison_slider_interpolated.exists():
        try:
            abs_path = comparison_slider_interpolated.absolute().as_uri()
            webbrowser.open(abs_path)
            print("✅ Opened: Energy Comparison Slider (Independent Interpolated)")
        except Exception as e:
            print(f"❌ Error opening interpolated comparison slider: {e}")
    
    # Open the original slider visualization
    main_slider = viz_dir / 'interactive_poi_slider_heatmap.html'
    if main_slider.exists():
        try:
            abs_path = main_slider.absolute().as_uri()
            webbrowser.open(abs_path)
            print("✅ Opened: Interactive POI Slider Heatmap (Original)")
        except Exception as e:
            print(f"❌ Error opening original main slider: {e}")
    
    # Open the original comparison slider
    comparison_slider = viz_dir / 'energy_comparison_slider.html'
    if comparison_slider.exists():
        try:
            abs_path = comparison_slider.absolute().as_uri()
            webbrowser.open(abs_path)
            print("✅ Opened: Energy Comparison Slider (Original)")
        except Exception as e:
            print(f"❌ Error opening original comparison slider: {e}")
    
    print("\n🎮 How to Use the Interactive Slider:")
    print("1. Drag the slider at the bottom to change POI count")
    print("2. Click 'Play' to animate through all POI counts")
    print("3. Hover over cells to see exact energy values")
    print("4. Zoom and pan to explore specific regions")
    print("5. Compare Independent vs External modes side-by-side")
    
    print("\n📊 What You'll See:")
    print("- Energy patterns change as POI count varies")
    print("- Optimal configurations shift with different POI counts")
    print("- Mode performance differences become apparent")
    print("- Scaling trends emerge across POI ranges")
    
    print("\n🔍 Key Insights to Look For:")
    print("- Which mode is more efficient for different POI counts")
    print("- How optimal drone configurations change with POI count")
    print("- Energy scaling patterns (linear vs non-linear)")
    print("- Bottlenecks and inefficiencies at different scales")
    
    print("\n🔄 INTERPOLATION FEATURES:")
    print("- Independent mode data interpolated using nearest neighbor method")
    print("- Smoother transitions between POI counts")
    print("- Filled data gaps for more complete visualization")
    print("- Enhanced hover information showing interpolation status")
    print("- 4.3M interpolated data points for comprehensive coverage")

if __name__ == "__main__":
    demo_slider_features() 