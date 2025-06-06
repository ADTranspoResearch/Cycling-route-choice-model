import matplotlib.pyplot as plt

def display_path(point_data, matched_links):
    fig, ax = plt.subplots(figsize=(10, 10))

    # (Optional) Plot all links in light gray for context
    #links_gdf.plot(ax=ax, color='lightgray', linewidth=1, label='All Roads')

    # Plot the matched path in red
    matched_links.plot(ax=ax, color='red', linewidth=2, label='Matched Path')

    # Plot the GPS points in blue
    point_data.plot(ax=ax, color='blue', markersize=10, label='GPS Points')

    # Add legend and labels
    ax.set_title("Map-Matching: GPS Trajectory and Matched Path")
    ax.legend()
    ax.set_aspect('equal')
    plt.show()
