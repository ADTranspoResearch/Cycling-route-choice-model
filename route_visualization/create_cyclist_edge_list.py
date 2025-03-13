'''
choice_set.json files generated for cyclists are a list of nodes from the origin node to the destination node
if you would like to display the choice set for a given cyclist on a map in QGIS, you will need the list of edges the cyclist uses instead of the nodes
this file takes a cyclist choice_set as an input, and outputs the list of edges that cyclist used, which can then be used in QGIS to create maps
'''
import json
import os
import networkx as nx

def check_dir(path):
    # Check if the directory exists
    if not os.path.exists(path):
        # Create the directory if it doesn't exist
        os.makedirs(path, exist_ok=True)
        print(f"Directory '{path}' created.")
    else:
        print(f"Directory '{path}' already exists.")



graph_filepath = os.path.join(os.getcwd(), os.pardir, 'road_network_2015_with_coords.graphml')
choice_set_rel_path = 'choice_set/'
choice_set_filepath = os.path.join(os.getcwd(), os.pardir, choice_set_rel_path)
edge_list_output_filepath = 'edge_lists/'
check_dir(edge_list_output_filepath)

G = nx.read_graphml(graph_filepath)

edge_choice_set=[]





idnum = input('cyclist_id you would like to analyze: ')
with open(f"{choice_set_filepath}{idnum}_choice_set.json", 'r') as json_file:
    choice_set = json.load(json_file)

for route in choice_set:
    edge_route = []
    for i in range(0, (len(route)-1)):
        j=i+1
        edge_data = G.get_edge_data(route[i],route[j])
        if edge_data and 'ID_RD' in edge_data:
            #print("ID_RD:", edge_data['ID_RD'])
            edge_route.append(edge_data['ID_RD'])
        else:
            print("Edge does not exist or has no 'ID_RD' attribute.")
    edge_choice_set.append(edge_route)

edge_choice_set_filename = f"{idnum}_edge_choice_set.json"
with open(os.path.join(edge_list_output_filepath,edge_choice_set_filename), 'w') as file:
    json.dump(edge_choice_set, file)

