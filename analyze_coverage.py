#!/usr/bin/env python3
"""
Analysis of church coverage in Istanbul
"""

from istanbul_churches_map import IstanbulChurchesMapper

def analyze_church_coverage():
    """Analyze the church coverage across Istanbul."""
    print("🗺️ Istanbul Churches Coverage Analysis")
    print("=" * 50)
    
    mapper = IstanbulChurchesMapper()
    churches = mapper.fetch_churches_from_overpass()
    
    print(f"Total churches found: {len(churches)}")
    print()
    
    # Analyze by area/district
    print("📍 Geographic Distribution:")
    
    # Define area boundaries for analysis
    areas = {
        'Historical Peninsula': (40.99, 28.94, 41.02, 28.98),  # Sultanahmet, Eminönü
        'Beyoğlu/Galata': (41.02, 28.97, 41.04, 28.99),       # Beyoğlu, Karaköy
        'Fatih District': (41.00, 28.92, 41.02, 28.96),       # Fener, Balat
        'Üsküdar (Asian)': (41.01, 29.01, 41.03, 29.04),      # Asian side center
        'Kadıköy (Asian)': (40.98, 29.02, 41.00, 29.05),      # Asian side south
        'Northern European': (41.08, 28.95, 41.15, 29.10),    # Sarıyer, Beykoz
        'Western Suburbs': (40.95, 28.60, 41.05, 28.80),      # Avcılar, Beylikdüzü
        'Eastern Asian': (40.85, 29.15, 41.00, 29.40),        # Pendik, Tuzla
        'Princes Islands': (40.84, 29.06, 40.91, 29.15),      # Adalar
    }
    
    for area_name, (south, west, north, east) in areas.items():
        count = 0
        area_churches = []
        
        for church in churches:
            lat, lon = church['coordinates']
            if south <= lat <= north and west <= lon <= east:
                count += 1
                area_churches.append(church['name'])
        
        print(f"  {area_name:20}: {count:3d} churches")
        if count > 0 and count <= 5:  # Show names for smaller areas
            for name in area_churches[:3]:
                print(f"    - {name}")
            if len(area_churches) > 3:
                print(f"    ... and {len(area_churches)-3} more")
    
    # Analyze by denomination
    print("\n⛪ Denomination Distribution:")
    denominations = {}
    for church in churches:
        denom = church.get('denomination', 'Unknown')
        # Normalize denomination names
        if 'orthodox' in denom.lower():
            denom = 'Orthodox'
        elif 'catholic' in denom.lower():
            denom = 'Catholic'
        elif 'armenian' in denom.lower():
            denom = 'Armenian Orthodox'
        elif 'protestant' in denom.lower():
            denom = 'Protestant'
        elif denom.lower() == 'christian':
            denom = 'General Christian'
        
        denominations[denom] = denominations.get(denom, 0) + 1
    
    for denom, count in sorted(denominations.items(), key=lambda x: x[1], reverse=True):
        print(f"  {denom:20}: {count:3d} churches")
    
    # Coverage statistics
    print(f"\n📊 Coverage Statistics:")
    print(f"  Bounding Box: 40.8°N to 41.4°N, 28.4°E to 29.8°E")
    print(f"  Area Coverage: ~1,400 km² (full Istanbul metropolitan)")
    print(f"  Includes Islands: Yes (Princes' Islands)")
    print(f"  Both Continents: Yes (European + Asian sides)")
    
    # Find interesting churches
    print(f"\n🏛️ Notable Churches Found:")
    notable = []
    for church in churches:
        name = church['name'].lower()
        if any(keyword in name for keyword in ['hagia', 'sophia', 'cathedral', 'patriarchate', 'saint', 'holy']):
            notable.append(church['name'])
    
    for name in sorted(notable)[:10]:  # Show first 10
        print(f"  - {name}")
    if len(notable) > 10:
        print(f"  ... and {len(notable)-10} more notable churches")

if __name__ == "__main__":
    analyze_church_coverage()
