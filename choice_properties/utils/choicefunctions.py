"""
Module contains functions used by choice_set_properties code to get
properties of alternatives and calculate path size factors.
"""

import pandas as pd


def concat_road_props(road_df, lts_df):
    """
    Takes different dataframes containing road data and merges them.

    parameters:
    road_df - df containing road properties

    lts_df - df containing level of traffic stress.

    returns - df
    """
    lts_cols = [
        "CLASSE",
        "SENS_CIR",
        "slope_edit",
        "Q85",
        "NBLane",
        "ADT",
        "lts",
    ]
    lts_filtered = lts_df[lts_cols].drop_duplicates(keep="first")
    merged_df = road_df.merge(
        lts_filtered, left_index=True, right_index=True, how="left"
    )
    # Any unknown LTS get given a value of 7
    merged_df.loc[merged_df["lts"] < 0, "lts"] = 7
    merged_df["lts"] = merged_df["lts"].fillna(7)

    return merged_df


def get_path_properties(path, df):
    """
    Gets properties of a path based on provided link df.

    parameters:
    path - Path to find properties of.
    df - dataframe containing properties of every link in network.

    Returns - dict keys: column names values: property
    """
    property_dict = {}

    # Length of path
    property_dict["length"] = df.loc[df.index.isin(path), "length"].sum()

    return property_dict


def get_edges_from_nodes(G, path):
    """
    Takes a nx graph and a list of nodes and returns edges used.
    If two nodes do not have a connection, it skips the edge and moves
    on.

    Parameters:
    G - graph used for validation
    path - list of nodes in the sequence of travel

    Returns:
    list of edges used in path.
    """
    edge_list = []
    for i in range (len(path)-1):
        j = i + 1
        start_node, end_node = path[i], path[j]
        try:
            edge = int(G[str(start_node)][str(end_node)]["ID_RD"])
        except:
            continue
        edge_list.append(edge)
        
    return edge_list


def get_path_size_factor(path: list, choice_df: pd.DataFrame, lengths: dict):
    """
    Calculates path size factor for an alternative given a choice set.

    Parameters:
    path - Alternative that PS will be calculated for.

    choice_set - Choice set to use for determining path_size factor.
    Pandas df containing all paths except for the one being analyzed.
    Must contain a column with lists of edges in path and a column of
    length of total path.

    lengths - Dict keys edge_ids, values length of edge.


    Returns - Float: path size factor for input alternative
    """
    path_dict = {}
    for edge in path:
        try:
            path_dict[edge] = lengths[edge]
        except KeyError:
            raise KeyError(f"edge {edge} not in lengths dict")

    L_i = sum(path_dict.values())
    L_c = choice_df["length"].min()

    ps_factor = 0
    for edge in path:
        overlap_df = choice_df[choice_df["edges"].apply(lambda x: edge in x)]
        l_a = path_dict[edge]

        link_path_incidence = 0
        for index, row in overlap_df.iterrows():
            if edge in row["edges"]:
                link_path_incidence += L_c / row["length"]
        ps_factor += (l_a / L_i) * (1 / link_path_incidence)
    return float(ps_factor)
