import json, math, time, io
from datetime import datetime, timezone, timedelta

import sys
import pandas as pd
import requests
from skyfield.api import Loader, wgs84, EarthSatellite
from skyfield.api import utc
from skyfield.timelib import Time
from dash import Dash, html, dcc, Input, Output

import plotly.graph_objects as go
import dash
# Initialize Dash
app = Dash(__name__)
print("dash __path__ ->", getattr(dash, "__path_", None))


# ---------------- Config ----------------
CFG_PATH = "config.json"
DEFAULT_CFG = "config.example.json"

def load_cfg():
    try:
        with open(CFG_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        with open(DEFAULT_CFG, "r") as f:
            return json.load(f)

cfg = load_cfg()
LAT = cfg["observer"]["lat"]
LON = cfg["observer"]["lon"]
ELEV = cfg["observer"].get("elev_m", 0.0)
TLE_SOURCES = cfg["tle_sources"]
FILTERS = [f.lower() for f in cfg.get("satellite_filters", [])]
GTRACK_MIN = int(cfg.get("groundtrack_minutes", 90))
MIN_EL = float(cfg.get("min_elevation_deg", 20))
MAX_SATS = int(cfg.get("max_sats", 150))

# ---------------- TLE fetch ----------------
def fetch_tles():
    blocks = []
    for url in TLE_SOURCES:
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            text = r.text.strip().splitlines()
            # parse three-line blocks
            for i in range(0, len(text)-2, 3):
                name, l1, l2 = text[i].strip(), text[i+1].strip(), text[i+2].strip()
                if name and l1.startswith("1 ") and l2.startswith("2 "):
                    if not FILTERS or any(k in name.lower() for k in FILTERS):
                        blocks.append((name, l1, l2))
        except Exception:
            continue
    if not blocks:
        # tiny fallback if offline
        blocks = [
            ("ISS (ZARYA)",
             "1 25544U 98067A   24175.51083333  .00016717  00000+0  10361-3 0  9990",
             "2 25544  51.6417 210.5607 0006040  61.8232  61.7964 15.50000000300000"),
        ]
    return blocks

# ---------------- Propagation helpers ----------------
load = Loader(".skyfield")
ts = load.timescale()

def sats_from_tle(blocks):
    sats = []
    for (name, l1, l2) in blocks[:MAX_SATS]:
        try:
            sats.append(EarthSatellite(l1, l2, name, ts))
        except Exception:
            pass
    return sats

def subpoint_df(sats, t: Time):
    rows = []
    for s in sats:
        try:
            g = s.at(t).subpoint()
            rows.append({
                "name": s.name,
                "lat": g.latitude.degrees,
                "lon": g.longitude.degrees
            })
        except Exception:
            continue
    return pd.DataFrame(rows)

def groundtrack_for_sat(sat: EarthSatellite, t0: Time, minutes=90, step_sec=30):
    points = []
    steps = int(minutes * 60 / step_sec)
    for k in range(steps):
        tk = ts.from_datetime((t0.utc_datetime() + timedelta(seconds=k*step_sec)).replace(tzinfo=timezone.utc))
        g = sat.at(tk).subpoint()
        points.append((g.latitude.degrees, g.longitude.degrees))
    return points

def next_passes(sat: EarthSatellite, obs, start_dt_utc, horizon_deg=10, window_hours=24):
    # Simple elevation threshold pass finder
    passes = []
    dt = start_dt_utc
    end = start_dt_utc + timedelta(hours=window_hours)
    step = timedelta(seconds=30)
    last_above = False
    aos_time = None
    while dt <= end:
        t = ts.from_datetime(dt.replace(tzinfo=timezone.utc))
        el = elevation_deg(sat, obs, t)
        above = el >= horizon_deg
        if above and not last_above:
            aos_time = dt
        if not above and last_above and aos_time:
            passes.append((aos_time, dt))
            aos_time = None
        last_above = above
        dt += step
    return passes

def elevation_deg(sat: EarthSatellite, obs, t: Time):
    diff = sat - obs
    topocentric = diff.at(t)
    alt, az, distance = topocentric.altaz()
    return float(alt.degrees)

# ---------------- Observer ----------------
observer = wgs84.latlon(latitude_degrees=LAT, longitude_degrees=LON, elevation_m=ELEV)

# ---------------- Build data ----------------
TLE_BLOCKS = fetch_tles()
SAT_OBJECTS = sats_from_tle(TLE_BLOCKS)

def world_figure():
    now = datetime.now(timezone.utc)
    t = ts.from_datetime(now)
    df = subpoint_df(SAT_OBJECTS, t)

    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lon=df["lon"], lat=df["lat"], mode="markers",
        text=df["name"], marker=dict(size=4), name="Satellites"
    ))

    # Ground tracks for first few (keeps it fast)
    for sat in SAT_OBJECTS[: min(15, len(SAT_OBJECTS))]:
        pts = groundtrack_for_sat(sat, t, minutes=GTRACK_MIN, step_sec=60)
        if pts:
            lats, lons = zip(*pts)
            fig.add_trace(go.Scattergeo(lon=lons, lat=lats, mode="lines", name=f"{sat.name} track"))

    fig.update_geos(showcoastlines=True, showcountries=True, showland=True, fitbounds="locations")
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=700)
    return fig

def passes_table(max_per_sat=2):
    now = datetime.utcnow()
    rows = []
    for sat in SAT_OBJECTS[: min(40, len(SAT_OBJECTS))]:
        ps = next_passes(sat, observer, now, horizon_deg=MIN_EL, window_hours=24)
        for (aos, los) in ps[:max_per_sat]:
            rows.append({
                "Satellite": sat.name,
                "AOS (UTC)": aos.strftime("%Y-%m-%d %H:%M:%S"),
                "LOS (UTC)": los.strftime("%Y-%m-%d %H:%M:%S"),
                "Duration (min)": f"{(los - aos).total_seconds()/60:.1f}",
                "MinEl(deg)": f"{MIN_EL:.0f}"
            })
    df = pd.DataFrame(rows).sort_values(by="AOS (UTC)")
    return df

# ---------------- Dash app ----------------
app.title = "SatViz v0.1"

app.layout = html.Div([
    html.H3("SatViz v0.1 — Live satellites & ground tracks"),
    html.Div(f"Observer: lat {LAT}, lon {LON}, elev {ELEV} m — Min elevation: {MIN_EL}° — Ground track: {GTRACK_MIN} min"),
    dcc.Graph(id="globe", figure=world_figure()),
    html.H4("Next 24h passes (top 2 each sat):"),
    dcc.Interval(id="tick", interval=60_000, n_intervals=0),
    html.Div(id="passes")
])

@app.callback(
    Output("globe", "figure"),
    Input("tick", "n_intervals")
)
def refresh_globe(_):
    return world_figure()

@app.callback(
    Output("passes", "children"),
    Input("tick", "n_intervals")
)
def refresh_passes(_):
    df = passes_table()
    if df.empty:
        return html.Div("No passes above threshold in next 24h.")
    header = html.Tr([html.Th(c) for c in df.columns])
    body = [html.Tr([html.Td(df.iloc[i, j]) for j in range(len(df.columns))]) for i in range(min(len(df), 200))]
    return html.Table([header] + body, style={"fontFamily":"monospace", "fontSize":"12px"})
    
if __name__ == "__main__":
    app.run(debug=True,
    host="127.0.0.1",
    port=8050,
    use_reloader=False)
