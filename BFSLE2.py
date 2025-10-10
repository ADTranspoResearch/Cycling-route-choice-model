"""
This module generates the breadth first search link elimination choice set using
cyclists origin and destination points. For each cyclist it saves a JSON file containing
a list of lists of node ids that make up the alternate paths for the cyclist in the
networkx graph.
"""
import json

import networkx as nx
import pandas as pd

from utils import check_dir
from BFSLE.sptree import get_sp_tree, euclidian
from BFSLE.weights import cyclist_edge_cost

CHOICE_SET_SIZE = 80

output_path = "choice_set/"
error_id_path = "choice_set/Past Error ID/"
check_dir(output_path)
check_dir(error_id_path)

od_filepath = "cyclists/"
od_filename = "cyclist_od_list_remove_first_last_pt.csv"
od_df = pd.read_csv(od_filepath + od_filename)

# Get graph
graph_path = "road_network_2015_with_coords_v3.graphml"
G = nx.read_graphml(graph_path)


error_id = {}
short_set_count = 0
# loop through all cyclists
for index, row in od_df.iterrows():

    # sp_and_removed_edge_dict holds the alternative paths and what
    # edges were removed from the graph when generated.
    sp_and_removed_edge_list = []
    counter = 0
    cyc_id = int(row["cyclist_id"])

    # Origin and destination nodes for cyclist.
    od = (str(row["origin"]), str(row["destination"]))

    # Get original shortest path on base graph.
        
    try:
#        sp = nx.astar_path(
#            G, od[0], od[1], heuristic=lambda u, v: euclidian(G, u, v), weight=cyclist_edge_cost
#        )
        sp = nx.shortest_path(G, od[0], od[1], weight=cyclist_edge_cost)
    except nx.NetworkXNoPath:
        error_id[cyc_id] = "no path from OD"
        print(f"warning: cyclist {cyc_id} has no path from origin to destination!")
        continue
    sp_and_removed_edge_list.append({"sp": sp, "removed_edges": []})

    # Loop through edges to create alternative paths with new graphs
    while len(sp_and_removed_edge_list) < CHOICE_SET_SIZE:

        # Calculates alternative paths to a maximum of the remaining
        # amount required to reach the choice set size.
        remaining_alts = CHOICE_SET_SIZE - len(sp_and_removed_edge_list)

        # Checks if we run out of alternative routes in the BF search.
        try:
            original_path = sp_and_removed_edge_list[counter]
        except IndexError:
            print(
                f"warning: cyclist {cyc_id}'s choice set is only {len(sp_and_removed_edge_list)} long!"
            )
            error_id[cyc_id] = f"choice set size, {len(sp_and_removed_edge_list)}"
            short_set_count+=1
            break
        layer_sp = get_sp_tree(
            G, original_path["sp"], od, original_path["removed_edges"], remaining_alts
        )
        sp_and_removed_edge_list.extend(layer_sp)
        counter+=1

    # Save the cyclist's choice set to a JSON file.
    choice_set_filename = f"{cyc_id}_choice_set.json"
    print(f"{cyc_id}_choice_set.json")
    sp_list = [d["sp"] for d in sp_and_removed_edge_list]
    with open(output_path+choice_set_filename, 'w') as file:
        json.dump(sp_list, file)


# Currently not saving the cyclist ids that had errors
print(f"{len(error_id)} cyclist trips had issues")
print(f"{short_set_count} cyclists have less than 80 choices")

# function for path weight
# get_cycling_cost(node_1, node_2, edge_attributes):
# possible factors: length, slope, infrastructure type
