"""
Module contains function for calculating all alternatives on the next
level of the BFSLE tree for a given path and network.
"""

import networkx as nx
from BFSLE.weights import cyclist_edge_cost


def euclidian(G, a, b):
    """Calcualtes euclidian distance between 2 nx nodes."""
    x1, y1 = G.nodes[a]["x"], G.nodes[a]["y"]
    x2, y2 = G.nodes[b]["x"], G.nodes[b]["y"]

    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def manhattan(G, a, b):
    """Calcualtes manhattan distance between 2 nx nodes."""
    x1, y1 = G.nodes[a]["x"], G.nodes[a]["y"]
    x2, y2 = G.nodes[b]["x"], G.nodes[b]["y"]

    return abs((x2 - x1)) + abs((y2 - y1))


def get_sp_tree(
    G: nx.Graph, original_path: list, od: tuple, edge_removals: list, set_size: int
):
    """
    Takes a nx network and a path along that network and calculates each
    shortest path after removing 1 edge from the original path inputted.


    Returns a dictionary containing the alternate path and which edges
    were removed from the graph.

    Parameters:
        inputs:
        G - nx.Graph Base graph to remove edges from and calculate
        shortest path on.

        original_path - list: List of nodes who's connections will be
        iteratively removed and replaced when calcualting the
        alternative routes.

        od - tuple: Origin and destination nodes to find path between.

        edge_removals - list of tuples: Optional list of node tuples 
        who's connections were removed when the original_path was
        created, so must be removed from the graph before calculating
        any alternatives.

        set_size - int: Function will stop early once this number of
        alternatives is reached.


        Returns:
        List of dicts - Dict format:
            {
            "sp": alternative route,
            "removed_edges": edges removed from graph when alternative
            was calculated
            }
    """
    # Backup and remove edges that must be hidden initially.
    edge_storage = [(u, v, G[u][v].copy()) for u, v in edge_removals]
    G.remove_edges_from(edge_removals)

    # Loop through each edge in the original path and calculate a new
    # alternative route. Through each calculation, 1 edge is removed
    # and restored after each shortest path calculation.
    tree_level_sp_list = []
    for i in range(len(original_path) - 1):
        j = i + 1
        node_1 = original_path[i]
        node_2 = original_path[j]

        # Save and remove edge from original path.
        removed_edge = (node_1, node_2, G[node_1][node_2].copy())
        G.remove_edge(node_1, node_2)
        try:
            sp = nx.astar_path(
                G,
                od[0],
                od[1],
                heuristic=lambda u, v: euclidian(G, u, v),
                weight=cyclist_edge_cost,
            )
        except nx.NetworkXNoPath:
            continue
        finally:
            # Always restores edge from path.
            G.add_edge(removed_edge[0], removed_edge[1], **removed_edge[2])

        removed_edges = edge_removals + [removed_edge[:-1]]
        tree_level_sp_list.append({"sp": sp, "removed_edges": removed_edges})
        if len(tree_level_sp_list) > set_size:
            break

    # Restore edges that were removed before the for loop.
    for u, v, attr in edge_storage:
        G.add_edge(u, v, **attr)

    return tree_level_sp_list
