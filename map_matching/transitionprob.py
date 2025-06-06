"""contains functions to calculate transition probabilities between points"""

from math import exp

import networkx as nx


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


@profile
def transition_probability(pt_i, pt_j, C_i, C_j, G, beta=30):
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
