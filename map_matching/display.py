"""
Module used for displaying HMM map matched cycling routes for manual
correction and validation.
"""

import folium
from streamlit_folium import st_folium
import streamlit as st
from shapely import LineString, MultiLineString, Point


def interactive_path_correction(links_gdf, trajectory_row, matched_path_gdf):
    """
    Display interactive map for path correction using Streamlit + Folium.
    Allows visualization of full road network, trajectory points,
    and the current matched path.

    Parameters:
        links_gdf (GeoDataFrame): All road links
        trajectory_row (GeoDataFrame): GPS points
        matched_path_gdf (GeoDataFrame): Current matched path

    Returns:
        dict: Data from folium map (e.g., last clicked position)
    """

    st.set_page_config(layout="wide")
    st.title("Interactive Map Matching Tool")

    traj_geom = trajectory_row.geometry
    # Determine map center from trajectory
    if traj_geom.geom_type == "LineString":
        center = traj_geom.centroid
    elif traj_geom.geom_type == "MultiPoint":
        center = traj_geom.geoms[0]
    elif isinstance(traj_geom, list) and isinstance(traj_geom[0], Point):
        center = traj_geom[0]
    else:
        raise ValueError("Unsupported trajectory geometry format.")

    m = folium.Map(location=[center.y, center.x], zoom_start=14)

    # Plot all road links
    for _, row in links_gdf.iterrows():
        geom = row.geometry
        if isinstance(geom, LineString):
            coords_list = [list(geom.coords)]
        elif isinstance(geom, MultiLineString):
            coords_list = [list(line.coords) for line in geom.geoms]
        else:
            continue  # skip unsupported geometries

        for coords in coords_list:
            folium.PolyLine(coords, color="gray", weight=2, opacity=0.3).add_to(m)
    # Plot matched path
    for _, row in matched_path_gdf.iterrows():
        coords = list(row.geometry.coords)
        folium.PolyLine(coords, color="blue", weight=5, opacity=0.9).add_to(m)

    # Trajectory: plot as red points or line
    if traj_geom.geom_type == "LineString":
        folium.PolyLine(
            list(traj_geom.coords), color="red", weight=3, opacity=0.8
        ).add_to(m)
    elif traj_geom.geom_type == "MultiPoint":
        for pt in traj_geom.geoms:
            folium.CircleMarker(
                location=(pt.y, pt.x), radius=4, color="red", fill=True
            ).add_to(m)
    elif isinstance(traj_geom, list) and isinstance(traj_geom[0], Point):
        for pt in traj_geom:
            folium.CircleMarker(
                location=(pt.y, pt.x), radius=4, color="red", fill=True
            ).add_to(m)
    st.subheader("Trajectory + Path Map")
    map_data = st_folium(m, width=1000, height=700)

    # Display latest click (optional: use for editing)
    click = map_data.get("last_clicked", None)
    if click:
        st.info(f"Clicked location: ({click['lat']:.6f}, {click['lng']:.6f})")

    return map_data
