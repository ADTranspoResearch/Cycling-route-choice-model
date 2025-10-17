"""
This module calculates the properties of each chosen path and
alternative for every cyclist in the cycling chosen path file. each
cyclist gets their own set_property file in choice_properties/.
"""

import json
import ast

import networkx as nx
import pandas as pd
import numpy as np

from choice_properties.utils.choicefunctions import (
    get_edges_from_nodes,
    get_path_size_factor,
    get_path_properties,
    concat_road_props,
)

# Filepaths.
choice_set_filepath = "choice_set/"
road_prop_filepath = "shapefiles/2015_attempt/road_properties_2015.csv"
lts_filepath = "shapefiles/LTS_links.csv"
error_filepath = "choice_properties/error_log/"
cyclist_trajectory_filepath = (
    "manual_map_matching/cyclist_chosen_path_node.csv"
)
output_filepath = "choice_properties/choice_files/"

# Get nx network.
G = nx.read_graphml("road_network_2015_with_coords_v3.graphml")

# Contains properties of all links from geobase.
prop_df = pd.read_csv(road_prop_filepath, index_col="ID_RD")

# Edge length dict used for calculating path size factor
edge_lengths = dict(zip(prop_df.index, prop_df["length"]))

# Contains LTS of most links, some are not in this database.
lts_df = pd.read_csv(lts_filepath, index_col="ID_TRC")

# Combine road_prop and lts_df
road_prop_df = concat_road_props(prop_df, lts_df)

# DB containing the chosen path of each cyclist
chosen_path_df = pd.read_csv(
    cyclist_trajectory_filepath, index_col="id_origine"
)

# Iterate over chosen path file and perform analysis for each cyclist.
for index, row in chosen_path_df.iterrows():
    # Check if choice set exists for cyclist.
    cyc_id = index
    if cyc_id != 114:
        continue
    try:
        with open(
            f"{choice_set_filepath}{index}_choice_set.json", "r"
        ) as json_file:
            choice_set = json.load(json_file)
    except FileNotFoundError:
        print(f"cyclist {index} does not have choice set file, skipping....")
        continue
    # Initialize df for storing choice properties.
    properties_cols = ["choice_id", "edges", "path_size", "chosen"]
    choice_prop_df = pd.DataFrame(columns=properties_cols)

    # Get chosen path.
    chosen_path = ast.literal_eval(chosen_path_df["node_path"].loc[index])
    chosen_path = [int(f) for f in chosen_path]
    # Edge ids are used to search the dbs for edge properties
    edge_list = get_edges_from_nodes(G, chosen_path)

    new_row = {
        "choice_id": len(choice_prop_df),
        "edges": edge_list,
        "path_size": None,
        "chosen": 1,
    }
    choice_prop_df.loc[len(choice_prop_df)] = new_row

    # Get alternative paths
    for path in choice_set:
        edge_list = get_edges_from_nodes(G, path)
        new_row = {
            "choice_id": len(choice_prop_df),
            "edges": edge_list,
            "path_size": None,
            "chosen": 0,
        }
        choice_prop_df.loc[len(choice_prop_df)] = new_row

    # Calculate properties of choices
    first_row = True
    for index, row in choice_prop_df.iterrows():
        path_properties = get_path_properties(row["edges"], road_prop_df)

        # Initialize the properties columns in df. Columns are define by
        # get_path_properties function.
        if first_row:
            for key in path_properties.keys():
                choice_prop_df[key] = None
                first_row = False
        choice_prop_df.loc[index, path_properties.keys()] = (
            path_properties.values()
        )

    # Calculate path size factor
    for index, row in choice_prop_df.iterrows():
        path = row["edges"]
        #other_choices = choice_prop_df.drop(index)
        path_size = get_path_size_factor(path, choice_prop_df, edge_lengths)
        choice_prop_df.at[index, "path_size"] = path_size

    choice_prop_df.to_csv(output_filepath + f"properties_{cyc_id}.csv")
    print(f"{cyc_id} successful")
