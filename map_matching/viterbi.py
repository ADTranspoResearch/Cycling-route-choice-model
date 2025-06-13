"""contains viterbi algorithm"""

import math
import pandas as pd
import networkx as nx


def initialize_edge_lookup(G):
    """
    Call this once to populate the edge_lookup
    """

    global edge_lookup  # pylint: disable=W0601
    edge_lookup = {
        data["ID_RD"]: (u, v) for u, v, data in G.edges(data=True) if "ID_RD" in data
    }


def remove_duplicates(lst):
    """
    removes any duplicate values in the given list, returning all unique values in list.
    """

    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def reverse_lookup(d, target_value):
    """
    Searches a dictionary using the values and returns the matching key.
    """

    for key, value in d.items():
        if value == target_value:
            return key
    raise ValueError(f"Value {target_value} not found in dictionary.")


def viterbi(points_df: pd.DataFrame):
    """
    computes most likely sequence of states given observations
    """

    V = [{}]
    backpointer = [{}]

    # --- Step 1: Initialization ---
    first_candidates = points_df.iloc[0]["candidates"]
    first_emissions = points_df.iloc[0]["candidate_probs"]

    for i, candidate in enumerate(first_candidates):
        link_id = candidate["metadata"]["ID_RD"]
        emission_prob = first_emissions[i]
        V[0][link_id] = math.log(emission_prob + 1e-12)  # avoid log(0)
        backpointer[0][link_id] = None

    for t in range(1, len(points_df)):
        V.append({})
        backpointer.append({})

        current_candidates = points_df.iloc[t]["candidates"]
        current_emissions = points_df.iloc[t]["candidate_probs"]

        # 🔄 Use transition probabilities *from previous point* (t - 1)
        transition_dict = points_df.iloc[t - 1]["transition_probs"]

        for i, curr_cand in enumerate(current_candidates):
            curr_link = curr_cand["metadata"]["ID_RD"]
            emission_prob = current_emissions[i]

            best_score = -math.inf
            best_prev_link = None

            for prev_link, prev_score in V[t - 1].items():
                transition_key = (prev_link, curr_link)
                transition_prob = transition_dict.get(
                    transition_key, 1e-12
                )  # or 0.0 if you want to fully exclude

                alpha = 1
                beta = 10
                score = (
                    prev_score
                    + alpha * math.log(transition_prob + 1e-12)
                    + beta * math.log(emission_prob + 1e-12)
                )

                if score > best_score:
                    best_score = score
                    best_prev_link = prev_link

            V[t][curr_link] = best_score
            backpointer[t][curr_link] = best_prev_link
    last_time = len(points_df) - 1
    last_step_scores = V[last_time]
    best_final_link = max(last_step_scores, key=last_step_scores.get)
    path = [best_final_link]
    curr_link = best_final_link

    for t in range(last_time, 0, -1):
        curr_link = backpointer[t][curr_link]
        path.insert(0, curr_link)
    return path


def prune_disconnected_links(path):
    """
    Removes links that are not topologically connected to both previous and next links.

    Args:
        path: list of link IDs (e.g., from Viterbi)
        edge_lookup: dict mapping link ID_RD to (u, v) tuple (start, end nodes)

    Returns:
        A pruned list of link IDs
        a list of node IDs used in the path
    """

    if len(path) <= 2:
        return path  # nothing to prune
    node_path = []
    for node in edge_lookup[path[0]]:
        node_path.append(node)
    for node in edge_lookup[path[1]]:
        if node in node_path:
            node_path.remove(node)
            node_path.append(node)
            break

    pruned_path = [path[0]]  # always keep first

    for i in range(1, len(path) - 1):
        prev_id = path[i - 1]
        curr_id = path[i]
        next_id = path[i + 1]

        prev_u, prev_v = edge_lookup[prev_id]
        curr_u, curr_v = edge_lookup[curr_id]
        next_u, next_v = edge_lookup[next_id]

        # Strict bridging condition:
        # (curr_u connects to prev AND curr_v connects to next) OR
        # (curr_v connects to prev AND curr_u connects to next)
        connects_forward = (
            curr_u in (prev_u, prev_v) and curr_v in (next_u, next_v)
        ) or (curr_v in (prev_u, prev_v) and curr_u in (next_u, next_v))

        if connects_forward:
            pruned_path.append(curr_id)
            for node in (curr_u, curr_v):
                if node not in node_path:
                    node_path.append(node)
        else:
            # Drop the link
            continue

    pruned_path.append(path[-1])  # always keep last
    for node in edge_lookup[path[-1]]:
        if node not in node_path:
            node_path.append(node)
    return pruned_path, node_path


def add_missing_nodes(node_path, graph):
    """
    Ensures that each consecutive pair of nodes in node_path are directly connected.
    If not, inserts the shortest path between them using the graph.

    Args:
        node_path: List of node IDs (e.g., from matched path)
        graph: A NetworkX graph (MultiDiGraph or DiGraph)

    Returns:
        A new node_path list with all intermediate nodes filled in
    """

    if not node_path or len(node_path) < 2:
        return node_path  # nothing to do

    full_path = [node_path[0]]

    for i in range(1, len(node_path)):
        u = node_path[i - 1]
        v = node_path[i]

        if graph.has_edge(u, v):
            # Direct edge exists, just append the node
            full_path.append(v)
        else:
            try:
                # Find shortest path (includes u and v)
                shortest_path = nx.shortest_path(
                    graph, source=u, target=v, weight="length"
                )

                # Append intermediate nodes (excluding first, already added)
                full_path.extend(shortest_path[1:])
            except nx.NetworkXNoPath as e:
                raise ValueError(f"No path between {u} and {v} in the graph.") from e

    return full_path


def node_to_edge_list(node_list):
    """
    Takes a list of nodes and returns a list of edge ids connecting those nodes.
    """

    edge_list = []
    for i in range(0, len(node_list) - 1):

        try:
            edge = reverse_lookup(edge_lookup, (node_list[i], node_list[i + 1]))
        except ValueError:
            try:
                edge = reverse_lookup(edge_lookup, (node_list[i + 1], node_list[i]))
            except ValueError as e:
                print(node_list)
                raise ValueError from e
        edge_list.append(edge)
    return edge_list


def run_viterbi(point_data, graph):
    """
    Runs the entire hmm process with networkx analysis,
    returns list of links in path and list of nodes
    """

    initialize_edge_lookup(graph)
    path = viterbi(point_data)
    path = remove_duplicates(path)
    node_path = path
    path, node_path = prune_disconnected_links(path)
    node_path = add_missing_nodes(node_path, graph)
    path = node_to_edge_list(node_path)
    return path, node_path
