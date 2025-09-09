"""
Module used to take chosen path given by data and compare paths to 
generated choice set paths. If there is a link that appears in the 
chosen path that does not appear in any of the chosen paths it will be 
removed. This is an attempt to solve the overfitting of the path size
factor problem.
"""
import os
import json
import ast

import pandas as pd
import networkx as nx
choice_set_filepath = "choice_set/"
database_filepath = "shapefiles/2015_attempt/road_properties_2015.csv"
cyclist_gps_filepath = "cyclists/cyclists_trips.csv"

def find_unique_edges(chosen_p, choice_s, graph):
    """
    Finds the links that appear in the chosen path but not in
    any of the choice set paths.
    """
    cs_links = []
    for choice in choice_s:
        rd_id_list = []
        for i in range(0, (len(choice) - 1)):
            j = i + 1

            rd_id_list.append(graph.edges[str(choice[i]), str(choice[j])]["ID_RD"])
        for link in rd_id_list:
            if link not in cs_links:
                cs_links.append(link)

    unique_chosen_links = []
    for link in chosen_p:
        if link not in cs_links:
            unique_chosen_links.append(link)

    return cs_links, unique_chosen_links

G = nx.read_graphml("road_network_2015_with_coords.graphml")
cyclist_df = pd.read_csv(cyclist_gps_filepath, index_col = "id_origine")

cs_directory = os.listdir(choice_set_filepath)

cs_link_count = []
cp_length = []
cp_unique = []
unique_ratio = []
for index, row in cyclist_df.iterrows():
    cs_filename = f"{int(index)}_choice_set.json"
    if cs_filename not in cs_directory:
        unique_ratio.append(1)
        continue

    with open(choice_set_filepath+cs_filename, "r") as json_file:
        str_choice_set = json.load(json_file)
    # Convert choice set list into ints
    choice_set = [[int(item) for item in sublist] for sublist in str_choice_set]
    chosen_path = ast.literal_eval(row["trip_segment"])

    choice_set_links, unique_chosen = find_unique_edges(chosen_path, choice_set, G)

    cs_link_count.append(len(choice_set_links))
    cp_length.append(len(chosen_path))
    cp_unique.append(len(unique_chosen))
    if len(chosen_path) == 0:
        ratio = 1
    else:
        ratio = len(unique_chosen) / len(chosen_path)
    unique_ratio.append(ratio)

cyclist_df["unique_link_ratio"] = unique_ratio
cyclist_df.to_csv("cyclists/cyclists_trips_with_unique_ratio.csv")
df_dict = {
    "choice_set_links": cs_link_count,
    "chosen_path_length": cp_length,
    "unique_cp_links": cp_unique,
}

stats = pd.DataFrame(df_dict)

stats.to_csv('unique_link_test.csv')
