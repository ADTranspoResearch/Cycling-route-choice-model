"""
3rd version of graph generation.
Issues it must address: must be a graph not digraph. must handle multiple
edge ids connecting the same nodes and only keep the relevant ones (bike lanes)
needs to include attributes that can be used to create a function to determine
shortest path (link speed, factors afecting that)
"""

import pandas as pd
import networkx as nx


def get_node_coords(rd_id, vertex_pos, id_name="ID_TRC"):
    x = float(
        df.loc[(df[id_name] == rd_id) & (df["vertex_pos"] == vertex_pos), "X"].iloc[0]
    )
    y = float(
        df.loc[(df[id_name] == rd_id) & (df["vertex_pos"] == vertex_pos), "Y"].iloc[0]
    )
    return x, y


# Load the shapefile
df = pd.read_csv("shapefiles/2015 verticies with node id_geometry.csv")

lts_filepath = "shapefiles/LTS_links.csv"
lts_df = pd.read_csv(lts_filepath, index_col="fid")

G = nx.Graph()

road_id_list = (
    df["ID_TRC"].dropna().unique().tolist()
)  # gets a list of all the unique ID numbers from the road network, does not include bike network


# create the road network using only road map, bike map is added in next loop
for id_trc in road_id_list:

    first_node = int(
        df.loc[(df["ID_TRC"] == id_trc) & (df["vertex_pos"] == 0), "node_id"].iloc[0]
    )
    first_x_corr, first_y_corr = get_node_coords(id_trc, 0)

    last_node = int(
        df.loc[(df["ID_TRC"] == id_trc) & (df["vertex_pos"] == -1), "node_id"].iloc[0]
    )
    last_x_corr, last_y_corr = get_node_coords(id_trc, -1)

    length = float(
        df.loc[(df["ID_TRC"] == id_trc) & (df["vertex_pos"] == 0), "Length"].iloc[0]
    )
    try:
        slope = float(lts_df.loc[(lts_df["ID_TRC"] == id_trc), "slope_edit"].iloc[0])
    except IndexError:
        slope = 0
    if slope > 1:
        slope = 0

    G.add_edge(
        first_node,
        last_node,
        ID_RD=id_trc,
        length=length,
        bike_lane_type=0,
        slope=slope,
    )

    G.nodes[first_node]["x"] = first_x_corr
    G.nodes[first_node]["y"] = first_y_corr
    G.nodes[last_node]["x"] = last_x_corr
    G.nodes[last_node]["y"] = last_y_corr


bike_id_list = (
    df["ID"].dropna().unique().tolist()
)  # gets a list of all the unique ID numbers from the bike network, does not include road network

bike_count = 0
bike_count_no_network = 0
bike_count_network = 0
for id_bk in bike_id_list:
    trc = int(
        df.loc[(df["ID"] == id_bk) & (df["vertex_pos"] == 0), "ID_TRC_GEO"].iloc[0]
    )
    type1 = int(
        df.loc[(df["ID"] == id_bk) & (df["vertex_pos"] == 0), "TYPE_VOIE"].iloc[0]
    )
    type2 = int(
        df.loc[(df["ID"] == id_bk) & (df["vertex_pos"] == 0), "TYPE_VOIE2"].iloc[0]
    )
    # Applying a bike lane not on the road network
    if round(trc) not in df["ID_TRC"].values:

        bike_count_no_network += 1
        first_node = int(
            df.loc[(df["ID"] == id_bk) & (df["vertex_pos"] == 0), "node_id"].iloc[0]
        )
        first_x_corr, first_y_corr = get_node_coords(id_bk, 0, id_name="ID")
        last_node = int(
            df.loc[(df["ID"] == id_bk) & (df["vertex_pos"] == -1), "node_id"].iloc[0]
        )
        last_x_corr, last_y_corr = get_node_coords(id_bk, -1, id_name="ID")
    # Applying a bike lane on a road that already exists
    else:
        bike_count_network += 1
        first_node = int(
            df.loc[(df["ID"] == id_bk) & (df["vertex_pos"] == 0), "node_id"].iloc[0]
        )
        first_x_corr, first_y_corr = get_node_coords(id_bk, 0, id_name="ID")
        last_node = int(
            df.loc[(df["ID"] == id_bk) & (df["vertex_pos"] == -1), "node_id"].iloc[0]
        )
        last_x_corr, last_y_corr = get_node_coords(id_bk, -1, id_name="ID")

    length = float(
        df.loc[(df["ID"] == id_bk) & (df["vertex_pos"] == 0), "LONGUEUR"].iloc[0]
    )
    try:
        slope = float(lts_df.loc[(lts_df["ID_CYCL"] == id_bk), "slope_edit"].iloc[0])
    except IndexError:
        slope = 0
    if slope > 1:
        slope = 0

    if not G.has_edge(first_node, last_node):
        G.add_edge(
            first_node,
            last_node,
            ID_RD=id_bk,
            length=length,
            bike_lane_type=type1,
            slope=slope,
        )
        G.nodes[first_node]["x"] = first_x_corr
        G.nodes[first_node]["y"] = first_y_corr
        G.nodes[last_node]["x"] = last_x_corr
        G.nodes[last_node]["y"] = last_y_corr
    else:
        if G[first_node][last_node]["bike_lane_type"] < type1:

            if slope == 0 and G[first_node][last_node]["slope"] > 0:
                G.add_edge(
                    first_node,
                    last_node,
                    ID_RD=id_bk,
                    length=length,
                    bike_lane_type=type1,
                )
            else:
                G.add_edge(
                    first_node,
                    last_node,
                    ID_RD=id_bk,
                    length=length,
                    bike_lane_type=type1,
                    slope=slope,
                )
                G.nodes[first_node]["x"] = first_x_corr
                G.nodes[first_node]["y"] = first_y_corr
                G.nodes[last_node]["x"] = last_x_corr
                G.nodes[last_node]["y"] = last_y_corr
    bike_count += 1

# Need to add other properties such as speed adjustment

nx.write_graphml(G, "road_network_2015_with_coords_v3.graphml")
print("written graph to memory")
print(f"bike count: {bike_count}")
print(f"no network count: {bike_count_no_network}")
print(f"network count: {bike_count_network}")
