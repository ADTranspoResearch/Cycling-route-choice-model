'''
choice_set.json files generated for cyclists are a list of nodes from
the origin node to the destination node. If you would like to display
the choice set for a given cyclist on a map in QGIS, you will need the
list of edges the cyclist uses instead of the nodes. This file takes a
cyclist choice_set as an input, and outputs the list of edges that
cyclist used, which can then be used in QGIS to create maps
'''
import json
import os
import networkx as nx
from utils import check_dir




graph_filepath =  'road_network_2015_with_coords_v3.graphml'
choice_set_filepath = 'choice_set/'
edge_list_output_filepath = 'edge_lists/'
check_dir(edge_list_output_filepath)

G = nx.read_graphml(graph_filepath)

for filename in os.listdir(choice_set_filepath):
    if filename.endswith('_choice_set.json'):
        cyclist_id = filename.replace('_choice_set.json', '')
        input_path = os.path.join(choice_set_filepath, filename)
        with open(input_path, 'r') as json_file:
            choice_set = json.load(json_file)

        edge_choice_set = []
        for route in choice_set:
            edge_route = []
            for i in range(0, (len(route)-1)):
                j = i + 1
                edge_data = G.get_edge_data(route[i], route[j])
                if edge_data and 'ID_RD' in edge_data:
                    edge_route.append(edge_data['ID_RD'])
                else:
                    print(f"Edge does not exist or has no 'ID_RD' attribute for {route[i]}->{route[j]} in {filename}.")
            edge_choice_set.append(edge_route)

        edge_choice_set_filename = f"{cyclist_id}_edge_choice_set.json"
        output_path = os.path.join(edge_list_output_filepath, edge_choice_set_filename)
        with open(output_path, 'w') as file:
            json.dump(edge_choice_set, file)

