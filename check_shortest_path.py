"""
Some GPS trips have large jumps in their trajectories with gaps between consecutive
GPS points. This module compares the shortest path between origin and destination
of trips to the reported length to find how many trips are significantly shorter
indicating the path reported is not possible due to GPS jumps.
"""

import pandas as pd
import networkx as nx

def euclidian(a, b):

    x1, y1 = G.nodes[a]['x'], G.nodes[a]['y']
    x2, y2 = G.nodes[b]['x'], G.nodes[b]['y']

    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

od_filepath = 'cyclists/'
od_filename = 'cyclist_od_list.csv'
od_df = pd.read_csv(od_filepath+od_filename)
cyclist_filepath = 'cyclists/cyclists_trips.csv'
cyclist_df = pd.read_csv(cyclist_filepath)

G = nx.read_graphml("road_network_2015_with_coords.graphml")

for index, row in od_df.iterrows(): #iterate over every GPS trace and OD pair to get the full Choice Set

    try:
        sp = nx.astar_path(
            G,
            str(row["origin"]),
            str(row["destination"]),
            heuristic=euclidian,
            weight="length",
        )  # find shortest path from the original graph,
        # Calculate total length of the path

    except nx.NetworkXNoPath:

        print(f"warning: cyclist {row['cyclist_id']} has no path from origin to destination!")
        continue
    total_length = sum(
        G.edges[sp[i], sp[i+1]]["length"] for i in range(len(sp)-1)
    )
    cyclist_df.loc[
        cyclist_df["id_origine"] == row["cyclist_id"], "shortest_path_length"
    ] = total_length
# Fill all empty (NaN) rows in 'shortest_path' with 0
cyclist_df['shortest_path_length'] = cyclist_df['shortest_path_length'].fillna(0)

# Calculate percentage where 'shortest_path' < 'length'
percentage = (cyclist_df['shortest_path_length'] < cyclist_df['length'].astype(float)).mean() * 100

print(f"Percentage of rows where 'shortest_path' is smaller than 'length': {percentage:.2f}%")

short_path_error_df = cyclist_df[cyclist_df['shortest_path_length'] > cyclist_df['length'].astype(float)]

short_path_error_df.to_csv('cyclists/shortest_path_error.csv')