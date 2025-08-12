"""
Module contains functions to calculate probabilities of candidates for a given point
"""

import math
from shapely import distance
from shapely.geometry import LineString, Point
from numpy import sqrt, pi, exp
from geopandas import GeoSeries

def calculate_bearing(p1, p2):
    """calculates the bearing of the line connecting two points"""

    # p1, p2 are shapely Point geometries (lon, lat)
    lon1, lat1, lon2, lat2 = map(math.radians, [p1.x, p1.y, p2.x, p2.y])
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = math.atan2(x, y)
    return (math.degrees(bearing) + 360) % 360

def link_bearing(line: LineString):
    start = line.coords[0]
    end = line.coords[-1]
    return calculate_bearing(Point(end), Point(start))

def normal_dist_prob(X, mean=0, var=20):
    """calculates the probability of a normal distribution"""
    prob = (1 / (sqrt(2 * pi) * var)) * exp(-((X - mean) ** 2 / (2 * var**2)))
    return prob


def gaussian_distance(point, candidate_geo: GeoSeries, var=20):
    """
    Calculates the probability of a point belonging to segemnt
    takes in a point and list of candidates, optional variance parameter
    outputs a list of probabilities with the same index as the candidates


    """
    can_prob = []
    for candidate in candidate_geo:
        dist = point.distance(candidate)
        prob = normal_dist_prob(dist, 0, var)
        can_prob.append(prob)
    return can_prob


def bearing_error(point_1, point_2, link_candidate, bear_var=20):
    """
    calculate the error comparing gps bearing and link bearing

    parameters:
        bear_var = variance of bearing, eg 20-40 degrees
    """
    b1 = calculate_bearing(point_1, point_2)
    b2 = link_bearing(link_candidate)

    diff = abs(b1 - b2)
    return min(diff, 360 - diff)


def emission_prob(p1, p2, candidate_geo, var=5, bear_var=20, use_bearing=True):
    dist_probability_list = gaussian_distance(p2, candidate_geo, var=5)
    bear_prob_list = []
    if use_bearing==False:
        return dist_probability_list
    for candidate in candidate_geo:
        bear_err= bearing_error(p1, p2, candidate, bear_var=20)
        bear_prob = exp(- (bear_err ** 2) / (2 * bear_var ** 2))
        bear_prob_list.append(bear_prob)
    emission_prob_list = []
    for i in range(0, len(bear_prob_list)):
        emission_prob_list.append(dist_probability_list[i]*dist_probability_list[i])

    return (emission_prob_list)
