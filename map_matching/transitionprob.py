"""contains functions to calculate transition probabilities between points"""

from math import exp

import networkx as nx
from shapely import Point, LineString
from geopandas import GeoDataFrame

import pandas as pd


# pylint:disable=E0601
try:
    profile  # pyright: ignore
except NameError:

    def profile(func):  # pylint: disable=C0116
        return func


# pylint: enable=C0116
# pylint: enable=E0601

edge_lookup = {}


def initialize_edge_lookup(G):
    """Call this once to populate the edge_lookup"""
    global edge_lookup  # pylint: disable=W0603
    edge_lookup = {
        data["ID_RD"]: (u, v) for u, v, data in G.edges(data=True) if "ID_RD" in data
    }


def project_point_on_edge(point:Point, edge:LineString):
    """
    Projects input point onto edge and returns projected point.
    """
    projected_distance = edge.project(point)
    projected_point = edge.interpolate(projected_distance)
    return projected_point


def transition_probability(points: set, edges: set, network: GeoDataFrame, beta = 30):
    """
    Calculates the probability of transitioning between 2 edges for a given point.

    Determines the probability based on the euclidian distance between points g(t) and
    g(t+1) and the shortest path distance between projected points g_proj(t) and
    g_proj(t+1). Takes the 2 points, 2 candidate edges, and network shapefile as input
    and outputs the probability for those candidates for that point.

    Parameters:
    inputs
        points (set) - set of length 2 containing sets containing 
            point object of points g(t) and g(t+1)
        edges (set) - set of length 2 containing the linestring object 
            of the 2 candidate edges under consideration
        network (Gdf) - Network to be used to determine the shortest 
            path between the projected candidate points

    """
    pt_i, pt_j = list(points)
    edge_i, edge_j = list(edges)

    # 1. Project GPS points onto their candidate edges
    g_proj_i = project_point_on_edge(pt_i, edge_i)
    g_proj_j = project_point_on_edge(pt_j, edge_j)

    # 2. Euclidean distance between raw GPS points
    d_euclid = pt_i.distance(pt_j)

    # 3. Build a graph from the network (nodes + edge lengths)
    G = nx.Graph()
    for _, row in network.iterrows():
        line: LineString = row.geometry
        coords = list(line.coords)
        for k in range(len(coords) - 1):
            u, v = coords[k], coords[k + 1]
            G.add_edge(u, v, length=Point(u).distance(Point(v)))

    # 4. Find nearest graph nodes for the projected points
    def nearest_node(p: Point, graph):
        return min(graph.nodes, key=lambda n: Point(n).distance(p))

    start_node = nearest_node(g_proj_i, G)
    end_node = nearest_node(g_proj_j, G)

    # 5. Compute shortest path distance and transition probability
    try:
        d_path = nx.shortest_path_length(G, source=start_node, target=end_node, weight="length")
        deviation = abs(d_path - d_euclid)
        probability = (1 / beta) * exp(-deviation / beta)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        d_path, deviation, probability = float("inf"), float("inf"), 0.0

    return {
        "pt_i": pt_i.wkt,
        "pt_j": pt_j.wkt,
        "edge_i": str(edge_i.wkt)[:50] + "...",
        "edge_j": str(edge_j.wkt)[:50] + "...",
        "gps_dist": d_euclid,
        "net_dist": d_path,
        "deviation": deviation,
        "probability": probability,
    }


def transition_probabilities_for_candidates(points: tuple, candidates_i: list, candidates_j: list, network, beta: float = 30):
    """
    Calculates transition probabilities for all combinations of candidate edges
    for two consecutive GPS points.

    Parameters
    ----------
    points : tuple
        Two shapely.Point objects (g(t), g(t+1)).
    candidates_i, candidates_j : list
        Lists of candidate edges (LineString).
    network : GeoDataFrame
        Road network (e.g. MATSim network).
    beta : float
        Scale parameter.

    Returns
    -------
    pandas.DataFrame
        Table with transition probabilities for all candidate combinations.
    """
    pt_i, pt_j = points
    results = []
    for edge_i in candidates_i:
        for edge_j in candidates_j:
            result = transition_probability({pt_i, pt_j}, {edge_i, edge_j}, network, beta)
            results.append(result)
    return pd.DataFrame(results)


@profile
def transition_probability_v1(pt_i, pt_j, C_i, C_j, G, beta=30):
    """
    calculates probability of taking one link to the next for all candidates of 2 pts
    """
    gps_dist = pt_i.distance(pt_j)
    trans_probs = {}

    for cand_i in C_i:
        meta_i = cand_i['metadata']
        id_rd_i = meta_i["ID_RD"]
        for cand_j in C_j:
            meta_j = cand_j['metadata']
            id_rd_j = meta_j["ID_RD"]

            # Look up edges from the graph
            if id_rd_i in edge_lookup and id_rd_j in edge_lookup:
                u_i, v_i = edge_lookup[id_rd_i]
                u_j, v_j = edge_lookup[id_rd_j]

                # Choose the direction: either u or v as the representative node
                # Here we choose the end node (v) of the directed edge
                start_node = v_i
                end_node = v_j

                try:
                    net_dist = nx.shortest_path_length(
                        G, source=start_node, target=end_node, weight="length"
                    )
                    deviation = abs(net_dist - gps_dist)
                    prob = (1 / beta) * exp(-deviation / beta)
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    prob = 0.0
            else:
                prob = 0.0

            trans_probs[(id_rd_i, id_rd_j)] = prob

    return trans_probs
