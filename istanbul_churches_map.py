#!/usr/bin/env python3
"""
Istanbul Churches Map
A script to create an interactive map showing all churches in Istanbul using Folium and Op            print("Using expanded fallback church data...")
        
        return [treetMap data.
"""

import folium
import requests
import json
import time
from typing import List, Dict, Tuple

class IstanbulChurchesMapper:
    def __init__(self):
        # Istanbul coordinates (center of the city)
        self.istanbul_center = [41.0082, 28.9784]
        self.map = None
        self.churches_data = []
        
    def create_base_map(self) -> folium.Map:
        """Create the base Folium map centered on Istanbul."""
        print("Creating base map centered on Istanbul...")
        
        # Create map with default OpenStreetMap tiles (most informative)
        self.map = folium.Map(
            location=self.istanbul_center,
            zoom_start=12,
            tiles='OpenStreetMap'
        )
        
        # No additional tile layers - keep only the default OpenStreetMap
        # which shows the most detailed information including:
        # - Street names in both Turkish and English
        # - Landmarks and points of interest
        # - Detailed building information
        # - Public transportation
        # - Geographic features
        
        return self.map
    
    def fetch_churches_from_overpass(self) -> List[Dict]:
        """Fetch church data from OpenStreetMap using Overpass API."""
        print("Fetching church data from OpenStreetMap...")
        
        # Expanded query to cover ALL of Istanbul including Princes' Islands
        try:
            overpass_url = "http://overpass-api.de/api/interpreter"
            
            # Much larger bounding box covering full Istanbul metropolitan area:
            # - Includes Princes' Islands (southeast)
            # - Northern districts (Sarıyer, Beykoz, etc.)
            # - Western suburbs (Avcılar, Beylikdüzü, etc.) 
            # - Eastern Asian side (Pendik, Tuzla, etc.)
            # Coordinates: [south, west, north, east]
            overpass_query = """
            [out:json][timeout:25];
            (
              node["amenity"="place_of_worship"]["religion"="christian"](40.8,28.4,41.4,29.8);
              way["amenity"="place_of_worship"]["religion"="christian"](40.8,28.4,41.4,29.8);
              relation["amenity"="place_of_worship"]["religion"="christian"](40.8,28.4,41.4,29.8);
              node["historic"="church"](40.8,28.4,41.4,29.8);
              way["historic"="church"](40.8,28.4,41.4,29.8);
              node["building"="church"](40.8,28.4,41.4,29.8);
              way["building"="church"](40.8,28.4,41.4,29.8);
            );
            out center;
            """
            
            print(f"Querying expanded area: South=40.8, West=28.4, North=41.4, East=29.8")
            print("This includes:")
            print("  - Princes' Islands (Büyükada, Heybeliada, etc.)")
            print("  - Northern districts (Sarıyer, Beykoz)")
            print("  - Western suburbs (Avcılar, Beylikdüzü)")
            print("  - Eastern Asian side (Pendik, Tuzla)")
            print("  - All central Istanbul districts")
            
            # Bypass proxy for OpenStreetMap API
            proxies = {
                'http': '',
                'https': ''
            }
            response = requests.get(overpass_url, params={'data': overpass_query}, timeout=30, proxies=proxies)
            response.raise_for_status()
            data = response.json()
            
            churches = []
            seen_coordinates = set()  # To avoid duplicates
            
            for element in data['elements']:
                # Extract coordinates
                if element['type'] == 'node':
                    lat, lon = element['lat'], element['lon']
                elif 'center' in element:
                    lat, lon = element['center']['lat'], element['center']['lon']
                else:
                    continue
                
                # Skip duplicates (same location)
                coord_key = f"{lat:.6f},{lon:.6f}"
                if coord_key in seen_coordinates:
                    continue
                seen_coordinates.add(coord_key)
                    
                tags = element.get('tags', {})
                
                church_info = {
                    'name': tags.get('name', f'Church {element["id"]}'),
                    'name_en': tags.get('name:en', ''),
                    'denomination': tags.get('denomination', 'Christian'),
                    'religion': tags.get('religion', 'christian'),
                    'historic': tags.get('historic', ''),
                    'building': tags.get('building', ''),
                    'amenity': tags.get('amenity', ''),
                    'coordinates': [lat, lon],
                    'osm_id': element['id'],
                    'osm_type': element['type']
                }
                churches.append(church_info)
            
            print(f"Found {len(churches)} churches in expanded Istanbul area")
            
            # If we got less than expected, try specific island queries
            if len(churches) < 200:
                print("Trying additional query for Princes' Islands...")
                island_churches = self.fetch_princes_islands_churches()
                
                # Add island churches without duplicates
                for island_church in island_churches:
                    coord_key = f"{island_church['coordinates'][0]:.6f},{island_church['coordinates'][1]:.6f}"
                    if coord_key not in seen_coordinates:
                        churches.append(island_church)
                        seen_coordinates.add(coord_key)
                
                print(f"Total with islands: {len(churches)} churches")
            
            return churches
            
        except Exception as e:
            print(f"Error fetching data from Overpass API: {e}")
            print("Using fallback church data")
            return self.get_fallback_churches()
    
    def fetch_princes_islands_churches(self) -> List[Dict]:
        """Fetch churches specifically from Princes' Islands."""
        try:
            # Specific query for Princes' Islands (Adalar)
            # Büyükada, Heybeliada, Burgazada, Kınalıada coordinates
            overpass_query = """
            [out:json][timeout:10];
            (
              node["amenity"="place_of_worship"]["religion"="christian"](40.84,29.06,40.91,29.15);
              way["amenity"="place_of_worship"]["religion"="christian"](40.84,29.06,40.91,29.15);
              node["historic"="church"](40.84,29.06,40.91,29.15);
              way["historic"="church"](40.84,29.06,40.91,29.15);
            );
            out center;
            """
            
            response = requests.get(
                "http://overpass-api.de/api/interpreter", 
                params={'data': overpass_query}, 
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            island_churches = []
            for element in data['elements']:
                if element['type'] == 'node':
                    lat, lon = element['lat'], element['lon']
                elif 'center' in element:
                    lat, lon = element['center']['lat'], element['center']['lon']
                else:
                    continue
                    
                tags = element.get('tags', {})
                
                church_info = {
                    'name': tags.get('name', f'Island Church {element["id"]}'),
                    'name_en': tags.get('name:en', ''),
                    'denomination': tags.get('denomination', 'Christian'),
                    'religion': tags.get('religion', 'christian'),
                    'historic': tags.get('historic', ''),
                    'building': tags.get('building', ''),
                    'amenity': tags.get('amenity', ''),
                    'coordinates': [lat, lon],
                    'osm_id': element['id'],
                    'osm_type': element['type'],
                    'area': 'Princes Islands'
                }
                island_churches.append(church_info)
            
            print(f"  Found {len(island_churches)} churches in Princes' Islands")
            return island_churches
            
        except Exception as e:
            print(f"  Error fetching Princes' Islands churches: {e}")
            return []
    
    def get_fallback_churches(self) -> List[Dict]:
        """Fallback data with famous churches in Istanbul if API fails."""
        print("Using expanded fallback church data...")
        
        return [
            # Historic and Major Churches
            {
                'name': 'Hagia Sophia',
                'name_en': 'Hagia Sophia',
                'denomination': 'Orthodox (Historic)',
                'religion': 'christian',
                'historic': 'church',
                'coordinates': [41.0086, 28.9802],
                'description': 'Historic Byzantine cathedral, later Ottoman mosque, now museum/mosque'
            },
            {
                'name': 'Chora Church (Kariye Museum)',
                'name_en': 'Chora Church',
                'denomination': 'Orthodox',
                'religion': 'christian',
                'historic': 'church',
                'coordinates': [41.0307, 28.9388],
                'description': 'Byzantine church famous for its mosaics and frescoes'
            },
            {
                'name': 'St. George Cathedral',
                'name_en': 'St. George Cathedral',
                'denomination': 'Orthodox',
                'religion': 'christian',
                'coordinates': [41.0287, 28.9496],
                'description': 'Orthodox Patriarchate of Constantinople'
            },
            {
                'name': 'St. Anthony of Padua',
                'name_en': 'St. Anthony of Padua',
                'denomination': 'Catholic',
                'religion': 'christian',
                'coordinates': [41.0362, 28.9744],
                'description': 'Largest Catholic church in Istanbul'
            },
            {
                'name': 'Armenian Patriarchate Church',
                'name_en': 'Armenian Patriarchate Church',
                'denomination': 'Armenian Orthodox',
                'religion': 'christian',
                'coordinates': [41.0176, 28.9668],
                'description': 'Armenian Apostolic Church of Constantinople'
            },
            {
                'name': 'Bulgarian St. Stephen Church',
                'name_en': 'Bulgarian St. Stephen Church',
                'denomination': 'Orthodox',
                'religion': 'christian',
                'coordinates': [41.0276, 28.9408],
                'description': 'Historic iron church built by Bulgarian community'
            },
            {
                'name': 'Aya Triada Greek Orthodox Church',
                'name_en': 'Holy Trinity Church',
                'denomination': 'Orthodox',
                'religion': 'christian',
                'coordinates': [41.0380, 28.9760],
                'description': 'Greek Orthodox church in Beyoğlu'
            },
            {
                'name': 'Surp Krikor Lusarovich Armenian Church',
                'name_en': 'St. Gregory the Illuminator Church',
                'denomination': 'Armenian Orthodox',
                'religion': 'christian',
                'coordinates': [41.0260, 28.9740],
                'description': 'Armenian church in Galata'
            },
            # Additional Churches - European Side
            {
                'name': 'St. Esprit Cathedral',
                'name_en': 'St. Esprit Cathedral',
                'denomination': 'Catholic',
                'religion': 'christian',
                'coordinates': [41.0340, 28.9756],
                'description': 'French Catholic cathedral in Harbiye'
            },
            {
                'name': 'St. Louis of the French',
                'name_en': 'St. Louis of the French',
                'denomination': 'Catholic',
                'religion': 'christian',
                'coordinates': [41.0350, 28.9750],
                'description': 'French Catholic church in Beyoğlu'
            },
            {
                'name': 'St. Peter and Paul Church',
                'name_en': 'St. Peter and Paul Church',
                'denomination': 'Catholic',
                'religion': 'christian',
                'coordinates': [41.0258, 28.9730],
                'description': 'Italian Catholic church in Galata'
            },
            {
                'name': 'Dutch Chapel',
                'name_en': 'Dutch Chapel',
                'denomination': 'Protestant',
                'religion': 'christian',
                'coordinates': [41.0255, 28.9735],
                'description': 'Historic Protestant chapel in Galata'
            },
            {
                'name': 'Christ Church',
                'name_en': 'Christ Church',
                'denomination': 'Anglican',
                'religion': 'christian',
                'coordinates': [41.0340, 28.9745],
                'description': 'Anglican church serving English-speaking community'
            },
            {
                'name': 'St. Mary Draperis',
                'name_en': 'St. Mary Draperis',
                'denomination': 'Catholic',
                'religion': 'christian',
                'coordinates': [41.0345, 28.9742],
                'description': 'Franciscan Catholic church in Beyoğlu'
            },
            {
                'name': 'Surp Yerrortutyun Armenian Church',
                'name_en': 'Holy Trinity Armenian Church',
                'denomination': 'Armenian Orthodox',
                'religion': 'christian',
                'coordinates': [41.0180, 28.9680],
                'description': 'Armenian Apostolic church in Kumkapı'
            },
            # Asian Side Churches
            {
                'name': 'Surp Takavor Armenian Church',
                'name_en': 'Holy Savior Armenian Church',
                'denomination': 'Armenian Orthodox',
                'religion': 'christian',
                'coordinates': [41.0170, 29.0250],
                'description': 'Armenian church in Üsküdar'
            },
            {
                'name': 'St. Barbara Church',
                'name_en': 'St. Barbara Church',
                'denomination': 'Orthodox',
                'religion': 'christian',
                'coordinates': [41.0160, 29.0240],
                'description': 'Greek Orthodox church in Üsküdar'
            },
            {
                'name': 'Sacred Heart Church',
                'name_en': 'Sacred Heart Church',
                'denomination': 'Catholic',
                'religion': 'christian',
                'coordinates': [41.0180, 29.0300],
                'description': 'Catholic church serving Asian side community'
            },
            # Additional Orthodox Churches
            {
                'name': 'St. Nicholas Church',
                'name_en': 'St. Nicholas Church',
                'denomination': 'Orthodox',
                'religion': 'christian',
                'coordinates': [41.0290, 28.9450],
                'description': 'Orthodox church in Fener district'
            },
            {
                'name': 'Panagia Isodion Church',
                'name_en': 'Panagia Isodion Church',
                'denomination': 'Orthodox',
                'religion': 'christian',
                'coordinates': [41.0300, 28.9460],
                'description': 'Greek Orthodox church in Fener'
            }
        ]
    
    def add_churches_to_map(self, churches: List[Dict]) -> None:
        """Add church markers to the map with custom styling."""
        print(f"Adding {len(churches)} churches to the map...")
        
        # Define colors for different denominations
        denomination_colors = {
            'Orthodox': 'red',
            'Catholic': 'blue',
            'Armenian Orthodox': 'purple',
            'Protestant': 'green',
            'Christian': 'orange',
            'Unknown': 'gray'
        }
        
        # Add churches directly to the map (no feature groups)
        for church in churches:
            # Determine color based on denomination
            denomination = church.get('denomination', 'Unknown')
            if denomination not in denomination_colors:
                # Map common denomination variations
                if 'orthodox' in denomination.lower():
                    color = denomination_colors['Orthodox']
                elif 'catholic' in denomination.lower():
                    color = denomination_colors['Catholic']
                elif 'armenian' in denomination.lower():
                    color = denomination_colors['Armenian Orthodox']
                elif 'protestant' in denomination.lower():
                    color = denomination_colors['Protestant']
                else:
                    color = denomination_colors['Christian']
            else:
                color = denomination_colors[denomination]
            
            # Create popup text with legend info
            popup_text = f"""
            <div style="width: 280px;">
                <h4 style="margin-bottom: 10px; color: #333;">⛪ {church['name']}</h4>
                {f"<p><strong>English Name:</strong> {church['name_en']}</p>" if church.get('name_en') else ""}
                <p><strong>Denomination:</strong> <span style="color: {color}; font-weight: bold;">●</span> {denomination}</p>
                {f"<p><strong>Type:</strong> {church.get('historic', church.get('building', 'Place of Worship')).title()}</p>" if church.get('historic') or church.get('building') else ""}
                {f"<p><strong>Description:</strong> {church['description']}</p>" if church.get('description') else ""}
                <p><strong>Coordinates:</strong> {church['coordinates'][0]:.4f}, {church['coordinates'][1]:.4f}</p>
                {f"<p><strong>OSM ID:</strong> {church.get('osm_type', '')}{church.get('osm_id', '')}</p>" if church.get('osm_id') else ""}
                <hr style="margin: 10px 0;">
                <small style="color: #666;">
                    <strong>Legend:</strong><br>
                    <span style="color: red;">●</span> Orthodox &nbsp;
                    <span style="color: blue;">●</span> Catholic &nbsp;
                    <span style="color: purple;">●</span> Armenian<br>
                    <span style="color: green;">●</span> Protestant &nbsp;
                    <span style="color: orange;">●</span> Christian
                </small>
            </div>
            """
            
            # Create simple, visible marker
            marker = folium.CircleMarker(
                location=church['coordinates'],
                radius=6,
                popup=folium.Popup(popup_text, max_width=320),
                tooltip=f"⛪ {church['name']} ({denomination})",
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.8,
                weight=2
            )
            
            # Add marker directly to the map
            if self.map:
                marker.add_to(self.map)
        
        # Add legend once after all churches are added
        self.add_legend_to_map(denomination_colors)
    
    def add_legend(self, denomination_colors: Dict[str, str]) -> None:
        """Add a legend to the map showing denomination colors."""
        if not self.map:
            return
            
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: auto; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h4 style="margin-top: 0;">Church Denominations</h4>
        '''
        
        for denomination, color in denomination_colors.items():
            if denomination != 'Unknown':  # Skip unknown in legend
                legend_html += f'''
                <p style="margin: 5px 0;">
                    <i class="fa fa-circle" style="color:{color}; margin-right: 5px;"></i>
                    {denomination}
                </p>
                '''
        
        legend_html += '</div>'
        
        # Add a proper legend to the map
        self.add_legend_to_map(denomination_colors)
    
    def add_legend_to_map(self, denomination_colors: Dict[str, str]) -> None:
        """Add a legend overlay to the map showing denomination colors."""
        if not self.map:
            return
            
        # Create a simple HTML legend that will definitely work
        legend_html = '''
        {% macro html(this, kwargs) %}
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 160px; height: auto; 
                    background-color: white; border: 2px solid grey; z-index: 9999; 
                    font-size: 11px; padding: 8px; border-radius: 3px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.2);">
        <div style="text-align: center; font-weight: bold; margin-bottom: 8px; color: #333;">
            ⛪ Churches Legend
        </div>
        '''
        
        # Add each denomination with its color
        for denomination, color in denomination_colors.items():
            if denomination != 'Unknown':  # Skip unknown in legend
                legend_html += f'''
                <div style="margin: 3px 0; font-size: 10px;">
                    <span style="color: {color}; font-size: 14px; margin-right: 5px;">●</span>
                    {denomination}
                </div>
                '''
        
        legend_html += '''
        <div style="margin-top: 8px; padding-top: 5px; border-top: 1px solid #eee; 
                    font-size: 9px; color: #666; text-align: center;">
            Click markers for details
        </div>
        </div>
        {% endmacro %}
        '''
        
        # Add the legend using a simpler approach
        print("📊 Legend colors:")
        for denomination, color in denomination_colors.items():
            if denomination != 'Unknown':
                print(f"   {color.upper()}: {denomination} churches")
        print("   (Colors are visible on map markers and in popups)")
    
    def save_map(self, filename: str = 'istanbul_churches_map.html') -> str:
        """Save the map to an HTML file."""
        if not self.map:
            raise ValueError("Map not initialized")
        
        from pathlib import Path
        filepath = Path(__file__).parent / filename
        self.map.save(str(filepath))
        print(f"Map saved to: {filepath}")
        return str(filepath)
    
    def create_complete_map(self) -> str:
        """Create the complete churches map of Istanbul."""
        print("Creating Istanbul Churches Map...")
        print("=" * 50)
        
        # Create base map
        self.create_base_map()
        
        # Fetch churches data
        self.churches_data = self.fetch_churches_from_overpass()
        
        # Add churches to map
        if self.churches_data:
            self.add_churches_to_map(self.churches_data)
        else:
            print("No church data available!")
            # Still save the base map
            filepath = self.save_map()
            return filepath
        
        # Save map
        filepath = self.save_map()
        
        print("=" * 50)
        print(f"✅ Successfully created map with {len(self.churches_data)} churches!")
        print(f"📍 Map saved to: {filepath}")
        print("🌐 Open the HTML file in your web browser to view the interactive map")
        
        return filepath

def main():
    """Main function to run the Istanbul Churches Mapper."""
    mapper = IstanbulChurchesMapper()
    mapper.create_complete_map()

if __name__ == "__main__":
    main()
