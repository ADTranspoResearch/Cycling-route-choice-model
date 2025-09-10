import geopandas as gpd
import pandas as pd

from candidatesearch import create_network_rtree
from mapmatching import run_map_matching
from transitionprob import build_graph
shapefile_path_network = "shapefiles/map_matching/2015merged_network_file.shp"

shapefile_path_trips = "shapefiles/map_matching/island_cyclist_trips.shp"

shp_network_full = gpd.read_file(shapefile_path_network)
shp_trip = gpd.read_file(shapefile_path_trips)
shp_network_full = shp_network_full.to_crs("EPSG:32188")
shp_trip = shp_trip.to_crs("EPSG:32188")
G = None

id_trc_geo_list = shp_network_full["ID_TRC_GEO"].unique()

series = pd.Series(id_trc_geo_list)

clean_int_list = series.dropna().astype(int).tolist()

shp_network = shp_network_full[
    ~shp_network_full["ID_RD"].isin(clean_int_list)
].copy()

str_tree, subsegments, subseg_metadata = create_network_rtree(shp_network)
tree_data = (str_tree, subsegments, subseg_metadata)


row_index = 0
row = shp_trip.iloc[row_index]

graph = build_graph(shp_network_full)
path, node_path, matched_links = run_map_matching(
            row_index,
            row,
            tree_data,
            G,
            shp_network_full,
            graph
        )