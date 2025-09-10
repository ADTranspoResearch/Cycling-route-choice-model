"""contains functions to calculate transition probabilities between points"""

from math import exp

import networkx as nx
from shapely import Point, LineString, MultiLineString
from geopandas import GeoDataFrame

import pandas as pd



def build_graph(network):
    G = nx.Graph()
    for _, row in network.iterrows():
        geom = row.geometry
        if isinstance(geom, LineString):
            lines = [geom]
        elif isinstance(geom, MultiLineString):
            lines = list(geom.geoms)
        else:
            continue

        for line in lines:
            coords = list(line.coords)
            for k in range(len(coords) - 1):
                u, v = coords[k], coords[k + 1]
                G.add_edge(u, v, length=Point(u).distance(Point(v)))
    return G


def project_point_on_edge(point:Point, edge:LineString):
    """
    Projects input point onto edge and returns projected point.
    """
    projected_distance = edge.project(point)
    projected_point = edge.interpolate(projected_distance)
    return projected_point

def insert_projection_in_graph(G: nx.Graph, edges: LineString, proj_points: Point):
    """
    Splits an edge in the graph at the projected point and inserts that point as a new node.

    Parameters
    ------
    G: networkx graph representing road network to be modified
    edges: tuple of size 2 containing candidate edge LineStrings for both points in
        proj_points. these may be the same edge.
    proj_points: tuple of size 2 containing the projected points that should be added
        as nodes to the network
    
    Returns:
        nodes: tuple of length 2 containing the new start and end nodes
        old_edges: list containing edges that have been removed
    
    """
    old_edges = []
    if edges[0] == edges[1]: # Same edge case.
        coords = list(edges[0].coords)
        u, v = coords[0], coords[-1]        
        if G.has_edge(u, v):
            old_edges.append((u, v, G[u][v].copy()))
            G.remove_edge(u, v)

        # Add points as nodes, must find which point is closer to which
        # node.
        proj_node_1 = (proj_points[0].x, proj_points[0].y)
        proj_node_2 = (proj_points[1].x, proj_points[1].y)

        dist_u_1 = Point(u).distance(proj_points[0])
        dist_u_2 = Point(u).distance(proj_points[1])
        dist_points =proj_points[0].distance(proj_points[1])
        dist_1_v = proj_points[0].distance(Point(v))
        dist_2_v = proj_points[1].distance(Point(v))

        if dist_u_1 <dist_u_2: #First point closer to start node.
            G.add_edge(u, proj_node_1, length=dist_u_1)
            G.add_edge(proj_node_1, proj_node_2, length=dist_points)
            G.add_edge(proj_node_2, v, length=dist_2_v)
        elif dist_u_1 > dist_u_2: #second point closer to start node.
            G.add_edge(u, proj_node_2, length=dist_u_2)
            G.add_edge(proj_node_1, proj_node_2, length=dist_points)
            G.add_edge(proj_node_1, v, length=dist_1_v)
        else:
            raise ValueError('projections same distance from start')
        proj_nodes = (proj_node_1, proj_node_2)
    else: #2 different edges
        proj_nodes = []
        for i, edge in enumerate(edges):
            coords = list(edge.coords)
            u, v = coords[0], coords[-1]
            proj_node = (proj_points[i].x, proj_points[i].y)
            if not G.has_node(proj_node):
                if G.has_edge(u, v):
                    old_edges.append((u, v, G[u][v].copy()))
                    G.remove_edge(u, v)
                G.add_node(proj_node)
                            # Distances
                dist_u_p = Point(u).distance(proj_points[i])
                dist_p_v = proj_points[i].distance(Point(v))
                # Add two new edges
                G.add_edge(u, proj_node, length=dist_u_p)
                G.add_edge(proj_node, v, length=dist_p_v)
                u, v = coords[0], coords[-1]        




            # Add projected point as a node

            proj_nodes.append(proj_node)
        proj_nodes = tuple(proj_nodes)
    # return proj_node AND original edge for restoration
    return proj_nodes, old_edges


def remove_projection_from_graph(G, new_nodes: tuple, old_edges: list):
    """
    Reverses insert_projection_in_graph by removing the projected node and restoring the original edge.

    new_nodes: tuple size 2 containing temp nodes that must be removed from G

    old_edges: list containing tuple size 3 (u, v, edge_data)
    """
    #TODO: Find a way to avoid removing original nodes from graph
    for node in new_nodes:
        if G.has_node(node):
            G.remove_node(node)

    for u, v, data in old_edges:

        if not G.has_edge(u, v):
            G.add_edge(u, v, **data)


def transition_probability(points: set, edges: set, G, beta = 30):
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


    # 4. Insert projected points into graph
    print(f"number of edges before: {G.number_of_edges()}")
    print(f"number of nodes before: {G.number_of_nodes()}")
    #start_node, start_edge = insert_projection_in_graph(G, edge_i, g_proj_i)
    #end_node, end_edge = insert_projection_in_graph(G, edge_j, g_proj_j)
    new_nodes, old_edges = insert_projection_in_graph(G, (edge_i,edge_j),(g_proj_i,g_proj_j))
    print("number of edges after insert:", G.number_of_edges())
    print(f"number of nodes after insert: {G.number_of_nodes()}")
    # 5. Compute shortest path distance and transition probability
    try:
        d_path = nx.shortest_path_length(G, source=new_nodes[0], target=new_nodes[1], weight="length")
        deviation = abs(d_path - d_euclid)
        probability = (1 / beta) * exp(-deviation / beta)

    except (nx.NetworkXNoPath, nx.NodeNotFound):
        probability = 0.0
    remove_projection_from_graph(G, new_nodes, old_edges)
    print("After remove:", G.number_of_edges())
    print(f"number of nodes after remove: {G.number_of_nodes()}")
#    remove_projection_from_graph(G, start_node, start_edge)
#    remove_projection_from_graph(G, end_node, end_edge)
    return probability


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
            prob = transition_probability({pt_i, pt_j}, {edge_i, edge_j}, network, beta)
            results.append({
                "pt_i": pt_i.wkt,
                "pt_j": pt_j.wkt,
                "edge_i": str(edge_i.wkt)[:50] + "...",
                "edge_j": str(edge_j.wkt)[:50] + "...",
                "probability": prob
            })
    return pd.DataFrame(results)


