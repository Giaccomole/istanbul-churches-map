# Istanbul Churches Map 🗺️⛪

An interactive map visualization of churches in Istanbul, Turkey, built with Python and Folium.

## Overview

This project creates an interactive HTML map that displays all churches in Istanbul color-coded denominations. The data is fetched from OpenStreetMap using the Overpass API.

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Giaccomole/istanbul-churches-map.git
   cd istanbul-churches-map
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate     # On Windows
   ```

3. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Start (Recommended)

Run the main script to generate all maps and start a local server:

```bash
python main.py
```

This will:
1. Generate both points and buildings maps
2. Create an index page
3. Start a local web server
4. Open your browser automatically

**Command line options:**
```bash
python main.py --help                    # Show all options
python main.py --port 8080               # Use specific port
python main.py --with-buildings          # Also generate buildings map
python main.py --with-analysis           # Also generate coverage analysis
python main.py --quiet                   # Minimal output
python main.py --no-browser              # Don't open browser
```

### Individual Scripts

Generate only the points map:
```bash
python istanbul_churches_map.py
```

Generate coverage analysis:
```bash
python analyze_coverage.py
```

### Advanced Usage

You can also use the mapper class in your own code:

```python
from istanbul_churches_map import IstanbulChurchesMapper

# Create mapper instance
mapper = IstanbulChurchesMapper()

# Generate complete map
filepath = mapper.create_complete_map()

# Or build step by step
mapper.create_base_map()
churches = mapper.fetch_churches_from_overpass()
mapper.add_churches_to_map(churches)
mapper.save_map("my_custom_map.html")
```

## Output

The script generates an HTML file (`istanbul_churches_map.html`) containing:

- **Interactive Map**: Centered on Istanbul with zoom controls
- **Church Markers**: Color-coded by denomination
  - 🔴 **Red**: Orthodox churches
  - 🔵 **Blue**: Catholic churches  
  - 🟣 **Purple**: Armenian Orthodox churches
  - 🟢 **Green**: Protestant churches
  - 🟠 **Orange**: General Christian churches
- **Popups**: Click any marker to see detailed information
- **Tooltips**: Hover over markers to see church names
- **Legend**: Shows denomination color coding
- **Layer Control**: Switch between different map styles

## Church Data

The script fetches data from OpenStreetMap including:

- **Official Churches**: `amenity=place_of_worship` + `religion=christian`
- **Historic Churches**: `historic=church`
- **Church Buildings**: `building=church`

### Data Fields
- Church name (in Turkish and English when available)
- Religious denomination
- Geographic coordinates
- Building/historic type
- OpenStreetMap ID for reference

### Coverage Area
The script covers the greater Istanbul metropolitan area (bounding box: 40.8°N to 41.3°N, 28.5°E to 29.5°E).

## Technical Details

### Dependencies
- **folium**: Interactive map generation
- **requests**: HTTP requests for API calls
- **pandas**: Data manipulation (if needed)
- **overpy**: Alternative Overpass API client

### Data Source
- **OpenStreetMap**: Via Overpass API
- **Fallback Data**: Manually curated list of major churches

### Map Features
- **Base Map**: OpenStreetMap tiles
- **Additional Layers**: Stamen Terrain, CartoDB Positron
- **Markers**: FontAwesome church icons
- **Popups**: HTML-formatted information boxes

## Customization

### Modifying the Search Area

Edit the bounding box coordinates in `fetch_churches_from_overpass()`:

```python
# Current: Istanbul area
(40.8,28.5,41.3,29.5)

# Change to your desired area
(min_lat, min_lon, max_lat, max_lon)
```

### Adding Custom Churches

Add churches to the `get_fallback_churches()` method:

```python
{
    'name': 'Your Church Name',
    'name_en': 'English Name',
    'denomination': 'Catholic',  # or Orthodox, Protestant, etc.
    'religion': 'christian',
    'coordinates': [latitude, longitude],
    'description': 'Description of the church'
}
```

### Changing Map Style

Modify the map initialization in `create_base_map()`:

```python
self.map = folium.Map(
    location=self.istanbul_center,
    zoom_start=12,  # Adjust zoom level
    tiles='CartoDB positron'  # Change default tiles
)
```

## License

This project is open source. The church data comes from OpenStreetMap, which is available under the Open Database License.

## Acknowledgments

- **OpenStreetMap**: For providing the church location data
- **Folium**: For the excellent mapping library
- **Overpass API**: For enabling efficient OpenStreetMap queries
- **FontAwesome**: For the church icons

---

**Note**: This map is for educational and informational purposes. Church information is sourced from OpenStreetMap and may not be complete or entirely up-to-date. For the most current information about specific churches, please contact them directly.
