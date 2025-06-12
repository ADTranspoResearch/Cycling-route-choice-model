import geopandas as gpd
import pandas as pd

# File paths
road_and_off_path = 'shapefiles/map_matching/road_and_off_bike_network.dbf'
merged_2015_path = 'shapefiles/map_matching/2015merged_network_file.dbf'
output_path = 'shapefiles/map_matching/road_and_off_bike_network_modified.dbf'

# Load DBF files into GeoDataFrames
road_and_off_df = gpd.read_file(road_and_off_path)
merged_2015_df = gpd.read_file(merged_2015_path)

# Drop rows in merged_2015_df where either ID_TRC_GEO or ID is NaN before casting
merged_2015_df = merged_2015_df.dropna(subset=['ID_TRC_GEO', 'ID'])

# Cast to integers
merged_2015_df['ID_TRC_GEO'] = merged_2015_df['ID_TRC_GEO'].astype(int)
merged_2015_df['ID'] = merged_2015_df['ID'].astype(int)

# Build lookup dictionary: {ID_TRC_GEO: ID}
id_lookup = dict(zip(merged_2015_df['ID_TRC_GEO'], merged_2015_df['ID']))

# If necessary, drop NaNs from road_and_off_df['ID_RD'] and cast to int
road_and_off_df = road_and_off_df.dropna(subset=['ID_RD'])
road_and_off_df['ID_RD'] = road_and_off_df['ID_RD'].astype(int)

# Replace 'ID_RD' values using the lookup
road_and_off_df['ID_RD'] = road_and_off_df['ID_RD'].apply(
    lambda x: id_lookup.get(x, x)
)

# Save the modified DataFrame
road_and_off_df.to_file(output_path, driver='ESRI Shapefile')

print("Modified file saved to:", output_path)
