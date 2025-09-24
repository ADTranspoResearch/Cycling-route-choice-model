"""
This module takes the modified cyclist trajectories from manual map matching
and determines the path of links used on the road network and saves that to a csv
with other data based on the cyclist id.
"""

import os
import re

import geopandas as gpd
import pandas as pd
# Directoy containing road network
road_network_filepath = "shapefiles/map_matching/road_and_off_bike_network_modified.shp"
road_network = gpd.read_file(road_network_filepath)

# Directory containing the cyclist trajectory shapefiles
trajectories_dir = "manual_map_matching/cyclist_modified_trajectories"

# Directory for writing the csv file with the chosen path data.
chosen_path_filepath = 'manual_map_matching/cyclist_chosen_path.csv'
chosen_path = pd.read_csv(chosen_path_filepath, index_col="id_origine")
cyclist_data_filepath = 'cyclists/cyclists_trips.csv'
cyclist_data = pd.read_csv(cyclist_data_filepath, index_col="id_origine")

# Regex pattern to extract the cyclist id from the filename
pattern = re.compile(r"id_origine_(\d+)\.shp$")

for filename in os.listdir(trajectories_dir):
    if filename.endswith(".shp"):
        match = pattern.match(filename)
        if match:
            cyclist_id = int(match.group(1))
            filepath = os.path.join(trajectories_dir, filename)
            trajectory = gpd.read_file(filepath)

            # Find nearest road network object for each point in the trajectory
            # and extract the 'ID_RD' value
            # Ensure both GeoDataFrames use the same CRS
            if trajectory.crs != road_network.crs:
                trajectory = trajectory.to_crs(road_network.crs)

            # Use sjoin_nearest to find nearest road segment for each point
            joined = gpd.sjoin_nearest(
                trajectory,
                road_network[["ID_RD", "geometry"]],
                how="left",
                distance_col="distance_to_road",
            )

            # Extract the 'ID_RD' column as a list, keeping only unique values in order
            id_rd_list = joined["ID_RD"].tolist()
            seen = set()
            unique_id_rd = []
            for val in id_rd_list:
                if val not in seen:
                    unique_id_rd.append(val)
                    seen.add(val)
            # Add or update the row for this cyclist_id in chosen_path
            # Store the unique_id_rd list as a string for CSV compatibility
            chosen_path.loc[cyclist_id, "path"] = str(unique_id_rd)



# Update chosen_path with 'original_length' and 'purpose' from cyclist_data for matching indices
if 'original_length' not in chosen_path.columns:
    chosen_path['original_length'] = None
if 'purpose' not in chosen_path.columns:
    chosen_path['purpose'] = None

for idx in chosen_path.index:
    if idx in cyclist_data.index:
        chosen_path.at[idx, 'original_length'] = cyclist_data.at[idx, 'length']
        chosen_path.at[idx, 'purpose'] = cyclist_data.at[idx, 'purpose']

chosen_path.to_csv(chosen_path_filepath, index_label="id_origine")