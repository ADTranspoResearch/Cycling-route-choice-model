"""
This module takes the modified cyclist trajectories from manual map
matching and determines the path of links used on the road network and
saves that to a csv with other data based on the cyclist id.
"""

import os
import re
from itertools import groupby

import geopandas as gpd
import pandas as pd


# Directoy containing road network
road_network_filepath = (
    "shapefiles/map_matching/road_and_off_bike_network_modified.shp"
)
road_network = gpd.read_file(road_network_filepath)

# Directory containing the cyclist trajectory shapefiles
trajectories_dir = "manual_map_matching/cyclist_map_matched"

# Directory for writing the csv file with the chosen path data.
chosen_path_filepath = "manual_map_matching/cyclist_chosen_path_node.csv"
chosen_path = pd.read_csv(chosen_path_filepath, index_col="id_origine")

cyclist_data_filepath = "cyclists/cyclists_trips.csv"
cyclist_data = pd.read_csv(cyclist_data_filepath, index_col="id_origine")

# Directory containing road network nodes.
edge_node_filepath = "shapefiles/2015 verticies with node id_geometry.csv"
edge_node_df = pd.read_csv(edge_node_filepath)
node_gdf = gpd.GeoDataFrame(
    edge_node_df,
    geometry=gpd.points_from_xy(edge_node_df["X"], edge_node_df["Y"]),
    crs="EPSG:32188",
)

# Regex pattern to extract the cyclist id from the filename
pattern = re.compile(r"id_origine_(\d+)\.shp$")

for filename in os.listdir(trajectories_dir):
    if filename.endswith(".shp"):
        match = pattern.match(filename)
        if match:
            cyclist_id = int(match.group(1))
            print(f"cyclist {cyclist_id}")
            filepath = os.path.join(trajectories_dir, filename)
            trajectory = gpd.read_file(filepath)

            # Find nearest road network object for each point in the
            # trajectory and extract the 'ID_RD' value
            # Ensure both GeoDataFrames use the same CRS.
            if trajectory.crs != road_network.crs:
                trajectory = trajectory.to_crs(road_network.crs)

            # Use sjoin_nearest to find nearest segment for each point.
            joined = gpd.sjoin_nearest(
                trajectory,
                road_network[["ID_RD", "geometry"]],
                how="left",
                distance_col="distance_to_road",
            )

            trajectory_with_roads = joined[["geometry", "ID_RD"]].copy()

            nodes_by_road = {
                rid: group for rid, group in node_gdf.groupby("ID_RD")
            }
            nearest_nodes = []
            for idx, row in trajectory_with_roads.iterrows():
                road_id = row["ID_RD"]
                point = row["geometry"]

                # Candidate nodes: only those on this road.
                candidates = nodes_by_road.get(road_id)

                if candidates is not None and not candidates.empty:
                    # Find nearest candidate node by distance.
                    distances = candidates.geometry.apply(point.distance)
                    nearest_idx = distances.idxmin()
                    nearest_nodes.append(
                        candidates.loc[nearest_idx, "node_id"]
                    )
                else:
                    continue

            # Removes all duplicates of nodes that occur in succession
            # but keeps nodes that appear again after a different node
            # appears in the sequence.
            sandwich_node_ids = [k for k, _ in groupby(nearest_nodes)]

            # Remove nodes that are sandwhiched between the same node.
            # If a the path is 1,2,1,3, then travelling to node 2 is not
            # necessary and can be removed.
            non_repeat_nodes = [x for i, x in enumerate(sandwich_node_ids)
                if i in (0, len(sandwich_node_ids)-1) or sandwich_node_ids[i-1] != sandwich_node_ids[i+1]]

            unique_node = [float(k) for k, _ in groupby(non_repeat_nodes)]
            # Store unique_id_rd list as a string for CSV compatibility.
            chosen_path.loc[cyclist_id, "node_path"] = str(
                unique_node
            )


# Update chosen_path with 'original_length' and 'purpose' from
# cyclist_data for matching indices.
if "original_length" not in chosen_path.columns:
    chosen_path["original_length"] = None
if "purpose" not in chosen_path.columns:
    chosen_path["purpose"] = None

for idx in chosen_path.index:
    if idx in cyclist_data.index:
        chosen_path.at[idx, "original_length"] = cyclist_data.at[idx, "length"]
        chosen_path.at[idx, "purpose"] = cyclist_data.at[idx, "purpose"]

chosen_path.to_csv(chosen_path_filepath, index_label="id_origine")
