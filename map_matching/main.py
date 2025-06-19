"""Main code that runs the map matching function and displays results"""

import streamlit as st

from displaymap import plot_trajectory_and_path
from mapmatching import run_map_matching
from stutils import initialize

# Steps of the code
#
# Step 1 - Imports:
# Road network shapefile.
# Trajectory shapefile.
# Road network NetworkX graph.

# Get filepaths of the necessary files

st.title('Manual Map Matching Correction')
status_placeholder = st.empty()
if "initialized" not in st.session_state:
    status_placeholder.write("Initializing...")
    initialize()
    st.session_state.initialized = True
    status_placeholder.write('Initializing complete')

if "row_index" not in st.session_state:
    # Ask user for the starting row index
    start_index = st.number_input(
        "Enter the starting row index:",
        min_value=0,
        step=1,
    )

    if st.button("Start"):
        st.session_state.row_index = int(start_index)
        st.rerun()  # rerun to proceed with initialized session state
    else:
        st.stop()  # wait until user presses "Start"
if "confirmed" not in st.session_state:
    st.session_state.confirmed = False
if "cached_row_index" not in st.session_state:
    st.session_state.cached_row_index = -1  # initialize to something invalid


# Get current row
row_index = st.session_state.row_index

if row_index >= len(st.session_state.shp_trip):
    st.success("✅ All paths reviewed!")
    st.session_state.output_df.to_csv(st.session_state.output_path)
    st.stop()

if st.session_state.cached_row_index != row_index:
    status_placeholder.write(f'calculating trip #{row_index}...')
    row = st.session_state.shp_trip.iloc[row_index]
    try:
        path, node_path, matched_links = run_map_matching(
            row_index, row, st.session_state.tree_data, st.session_state.G, st.session_state.shp_network_full
        )
    except Exception as e:
        st.warning(f"Mapmatching error in trip {row_index}, skipping...")
        new_row = (row['id_origine'],None,f'MM Error:{e}')
        df_length = len(st.session_state.output_df)
        st.session_state.output_df.loc[df_length] = new_row
        st.session_state.row_index += 1
        st.rerun()
    st.session_state.cached_row_index = row_index
    st.session_state.row = row
    st.session_state.path = path
    st.session_state.node_path = node_path
    st.session_state.matched_links = matched_links
    
    fig = plot_trajectory_and_path(st.session_state.shp_network_full, row, matched_links, row_index)
    status_placeholder.write(f'Map matched path for trip #{row_index}')
    st.pyplot(fig)

row = st.session_state.row
path = st.session_state.path
node_path = st.session_state.node_path
matched_links = st.session_state.matched_links
center = row.geometry.centroid


# Plot background network

# Buttons
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("✅ No errors in path"):
        int_path = list(map(int, path))
        new_row = (row['id_origine'],int_path,'no')
        df_length = len(st.session_state.output_df)
        st.session_state.output_df.loc[df_length] = new_row
        st.session_state.row_index += 1
        st.rerun()
with col2:
    if st.button("🟨 Minor errors (less than 3)"):
        int_path = list(map(int, path))
        new_row = (row['id_origine'],int_path,'minor')
        df_length = len(st.session_state.output_df)
        st.session_state.output_df.loc[df_length] = new_row
        st.session_state.row_index += 1
        # Reset logic if needed
        st.rerun()
with col3:
    if st.button("🟥 Major errors"):
        int_path = list(map(int, path))
        new_row = (row['id_origine'],int_path,'major')
        df_length = len(st.session_state.output_df)
        st.session_state.output_df.loc[df_length] = new_row
        st.session_state.row_index += 1
        # Reset logic if needed
        st.rerun()
with col4:
    if st.button("🛑 Exit and save changes"):
        st.success("Saving changes to correction file")
        st.session_state.output_df.to_csv(st.session_state.output_path)
        st.stop()