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
    trajectory = row.geometry
    # Iterate over all points along trajectory, find candidate links
    trajectory_gdf = gpd.GeoDataFrame(
    geometry=[Point(x, y) for x, y in trajectory.coords],
    crs="EPSG:32188"  # replace with your CRS if known
)
    points_records = {}
    trajectory_gdf['candidates'] = None
    for i, row in trajectory_gdf.iterrows():
        pt = row.geometry
        candidates = k_nearest_segments(pt, tree_data[0], tree_data[1], tree_data[2], k=5)
        candidates['transition_prob'] = None
        # Step 3 - Emission Probabilities
        if len(points_records) == 0:
            emission_probs = gaussian_distance(pt, candidates.geometry)
            prev_pt = pt
        else:
            emission_probs = emission_prob(pt, prev_pt, candidates.geometry, bear_var=40, use_bearing=True)
        candidates['emission_prob'] = emission_probs
        trajectory_gdf.at[i, 'candidates'] = candidates
        #trajectory_gdf.at[i, 'emission_probability'] = emission_probs 
        prev_pt = pt

    # Step 4 - Transition Probabilities
    for i, row in trajectory_gdf.iterrows():
        pt = row.geometry
        candidates = row['candidates']
        if i + 1 < len(trajectory_gdf):
            next_pt = trajectory_gdf.iloc[i+1].geometry
            next_candidates = trajectory_gdf.iloc[i+1]['candidates']
        else:
            break
        for idy, candidate in candidates.iterrows():
            transition_prob_list = []
            for next_candidate in next_candidates.geometry:
                transition_prob = transition_probability(
                    (pt, next_pt),
                    (candidate, next_candidate),
                    shp_network_full
                )
                transition_prob_list.append(transition_prob)
            candidates.at[idy, 'transition_prob'] = transition_prob_list


    trajectory_gdf.to_csv('map_matching/trajectory_transition_test.csv')
    exit()
    # Step 5 - Hidden Markov Model
    # Apply Viterbi Algorithm
    path, node_path = run_viterbi(point_gdf, G)
    matched_links = shp_network_full[shp_network_full['ID_RD'].isin(path)].copy()
    #    print(node_path)
    #    print(path)

    tok = time()
    point_time(idx, len(trajectory.coords), tik, tok)
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
