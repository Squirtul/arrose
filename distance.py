
# find acfts distance to airport. airport coords 

from geopy.distance import geodesic

def distance_to_airport(plane, arptLoc):
    plane_position = (
        plane["latitude"],
        plane["longitude"],
    )

    distance = geodesic(plane_position, arptLoc).nautical
    return distance
