"""module contains function for creating R-tree of road network file"""

from shapely.geometry import LineString, MultiLineString
from shapely.strtree import STRtree


def create_network_rtree(net_gdf):
    """
    Takes a GeoDataFrame of road network and returns:

    - STRtree built on subsegments
    - list of subsegment geometries
    - List of dicts: (subsegment ID_RD, parent index)
    """

    subsegments = []
    metadata = []

    for idx, row in net_gdf.iterrows():
        geom = row.geometry
        id_rd = row["ID_RD"]
        # Handle MultiLineString by looping over each LineString
        if isinstance(geom, MultiLineString):
            lines = geom.geoms  # list of LineStrings
        elif isinstance(geom, LineString):
            lines = [geom]
        else:
            continue  # Skip unsupported geometry types
        for line in lines:
            coords = list(line.coords)
            for i in range(len(coords) - 1):
                seg = LineString([coords[i], coords[i + 1]])
                subsegments.append(seg)
                metadata.append({"ID_RD": id_rd, "parent_index": idx})
    str_tree = STRtree(subsegments)
    return str_tree, subsegments, metadata


def k_nearest_segments(point, str_tree, subsegments, metadata, k=5, search_radius=10):
    """Returns the k-nearest subsegments with at least k unique ID_RD values."""
    radius = search_radius

    while True:
        buffer_geom = point.buffer(radius)
        indices = str_tree.query(buffer_geom)

        # Extract candidate data and deduplicate based on ID_RD
        candidate_data = [(i, subsegments[i], metadata[i]) for i in indices]
        unique_by_id_rd = {}
        for i, geom, meta in candidate_data:
            id_rd = meta["ID_RD"]
            if id_rd not in unique_by_id_rd:
                unique_by_id_rd[id_rd] = (i, geom, meta)

        if len(unique_by_id_rd) >= k:
            break

        radius *= 2  # Expand search area

    # Now sort the filtered unique segments by distance to point
    sorted_unique = sorted(unique_by_id_rd.values(), key=lambda x: point.distance(x[1]))
    # Convert to list of dictionaries
    result = [
        {'index': i, 'geometry': geom, 'metadata': meta}
        for i, geom, meta in sorted_unique[:k]
    ]
    return result  # Each item is a dictionary
