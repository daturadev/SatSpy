# Dependencies
#import numpy as np
# from beyond.io.tle import Tle
import requests
import observe

# Two-line element (TLE) sets:
# Chinese (CN) satellite DB:
url_cn =  'https://celestrak.org/NORAD/elements/gp.php?GROUP=fengyun-1c-debris&FORMAT=tle'
# Russian (RU) satellite DB: 
url_ru = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=cosmos-1408-debris&FORMAT=tle'


# Handle intel
r_ru = requests.get(url_ru)
r_cn = requests.get(url_cn)

# Parse intel
ru = r_ru.text
cn = r_cn.text

# Gather information using observe package
observe(tle, qth[, at=None])  
    Return an observation of a satellite relative to a groundstation.
    qth groundstation coordinates as (lat(N),long(W),alt(m))
    If at is not defined, defaults to current time (time.time())
    Returns an "observation" or dictionary containing:  
        altitude _ altitude of satellite in kilometers
        azimuth - azimuth of satellite in degrees from perspective of groundstation.
        beta_angle
        decayed - 1 if satellite has decayed out of orbit, 0 otherwise.
        doppler - doppler shift between groundstation and satellite.
        eci_obs_x
        eci_obs_y
        eci_obs_z
        eci_sun_x
        eci_sun_y
        eci_sun_z
        eci_vx
        eci_vy
        eci_vz
        eci_x
        eci_y
        eci_z
        eclipse_depth
        elevation - elevation of satellite in degrees from perspective of groundstation.
        epoch - time of observation in seconds (unix epoch)
        footprint
        geostationary - 1 if satellite is determined to be geostationary, 0 otherwise.
        has_aos - 1 if the satellite will eventually be visible from the groundstation
        latitude - north latitude of point on earth directly under satellite.
        longitude - west longitude of point on earth directly under satellite.
        name - name of satellite from first line of TLE.
        norad_id - NORAD id of satellite.
        orbit 
        self.observe_parse_tle()

    def observe_parse_tle(self):
        self.satellite_id = self.line1[2:7].strip()
        self.classification = self.line1[7:8].strip()
        self.epoch = self.line1[18:32].strip()
        self.inclination = self.line2[8:16].strip()
        self.ra_of_asc_node = self.line2[17:25].strip()
        self.eccentricity = self.line2[26:33].strip()
        self.arg_of_perigee = self.line2[34:42].strip()
        self.mean_anomaly = self.line2[43:51].strip()
        self.mean_motion = self.line2[52:63].strip()

    def __str__(self):
        return f'Satellite ID: {self.satellite_id}, Classification: {self.classification}, Epoch: {self.epoch}'

ru_tle_data = ru
cn_tle_data = cn

def manual_parse_tle(tle):
    lines = tle.strip().split('\n')[1:]  # Skip the first line
    satellites = []
    if len(lines) % 2 != 0:
        print("Warning: TLE data does not contain an even number of lines.")
        return satellites  # Return an empty list if the data is invalid
    for i in range(0, len(lines), 2):
        satellites.append(SatelliteTLE(lines[i], lines[i + 1]))
    return satellites


ru_sats = observe_parse_tle(ru_tle_data) + manual_parse_tle(ru_tle_data)
cn_sats = observe_parse_tle(cn_tle_data) + manual_parse_tle(cn_tle_data)
standardized_sat = ru_sats + cn_sats

def separate_intel(country):
    for sat in country:
        print(sat)
        
separate_intel(cn_sats)
separate_intel(ru_sats)






