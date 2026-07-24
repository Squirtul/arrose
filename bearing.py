
# determines an acfts bearing from the aerodrome, then puts it into a sector

from math import radians, degrees, atan2, sin, cos

def bearing_from_airport(airport, plane):

    lat1 = radians(airport[0])
    lon1 = radians(airport[1])

    lat2 = radians(plane["latitude"])
    lon2 = radians(plane["longitude"])

    dlon = lon2 - lon1

    x = sin(dlon) * cos(lat2)
    y = (
        cos(lat1) * sin(lat2)
        - sin(lat1) * cos(lat2) * cos(dlon)
    )

    bearing = (degrees(atan2(x, y)) + 360) % 360
    return bearing


def get_sector(bearing):
    # 8 sectors required as of now.. can add some logic to this to make sector numbers customisable later
    return int(bearing // 45) % 8