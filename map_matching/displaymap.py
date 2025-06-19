import matplotlib.pyplot as plt
import geopandas as gpd


def display_path(point_data, matched_links):
    fig, ax = plt.subplots(figsize=(10, 10))

    # (Optional) Plot all links in light gray for context
    # links_gdf.plot(ax=ax, color='lightgray', linewidth=1, label='All Roads')

    # Plot the matched path in red
    matched_links.plot(ax=ax, color="red", linewidth=2, label="Matched Path")

    # Plot the GPS points in blue
    point_data.plot(ax=ax, color="blue", markersize=10, label="GPS Points")

    # Add legend and labels
    ax.set_title("Map-Matching: GPS Trajectory and Matched Path")
    ax.legend()
    ax.set_aspect("equal")
    plt.show()


def plot_trajectory_and_path(links_gdf, row, matched_links_gdf, row_index):
    """
    Used to plot cycling trajectories on top of road network and chosen path,
    can be used for map matched path or original path.
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor("white")  # White background

    # Plot full network in light grey
    links_gdf.plot(ax=ax, color="lightgrey", linewidth=1, label="Road Network")

    # Plot trajectory points (can be a MultiPoint or series of Points)
    if row.geometry.geom_type == "LineString":
        # Wrap in GeoSeries to plot
        gpd.GeoSeries([row.geometry]).plot(
            ax=ax, color="blue", linewidth=3, label="Trajectory"
        )

    elif row.geometry.geom_type == "MultiLineString":
        # Convert each LineString in MultiLineString to a separate geometry
        traj_lines = gpd.GeoSeries(list(row.geometry))
        traj_lines.plot(ax=ax, color="blue", linewidth=3, label="Trajectory")

    else:
        raise ValueError(
            f"Unsupported geometry type in trajectory: {row.geometry.geom_type}"
        )

    # Plot matched path in red
    matched_links_gdf.plot(ax=ax, color="red", linewidth=2, label="Matched Path")

    # Zoom to area of interest
    bounds = row.geometry.bounds  # (minx, miny, maxx, maxy)
    padding = 100  # small buffer for visibility
    ax.set_xlim(bounds[0] - padding, bounds[2] + padding)
    ax.set_ylim(bounds[1] - padding, bounds[3] + padding)

    ax.legend()
    ax.axis("off")  # remove axes

    plt.tight_layout()
    return fig
