'''draft file used for testing viterbi without running whole code'''
import pandas as pd
import geopandas as gpd
import networkx as nx
from viterbi import viterbi, initialize_edge_lookup, prune_disconnected_links, add_missing_nodes, node_to_edge_list


def remove_duplicates(lst):
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

shp_network = gpd.read_file('shapefiles/map_matching/2015merged_network_file.shp')
point_data = pd.read_pickle('test/hmm_data_test_only_bike_lane.pkl')
G = nx.read_graphml('road_network_2015_with_coords.graphml')
initialize_edge_lookup(G)
path = viterbi(point_data)


path = remove_duplicates(path)
path, node_path = prune_disconnected_links(G, path)

node_path = add_missing_nodes(node_path, G)

print(node_path)
path = node_to_edge_list(node_path)
print(path)
matched_links = shp_network[shp_network['ID_RD'].isin(path)].copy()

import matplotlib.pyplot as plt


fig, ax = plt.subplots(figsize=(10, 10))

# (Optional) Plot all links in light gray for context
#links_gdf.plot(ax=ax, color='lightgray', linewidth=1, label='All Roads')

# Plot the matched path in red
matched_links.plot(ax=ax, color='red', linewidth=2, label='Matched Path')

# Plot the GPS points in blue
point_data.plot(ax=ax, color='blue', markersize=10, label='GPS Points')

# Add legend and labels
ax.set_title("Map-Matching: GPS Trajectory and Matched Path")
ax.legend()
ax.set_aspect('equal')
plt.show()
