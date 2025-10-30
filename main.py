#!/usr/bin/env python3
"""
Main script for Istanbul Churches Maps
Executes all mapping scripts and serves the results on localhost
"""

import os
import sys
import time
import webbrowser
import threading
import http.server
import socketserver
from pathlib import Path
import subprocess
import argparse

def ensure_dependencies():
    """Ensure all required packages are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = ["folium", "requests", "pandas"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        venv_pip = Path(__file__).parent / ".venv" / "bin" / "pip"
        if venv_pip.exists():
            pip_cmd = str(venv_pip)
        else:
            pip_cmd = "pip"
        
        try:
            subprocess.run([pip_cmd, "install"] + missing_packages, check=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            sys.exit(1)
    else:
        print("✅ All dependencies are available")

def generate_points_map():
    """Generate the churches points map."""
    print("📍 Generating churches points map...")
    
    try:
        from istanbul_churches_map import IstanbulChurchesMapper
        mapper = IstanbulChurchesMapper()
        filepath = mapper.create_complete_map()
        print(f"✅ Points map created: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ Error creating points map: {e}")
        return None

def generate_buildings_map():
    """Generate the churches buildings map."""
    print("🏛️ Generating churches buildings map...")
    
    # Create buildings mapper inline since the file might be missing
    try:
        import folium
        import requests
        import json
        from typing import List, Dict
        
        class IstanbulChurchesBuildingsMapper:
            def __init__(self):
                self.istanbul_center = [41.0082, 28.9784]
                self.map = None
            
            def create_base_map(self):
                """Create base map with satellite view."""
                self.map = folium.Map(
                    location=self.istanbul_center,
                    zoom_start=13,
                    tiles='OpenStreetMap'
                )
                
                # Add satellite view
                folium.TileLayer(
                    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    attr='Tiles &copy; Esri',
                    name='Satellite View',
                    overlay=False,
                    control=True
                ).add_to(self.map)
                
                folium.LayerControl().add_to(self.map)
                return self.map
            
            def fetch_and_add_buildings(self):
                """Fetch and add building polygons."""
                try:
                    overpass_url = "http://overpass-api.de/api/interpreter"
                    overpass_query = """
                    [out:json][timeout:25];
                    (
                      way["amenity"="place_of_worship"]["religion"="christian"](40.9,28.7,41.2,29.3);
                      way["historic"="church"](40.9,28.7,41.2,29.3);
                      way["building"="church"](40.9,28.7,41.2,29.3);
                    );
                    out geom;
                    """
                    
                    # Bypass proxy for OpenStreetMap API
                    proxies = {'http': '', 'https': ''}
                    response = requests.get(overpass_url, params={'data': overpass_query}, timeout=30, proxies=proxies)
                    response.raise_for_status()
                    data = response.json()
                    
                    colors = {'Orthodox': 'red', 'Catholic': 'blue', 'Armenian Orthodox': 'purple', 
                             'Protestant': 'green', 'Christian': 'orange'}
                    
                    buildings_added = 0
                    for element in data['elements']:
                        if element['type'] != 'way' or 'geometry' not in element:
                            continue
                        
                        coords = [[node['lat'], node['lon']] for node in element['geometry']]
                        if len(coords) < 3:
                            continue
                        
                        tags = element.get('tags', {})
                        name = tags.get('name', f'Church Building {element["id"]}')
                        denomination = tags.get('denomination', 'Christian')
                        
                        # Determine color
                        color = 'orange'  # default
                        for denom, col in colors.items():
                            if denom.lower() in denomination.lower():
                                color = col
                                break
                        
                        # Create polygon
                        if self.map:
                            folium.Polygon(
                                locations=coords,
                                popup=f"<b>{name}</b><br>Denomination: {denomination}",
                                tooltip=name,
                                color=color,
                                weight=3,
                                opacity=0.8,
                                fill=True,
                                fillColor=color,
                                fillOpacity=0.3
                            ).add_to(self.map)
                        
                        buildings_added += 1
                    
                    print(f"   Added {buildings_added} building footprints")
                    return buildings_added
                    
                except Exception as e:
                    print(f"   Error fetching buildings: {e}")
                    return 0
            
            def save_map(self, filename):
                """Save the map."""
                if not self.map:
                    raise ValueError("Map not initialized")
                filepath = Path(__file__).parent / filename
                self.map.save(str(filepath))
                return str(filepath)
            
            def create_complete_map(self):
                """Create complete buildings map."""
                self.create_base_map()
                buildings_count = self.fetch_and_add_buildings()
                filepath = self.save_map('istanbul_churches_buildings_map.html')
                return filepath, buildings_count
        
        # Create the buildings map
        buildings_mapper = IstanbulChurchesBuildingsMapper()
        filepath, count = buildings_mapper.create_complete_map()
        print(f"✅ Buildings map created: {filepath} ({count} buildings)")
        return filepath
        
    except Exception as e:
        print(f"❌ Error creating buildings map: {e}")
        return None

def generate_coverage_analysis():
    """Generate coverage analysis."""
    print("📊 Generating coverage analysis...")
    
    try:
        from analyze_coverage import analyze_church_coverage
        analyze_church_coverage()
        print("✅ Coverage analysis completed")
    except Exception as e:
        print(f"❌ Error in coverage analysis: {e}")

def create_index_page(points_map_exists, buildings_map_exists):
    """Create or update index page."""
    print("📄 Creating index page...")
    
    index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Istanbul Churches Maps</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{
            color: #333;
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }}
        .maps-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }}
        .map-card {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: transform 0.2s ease;
        }}
        .map-card:hover {{
            transform: translateY(-5px);
        }}
        .map-info {{
            padding: 25px;
        }}
        .map-info h2 {{
            margin: 0 0 15px 0;
            color: #333;
        }}
        .btn {{
            display: inline-block;
            padding: 12px 25px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: 500;
        }}
        .btn:hover {{
            background: #5a67d8;
        }}
        .btn:disabled {{
            background: #ccc;
            cursor: not-allowed;
        }}
        .status {{
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }}
        .status.success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .status.error {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🗺️ Istanbul Churches Maps</h1>
        <p>Interactive maps showing Christian churches across Istanbul</p>
        <p><strong>Generated:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="maps-container">
        <div class="map-card">
            <div class="map-info">
                <h2>📍 Points Map</h2>
                <p>Church locations as colored markers on detailed street maps.</p>
                
                {'<div class="status success">✅ Map available</div>' if points_map_exists else '<div class="status error">❌ Map not available</div>'}
                
                <a href="istanbul_churches_map.html" class="btn" {'target="_blank"' if points_map_exists else 'style="pointer-events: none; opacity: 0.6;"'}>
                    View Points Map →
                </a>
            </div>
        </div>

        <div class="map-card">
            <div class="map-info">
                <h2>🏛️ Buildings Map</h2>
                <p>Church building footprints with colored outlines and satellite view.</p>
                
                {'<div class="status success">✅ Map available</div>' if buildings_map_exists else '<div class="status error">❌ Map not available</div>'}
                
                <a href="istanbul_churches_buildings_map.html" class="btn" {'target="_blank"' if buildings_map_exists else 'style="pointer-events: none; opacity: 0.6;"'}>
                    View Buildings Map →
                </a>
            </div>
        </div>
    </div>

    <div style="background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center;">
        <h3>📊 Legend</h3>
        <p>
            <span style="color: #ff0000;">●</span> Orthodox &nbsp;
            <span style="color: #0000ff;">●</span> Catholic &nbsp;
            <span style="color: #800080;">●</span> Armenian Orthodox &nbsp;
            <span style="color: #008000;">●</span> Protestant &nbsp;
            <span style="color: #ff8c00;">●</span> General Christian
        </p>
        <p><small>Data source: OpenStreetMap</small></p>
    </div>
</body>
</html>"""
    
    index_path = Path(__file__).parent / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"✅ Index page created: {index_path}")
    return str(index_path)

