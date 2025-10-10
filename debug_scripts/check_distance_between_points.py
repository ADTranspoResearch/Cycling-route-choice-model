"""
Some GPS trips have large gaps, this module attempts to locate the gaps
by checking distance between consecutive GPS points
"""
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

shapefile_path_trips = "shapefiles/map_matching/island_cyclist_trips.shp"
shp_trip = gpd.read_file(shapefile_path_trips)
shp_trip = shp_trip.to_crs("EPSG:32188")


# Collect all segment lengths between consecutive points in all linestrings
segment_lengths = []

ids_with_large_gap = []
large_gap = 200
for idx, line in enumerate(shp_trip.geometry):
    has_large_gap = False
    if line.geom_type == "LineString":
        coords = list(line.coords)
        lengths = [((coords[i][0] - coords[i-1][0])**2 + (coords[i][1] - coords[i-1][1])**2)**0.5
                  for i in range(1, len(coords))]
        lengths = lengths[1:-1]
        segment_lengths.extend(lengths)
        if any(l > large_gap for l in lengths):
            has_large_gap = True
    elif line.geom_type == "MultiLineString":
        for linestring in line:
            coords = list(linestring.coords)
            lengths = [((coords[i][0] - coords[i-1][0])**2 + (coords[i-1][1] - coords[i][1])**2)**0.5
                      for i in range(1, len(coords))]
            lengths = lengths[1:-1]
            segment_lengths.extend(lengths)
            if any(l > large_gap for l in lengths):
                has_large_gap = True
    if has_large_gap:
        ids_with_large_gap.append(shp_trip.iloc[idx]['id_origine'])

# ...existing code for histogram...
print(f"id_origine values with a gap > {large_gap} meters between points:")
print(ids_with_large_gap)
print(len(ids_with_large_gap))

exit()
# Plot histogram
bins = list(range(0, 51, 1)) + [float('inf')]
# Assign segment lengths to bins, capping anything >1000 to the last bin

segment_lengths_capped = [l if l <= 51 else 52 for l in segment_lengths]

plt.hist(segment_lengths_capped, bins=bins, density=False)
plt.xlabel("Segment Length (meters)")
plt.ylabel("Count")
plt.title("Distribution of Lengths Between Consecutive Points")
#plt.xticks(list(range(0, 51, 100)) + [1001], labels=[str(x) for x in range(0, 1001, 100)] + ['>1000'])
plt.show()
# ...existing code...