import streamlit as st
import networkx as nx
import pandas as pd
import geopandas as gpd

from candidatesearch import create_network_rtree


def initialize():
    """
    Initializes data heavy variables that do not need to be run
    each iteration.
    """

    print("running init")
    shapefile_path_network = "shapefiles/map_matching/2015merged_network_file.shp"

    shapefile_path_trips = "shapefiles/map_matching/island_cyclist_trips.shp"

    shp_network_full = gpd.read_file(shapefile_path_network)
    shp_trip = gpd.read_file(shapefile_path_trips)
    shp_network_full = shp_network_full.to_crs("EPSG:32188")
    shp_trip = shp_trip.to_crs("EPSG:32188")
    graph_path = "road_network_2015_with_coords.graphml"
    st.session_state.output_path = "map_matching/validation/manual_path_correction.csv"
    G = nx.read_graphml(graph_path)
    id_trc_geo_list = shp_network_full["ID_TRC_GEO"].unique()
    series = pd.Series(id_trc_geo_list)
    clean_int_list = series.dropna().astype(int).tolist()
    shp_network = shp_network_full[
        ~shp_network_full["ID_RD"].isin(clean_int_list)
    ].copy()
    str_tree, subsegments, subseg_metadata = create_network_rtree(shp_network)
    tree_data = (str_tree, subsegments, subseg_metadata)
    st.session_state.G = G
    st.session_state.shp_network = shp_network
    st.session_state.shp_network_full = shp_network_full
    st.session_state.shp_trip = shp_trip
    st.session_state.tree_data = tree_data
    st.session_state.output_df = pd.read_csv(
        st.session_state.output_path, index_col="index"
    )
    st.session_state.exit_pressed = False

def handle_exit():
    st.session_state.exit_pressed = True
    st.session_state.output_df.to_csv(st.session_state.output_path)
