#!/usr/bin/env python3
"""
Fetch weather data from FMI Open Data API for Kaisaniemi, Helsinki.
"""
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# FMI API endpoint
FMI_API_URL = "https://opendata.fmi.fi/wfs"

# Kaisaniemi, Helsinki coordinates (latitude, longitude)
KAISANIEMI_COORDS = "60.1699,24.9384"

# Parameters to fetch
def get_weather_parameters() -> Dict[str, str]:
    """Return a dictionary of weather parameters and their descriptions."""
    return {
        "t2m": "Temperature at 2m height (°C)",
        "rh": "Relative humidity (%)",
        "ws_10min": "Wind speed at 10m (m/s)",
        "wd_10min": "Wind direction at 10m (°)",
        "r_1h": "Precipitation amount (mm)",
        "td": "Dew point temperature (°C)",
        "p_sea": "Pressure at sea level (hPa)",
        "vis": "Visibility (m)",
        "n_man": "Cloud cover (0-8)",
        "wawa": "Weather code (WMO code 4680)"
    }

def fetch_weather_data(location: str, start_time: str, end_time: str) -> Optional[Dict]:
    """
    Fetch weather data from FMI API for the specified location and time range.
    
    Args:
        location: Place name or coordinates (lat,lon)
        start_time: Start time in ISO format (YYYY-MM-DDTHH:MM:SSZ)
        end_time: End time in ISO format (YYYY-MM-DDTHH:MM:SSZ)
        
    Returns:
        Dictionary containing the weather data or None if request fails
    """
    # Get parameter names
    parameters = ",".join(get_weather_parameters().keys())
    
    # Prepare request parameters
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "getFeature",
        "storedquery_id": "fmi::observations::weather::simple",
        "place": location,
        "starttime": start_time,
        "endtime": end_time,
        "timestep": 60,  # 60 minutes between observations
        "parameters": parameters
    }
    
    try:
        response = requests.get(FMI_API_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}", file=sys.stderr)
        return None

def parse_weather_data(xml_data: str) -> List[Dict]:
    """
    Parse XML weather data into a list of observation dictionaries.
    
    Args:
        xml_data: Raw XML response from FMI API
        
    Returns:
        List of observation dictionaries
    """
    import xml.etree.ElementTree as ET
    from datetime import datetime
    
    # Parse the XML data
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        print(f"Error parsing XML data: {e}", file=sys.stderr)
        return []
    
    # Define namespace dictionary
    namespaces = {
        'wfs': 'http://www.opengis.net/wfs/2.0',
        'BsWfs': 'http://xml.fmi.fi/schema/wfs/2.0',
        'gml': 'http://www.opengis.net/gml/3.2'
    }
    
    # Register namespaces for easier access
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)
    
    observations = {}
    
    # Find all BsWfsElement elements
    for element in root.findall('.//BsWfs:BsWfsElement', namespaces=namespaces):
        try:
            # Extract common fields
            time_elem = element.find('BsWfs:Time', namespaces)
            param_elem = element.find('BsWfs:ParameterName', namespaces)
            value_elem = element.find('BsWfs:ParameterValue', namespaces)
            
            if time_elem is not None and param_elem is not None and value_elem is not None:
                time = time_elem.text
                param = param_elem.text
                try:
                    value = float(value_elem.text)
                except (ValueError, TypeError):
                    value = value_elem.text
                
                # Group observations by timestamp
                if time not in observations:
                    observations[time] = {'time': time}
                    
                # Add parameter value to the observation
                observations[time][param] = value
                
        except Exception as e:
            print(f"Warning: Could not parse measurement: {e}", file=sys.stderr)
    
    # Convert to list sorted by time
    sorted_obs = sorted(observations.values(), key=lambda x: x['time'])
    
    # Limit to the most recent 5 observations
    return sorted_obs[-5:]

def format_weather_data(observations: List[Dict]) -> str:
    """
    Format weather observations into a human-readable string.
    
    Args:
        observations: List of observation dictionaries
        
    Returns:
        Formatted weather data string
    """
    if not observations:
        return "No weather data available."
    
    # Get parameter descriptions
    param_descriptions = get_weather_parameters()
    
    # Format each observation
    formatted = []
    for obs in observations[-5:]:  # Show only the last 5 observations
        time_str = datetime.fromisoformat(obs['time'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
        obs_str = [f"\n{time_str}:"]
        
        for param, desc in param_descriptions.items():
            if param in obs:
                obs_str.append(f"  - {desc}: {obs[param]}")
        
        formatted.append("\n".join(obs_str))
    
    return "\n".join(formatted)

def main():
    """Main function to fetch and display weather data."""
    # Set time range (last 24 hours)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
    
    # Format times for API
    time_format = "%Y-%m-%dT%H:%M:%SZ"
    start_str = start_time.strftime(time_format)
    end_str = end_time.strftime(time_format)
    
    print(f"Fetching weather data for Kaisaniemi, Helsinki...")
    print(f"Time range: {start_str} to {end_str}\n")
    
    # Fetch weather data
    xml_data = fetch_weather_data("Kaisaniemi,Helsinki", start_str, end_str)
    
    if not xml_data:
        print("Failed to fetch weather data.")
        sys.exit(1)
    
    # Parse and format the data
    observations = parse_weather_data(xml_data)
    formatted_data = format_weather_data(observations)
    
    print("Latest Weather Observations for Kaisaniemi, Helsinki:")
    print(formatted_data)

if __name__ == "__main__":
    main()
