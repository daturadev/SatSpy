# SatViz

A satellite tracking and visualization application for real-time satellite intelligence collection and data aggregation. This project provides positional data, ground tracks, and pass predictions through a clean web-based interface.

![SatViz Dashboard](https://github.com/user-attachments/assets/e1442e81-7056-49e2-bf5b-e510f4a1100e)

## Features

### 🛰️ TLE Fetch & Orbit Propagation
- Automatic TLE (Two-Line Element) fetching from CelesTrak
- SGP4 orbit propagation using Skyfield library
- Configurable TLE sources and satellite filters
- Fallback TLE data for offline operation
- Support for up to 150 satellites

### 🗺️ Live Map with Ground Tracks
- Interactive world map showing real-time satellite positions
- Ground track visualization (90-minute default)
- Auto-refresh every 60 seconds
- Displays up to 15 satellites with ground tracks
- Plotly-based interactive visualization

### 📡 Pass Predictor
- Next pass timing predictions for 24-hour window
- Acquisition of Signal (AOS) and Loss of Signal (LOS) times
- Pass duration calculation
- Configurable minimum elevation threshold (default 20°)
- Pass geometry with elevation and azimuth data
- Shows top 2 passes per satellite

## Installation

1. Clone the repository:
```bash
git clone https://github.com/daturadev/SatSpy.git
cd SatSpy
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your observer location:
```bash
cp config.example.json config.json
# Edit config.json with your latitude, longitude, and elevation
```

## Usage

Run the application:
```bash
python app.py
```

The dashboard will be available at: `http://127.0.0.1:8050/`

## Configuration

Edit `config.json` to customize:

- **observer**: Your location (lat, lon, elev_m)
- **tle_sources**: URLs for TLE data sources
- **satellite_filters**: Filter by satellite name (e.g., "ISS", "NOAA", "METEOR")
- **groundtrack_minutes**: Length of ground track to display (default: 90)
- **min_elevation_deg**: Minimum elevation for pass predictions (default: 20)
- **max_sats**: Maximum number of satellites to track (default: 150)

## Technologies

- **Python 3.12+**
- **Skyfield**: Astronomical computations and SGP4 propagation
- **Dash & Plotly**: Interactive web dashboard
- **Pandas**: Data processing
- **Requests**: TLE data fetching

---

## Development History

### Sprint - 08292025
<img width="1908" height="894" alt="Progress Report 2025-08-29" src="https://github.com/user-attachments/assets/c56eece9-c500-4397-bb8c-8c164b7542d8" />

- Created a web dashboard in which to visualize satellite data
- Still manual entry, looking to update in real-time
- A bit of numerical data presented on dash
- Overcame a few hurdles with Dash import

### Current Release
- ✅ Implemented automatic TLE fetching
- ✅ Real-time orbit propagation
- ✅ Live map with satellite ground tracks
- ✅ Pass predictor with timing and geometry
