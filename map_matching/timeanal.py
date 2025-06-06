"""module contains diagnostic function for loop time length"""


def point_time(index, points, tik, tok):
    """takes in number of points, tik and tok and outputs duration info"""

    time_delta = tok - tik
    print(
        f"trip #{index} had {points} points and took {time_delta} sec, or {time_delta/points} sec per point"
    )
