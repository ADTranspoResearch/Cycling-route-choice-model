"""Map-matching module that matches trajectory points to a road network"""

from time import time
import pandas as pd
import geopandas as gpd
from shapely import Point

from candidatesearch import k_nearest_segments
from timeanal import point_time
from emissionprob import emission_prob, gaussian_distance
from transitionprob import initialize_edge_lookup, transition_probability
from viterbi import run_viterbi



def run_map_matching(idx, row, tree_data, G, shp_network_full):
    """Runs the full map matching algorithm and returns the link path list"""
    tik = time()
    points_count = 0
    trajectory = row.geometry
    # Iterate over all points along trajectory, find candidate links
    points_count += len(trajectory.coords)
    points_records = {}
    for coord in trajectory.coords:
        x, y = coord
        pt = Point(x, y)
        candidates = k_nearest_segments(pt, tree_data[0], tree_data[1], tree_data[2], k=5)
        # Step 3 - Emission Probabilities
        if len(points_records) == 0:
            candidates['emission_probability'] = gaussian_distance(pt, candidates.geometry)
            prev_pt = pt
        else:
            candidates['emission_probability'] = emission_prob(pt, prev_pt, candidates.geometry, bear_var=40, use_bearing=True)
        points_records[pt]= candidates,  # gdf containing emission prob

        prev_pt = pt

    # Step 4 - Transition Probabilities
    for coord in trajectory.coords:
        x, y = coord
        pt = Point(x, y)
        candidates = points_records[pt]

# Transition probability section currently not working


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
    return path, node_path, matched_links








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