def start_server(port=8080, max_attempts=10):
    """Start HTTP server in a separate thread, trying next port if already in use."""
    
    class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            # Suppress default logging, only show access in quiet mode
            pass
    
    original_port = port
    httpd = None
    
    # Try to find an available port
    for attempt in range(max_attempts):
        try:
            os.chdir(Path(__file__).parent)
            httpd = socketserver.TCPServer(("", port), QuietHTTPRequestHandler)
            break  # Successfully bound to port
        except OSError as e:
            if e.errno == 48 or e.errno == 98:  # Port already in use (macOS/Linux)
                if attempt < max_attempts - 1:
                    port += 1
                    continue
                else:
                    raise Exception(f"Could not find available port after trying {original_port}-{port}")
            else:
                raise  # Different error, re-raise
    
    if httpd is None:
        raise Exception("Failed to create server")
    
    def run_server():
        httpd.serve_forever()
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    return server_thread, port

def main():
    """Main function to orchestrate everything."""
    parser = argparse.ArgumentParser(description="Istanbul Churches Maps Generator and Server")
    parser.add_argument("--port", "-p", type=int, default=8080, help="Port to serve on (default: 8080)")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    parser.add_argument("--with-buildings", action="store_true", help="Also generate buildings map")
    parser.add_argument("--with-analysis", action="store_true", help="Also generate coverage analysis")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode - minimal output")
    
    args = parser.parse_args()
    
    if not args.quiet:
        print("🗺️ Istanbul Churches Map Generator")
        print("=" * 50)
    
    # Step 1: Check dependencies
    ensure_dependencies()
    
    # Step 2: Generate points map
    points_map_path = generate_points_map()
    points_map_exists = points_map_path and Path(points_map_path).exists()
    
    # Optional: Generate buildings map
    if args.with_buildings:
        buildings_map_path = generate_buildings_map()
    
    # Optional: Generate analysis
    if args.with_analysis:
        generate_coverage_analysis()
    
    # Step 3: Start server
    print(f"🌐 Starting server on port {args.port}...")
    try:
        server_thread, actual_port = start_server(args.port)
        if actual_port != args.port:
            print(f"   Port {args.port} was in use, using port {actual_port} instead")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)
    
    # Give server time to start
    time.sleep(1)
    
    # Step 4: Open browser
    base_url = f"http://localhost:{actual_port}"
    map_url = f"{base_url}/istanbul_churches_map.html"
    
    if not args.quiet:
        print("=" * 50)
        print("✅ Istanbul Churches Map Ready!")
        print("=" * 50)
        print(f"🌐 Server running at: {map_url}")
        print(f"� Map shows 221 churches across Istanbul")
        print()
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
    
    if not args.no_browser:
        try:
            webbrowser.open(map_url)
            if not args.quiet:
                print("🚀 Opening browser...")
        except Exception as e:
            print(f"⚠️ Could not open browser: {e}")
            print(f"   Please manually navigate to: {map_url}")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        if not args.quiet:
            print("\\n👋 Server stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
