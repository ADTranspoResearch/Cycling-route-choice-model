"""
Module contains functions for calculating the cost of traveling on
edges in a graph.
"""


def cyclist_edge_cost(u, v, attributes):
    """
    Calculates the cost of a edge given its attributes.
    """
    # Avg speed assumed to be 17 km/hr, 4.72 m/s
    ini_speed = 4.72

    length = attributes["length"]
    slope = max(min(attributes["slope"], 0.25), -0.1)
    infra = attributes["bike_lane_type"]

    # Assume each % slope slows by 0.635 km/hr, 0.176 m/s
    slope_impact = -0.176

    # Adjust speed by flat coefficient to favour cycling infrasructure
    # if needed.
    if infra in [4,5,6,7]:
        infra_impact = 1
    elif infra == 3:
        infra_impact = 1.25
    elif infra in [0,1,2]:
        infra_impact = 1.5
    else:
        infra_impact = 1.5

    sloped_speed = ini_speed + (slope * 100 * slope_impact)

    cost = length * (infra_impact)
#    print(f"cost {time}")
    
    try:
        return max(1, int(cost))
    except ValueError:
        print(f"length {length}")
        print(f"slope {slope}")
        print(f"infra {infra}")
        print(f"sloped speed {sloped_speed}")
        print(f"time {cost}")
        print(type(cost))
        raise
