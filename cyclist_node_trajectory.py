"""
This module takes a csv that contains the chosen path for each cyclist
based on edges and then replaces the path the the list of nodes it uses.
"""
import ast 

import pandas as pd

cyclist_traject_filepath = "manual_map_matching/cyclist_chosen_path.csv"
cyclist_traject_df = pd.read_csv(cyclist_traject_filepath, index_col="id_origine")

edge_node_filepath = "shapefiles/2015 verticies with node id_geometry.csv"
edge_node_df = pd.read_csv(edge_node_filepath)

cyclist_traject_df["node_path"] = None
for index, row in cyclist_traject_df.iterrows():
    chosen_path = ast.literal_eval(row["path"])
    node_path = []
    for edge in chosen_path:
        start_node = int(edge_node_df.loc[(edge_node_df["ID_RD"] == edge) & (edge_node_df["vertex_pos"]==0), "node_id" ].iloc[0])
        end_node = int(edge_node_df.loc[(edge_node_df["ID_RD"] == edge) & (edge_node_df["vertex_pos"]==-1), "node_id" ].iloc[0])
        if start_node not in node_path:
            node_path.append(start_node)
        if end_node not in node_path:
            node_path.append(end_node)
    cyclist_traject_df.at[index, "node_path"] = node_path

output_filepath = "manual_map_matching/cyclist_chosen_path_node.csv"
cyclist_traject_df.to_csv(output_filepath, index_label="id_origine")