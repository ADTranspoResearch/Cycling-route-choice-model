"""Map-matching module that matches trajectory points to a road network"""

import os
from time import time
import pandas as pd
import geopandas as gpd
import networkx as nx
from shapely import Point


from candidatesearch import create_network_rtree, k_nearest_segments
from timeanal import point_time
from emissionprob import emission_prob, gaussian_distance
from transitionprob import initialize_edge_lookup, transition_probability
from viterbi import run_viterbi
from displaymap import display_path

# Steps of the code
#
# Step 1 - Imports:
# Road network shapefile.
# Trajectory shapefile.
# Road network NetworkX graph.

# Get filepaths of the necessary files
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
os.chdir(parent_dir)
print(f"Changed working directory to: {os.getcwd()}")
shapefile_path_network = os.path.join(
    "shapefiles", "map_matching", "2015merged_network_file.shp"
)
shapefile_path_trips = os.path.join(
    "shapefiles", "map_matching", "island_cyclist_trips.shp"
)
shp_network_full = gpd.read_file(shapefile_path_network)
shp_trip = gpd.read_file(shapefile_path_trips)
shp_network_full = shp_network_full.to_crs("EPSG:32188")
shp_trip = shp_trip.to_crs("EPSG:32188")
graph_path = "road_network_2015_with_coords.graphml"
G = nx.read_graphml(graph_path)

# Step 1.5 - Remove overlaping road and bikelanes:
# Find all unique IDs in the field "ID_TRC_GEO" and drop all lines
# whose ID_RD is in this list.
id_trc_geo_list = shp_network_full['ID_TRC_GEO'].unique()
series = pd.Series(id_trc_geo_list)
clean_int_list = series.dropna().astype(int).tolist()
shp_network = shp_network_full[~shp_network_full['ID_RD'].isin(clean_int_list)].copy()


# Step 2 - Candidate link identification:
# For every point, find a set of possible links it could belong to.
# Could be done through K-nearest Neighbour based on fixed radius
# or fixed number of candidates.

# Construct R-tree for road network subsegments
str_tree, subsegments, subseg_metadata = create_network_rtree(shp_network)

# For every point, find a set of possible links it could belong to.


for idx, row in shp_trip.iterrows():
    tik = time()
    points_count = 0
    trajectory = row.geometry
    # Iterate over all points along trajectory, find candidate links
    points_count += len(trajectory.coords)
    points_records = []
    for coord in trajectory.coords:
        x, y = coord
        pt = Point(x, y)
        candidates = k_nearest_segments(pt, str_tree, subsegments, subseg_metadata, k=5)
        candidates_geom = [entry['geometry'] for entry in candidates]
        # Step 3 - Emission Probabilities
        if len(points_records) == 0:
            candidate_probs = gaussian_distance(pt, candidates_geom)
            prev_pt = pt
        else:
            candidate_probs = emission_prob(pt, prev_pt, candidates_geom, bear_var=40, use_bearing=True)
        points_records.append(
            {
                "geometry": pt,
                "candidates": candidates,  # List of (index, segment, metadata)
                "candidate_probs": candidate_probs,  # List of floats
            }
        )
        prev_pt = pt
    point_gdf = gpd.GeoDataFrame(points_records, geometry="geometry", crs="EPSG:32188")
    # Step 4 - Transition Probabilities
    initialize_edge_lookup(G)
    rows = list(point_gdf.iterrows())
    trans_dict = {}
    for i in range(len(rows) - 1):
        idx_i, row_i = rows[i]
        idx_j, row_j = rows[i + 1]
        point_i = row_i["geometry"]
        point_j = row_j["geometry"]
        candidate_i = row_i["candidates"]
        candidate_j = row_j["candidates"]
        trans_prob = transition_probability(
            point_i, point_j, candidate_i, candidate_j, G
        )
        trans_dict[idx_i] = trans_prob
    point_gdf["transition_probs"] = pd.Series(trans_dict)
    # Step 5 - Hidden Markov Model
    # Apply Viterbi Algorithm
    path, node_path = run_viterbi(point_gdf, G)
    matched_links = shp_network_full[shp_network_full['ID_RD'].isin(path)].copy()
#    print(node_path)
#    print(path)

    tok = time()
    point_time(idx, points_count, tik, tok)
    display_path(point_gdf, matched_links)





# Step 3 - Emission Probabilities
# Compute likelihood that a point belongs to a link for all
# candidate links.
# Possible model: Gaussian distribution distance.

# Step 4 - Transition Probabilities
# When consecutive points have different candidate links, compute
# the probability that they are actually transition links based on
# the geodesic distance VS network distance (use nx graph to find
# shortest path between candidate links).

# Step 5 - Hidden Markov Model
# Use HMM to find most likely sequence of links based on emission
# and transition probabilities.


# Step 6 - Route Reconstruction
# Build the set of links that make up the cyclist's path.

# Step 7 - Export
# Re create cyclist trip data file that includes ID, and all other
# trip data.
