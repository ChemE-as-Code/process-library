"""Local site frame of lng-terminal-1 from the measured reference points (DESIGN.md D-013).

The plot plan follows the real geometry of the LNG Canada site at Kitimat: a few points and
distances measured on OpenStreetMap (data (c) OpenStreetMap contributors, ODbL) and checked
on Esri World Imagery (2024-07-06, 2025-05-12; viewed and measured only, nothing copied).
Only these rounded points enter the layout; no OSM geometry is imported.

Frame: x east, y north, metres, origin at the site's south-west corner (53.990 N, 128.700 W);
local equirectangular projection at 54.0 N (WGS84 metres per degree). Run with
`cheme run scripts/site_frame.py`; it prints the local coordinates, distances and bearings.
"""

import math

LAT0, LON0 = 53.990, -128.700
PHI = math.radians(54.0)
M_LAT = 111132.92 - 559.82 * math.cos(2 * PHI) + 1.175 * math.cos(4 * PHI)
M_LON = 111412.84 * math.cos(PHI) - 93.5 * math.cos(3 * PHI)

# name: (lat, lon, source)
POINTS = {
    "tank 1 centre": (54.017185, -128.685827, "OSM way 1435792133 (footprint ~93 m)"),
    "flare (storage and loading derrick)": (54.0178769, -128.6773564, "OSM node 13436993551"),
    "train 1 centre": (54.024647, -128.680349, "OSM way 1465010131 (316 x 162 m)"),
    "train 2 centre": (54.024465, -128.683533, "OSM way 1465010132"),
    "train 3 centre": (54.024253, -128.686968, "OSM way 1465010133"),
    "train 4 centre": (54.024060, -128.690200, "OSM way 1465010134"),
    "plant south edge, trestle start": (54.0158, -128.6833, "imagery reading, +/-20 m"),
    "loading platform (Berth 2)": (53.9980, -128.6824, "imagery reading, +/-15 m"),
    "berth face north end": (54.0001, -128.6832, "imagery reading"),
    "berth face south end": (53.99675, -128.68255, "imagery reading"),
    "south dolphin and catwalk": (53.996645, -128.682176, "OSM way 192912131"),
}


def local(lat, lon):
    return (lon - LON0) * M_LON, (lat - LAT0) * M_LAT


def bearing(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    return math.hypot(dx, dy), math.degrees(math.atan2(dx, dy)) % 360


def main():
    print(f"m per degree: lat {M_LAT:.1f}, lon {M_LON:.1f}")
    xy = {}
    for name, (lat, lon, src) in POINTS.items():
        xy[name] = local(lat, lon)
        print(f"{name:40s} x {xy[name][0]:8.1f}  y {xy[name][1]:8.1f}   ({src})")
    for a, b in [("tank 1 centre", "flare (storage and loading derrick)"),
                 ("tank 1 centre", "loading platform (Berth 2)"),
                 ("plant south edge, trestle start", "loading platform (Berth 2)"),
                 ("berth face north end", "berth face south end"),
                 ("train 1 centre", "train 2 centre"),
                 ("tank 1 centre", "train 2 centre")]:
        d, brg = bearing(xy[a], xy[b])
        print(f"{a} -> {b}: {d:.0f} m at {brg:.1f} deg")


if __name__ == "__main__":
    main()
