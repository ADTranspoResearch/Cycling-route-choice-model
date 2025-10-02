"""
Module contains functions for calculating the cost of traveling on
edges in a graph.
"""


def cyclist_edge_cost(u, v, attributes):
    """
    Calculates the cost of a edge given its attributes.
    """
    # Avg speed assumed to be 17 km/hr, this is in m/s
    ini_speed = 4.72

    length = attributes["length"]
    slope = attributes["slope"]
    infra = attributes["bike_lane_type"]

    # Assume each % slope slows by 0.635 km/hr, 0.176 m/s
    slope_impact = -0.176

    # Adjust speed by flat coefficient to favour cycling infrasructure
    # if needed. values below 1 decrease total time, above 1 increase.
    if infra == 0:
        infra_impact = 1
    else:
        # Any infrastructure reduces time by 5%
        infra_impact = 0.95

    sloped_speed = ini_speed + (slope * 100 * slope_impact)

    time = (length / (sloped_speed)) * infra_impact

    return time
