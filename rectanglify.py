import geopandas
import numpy as np
from shapely.geometry import Polygon, LineString, MultiLineString, Point
import matplotlib.pyplot as plt

# Args
FILE_IN_PATH = r"C:\Users\traff\source\repos\PrintCities.Modelling\shps\roads.shp"
FILE_OUT_PATH = r"C:\Users\traff\source\repos\PrintCities.Modelling\shps\roads_rect.shp"

# Constants
ETRS89_UTM32N = 3044
WIDTH_MAPPING = {
    # Major roads
    'motorway': 20,
    'trunk': 18,
    'primary': None,
    'secondary': 12,
    'tertiary': 10,

    # Minor roads
    'unclassified': 5,
    'residential': 5,
    'living_street': 5,
    'pedestrian': None,

    # Highway links
    'motorway_link': 12,
    'trunk_link': 10,
    'primary_link': 9,
    'secondary_link': 8,

    # Very small roads
    'service': None,
    'track': None,

    # Paths unsuitable for cars
    'bridleway': None,
    'cycleway': None,
    'footway': None,
    'Path': None,
    'steps': None,

    # Unknown
    'unkown': None,
}

def rectanglify_linesegment(p1, p2, width):

    # Set (x1, y1) as the leftmost point
    x1, y1 = p1
    x2, y2 = p2
    if min(x1, x2) == x2:
        tmp = x1
        x1 = x2 
        x2 = tmp
        tmp = y1 
        y1 = y2 
        y2 = tmp

    # Compute step sizes for x and y
    x_diff = x2-x1
    y_diff = y2-y1
    v = np.array([x_diff, y_diff], dtype=np.float32)
    v /= np.linalg.norm(v)
    N = np.array([y_diff, -x_diff], dtype=np.float32)
    N /= np.linalg.norm(N)
    x_step = N[0] * width / 2
    y_step = N[1] * width / 2
    
    # Compute output points
    out1 = (x1-x_step, y1-y_step)
    out2 = (x1+x_step, y1+y_step)
    out3 = (x2+x_step, y2+y_step)
    out4 = (x2-x_step, y2-y_step)

    rectangle = Polygon([
        out1,
        out2,
        out3,
        out4
    ])

    c1 = Point(p1).buffer(width / 2, resolution=6)
    c2 = Point(p2).buffer(width / 2, resolution=6)

    return rectangle, c1, c2

def rectanglify_line(geometry, width):
    outputs = []
    for idx, coord in enumerate(geometry.coords[:-1]):
        coord_next = geometry.coords[idx+1]
        geoms = rectanglify_linesegment(coord, coord_next, width)
        outputs += geoms
    return outputs

def rectanglify(df):

    df_out = geopandas.GeoDataFrame(columns=['geometry', 'fclass'], crs=ETRS89_UTM32N)

    shapes = []

    for idx, row in df.iterrows():
        geometry = row['geometry']
        fclass = row['fclass']

        if fclass not in WIDTH_MAPPING or WIDTH_MAPPING[fclass] is None:
            continue

        width = WIDTH_MAPPING[fclass]

        if type(geometry) == MultiLineString:
            for line in geometry.geoms:
                shapes += rectanglify_line(line, width)
            continue

        if type(geometry) == LineString:
            shapes += rectanglify_line(geometry, width)
            continue

    for idx, shape in enumerate(shapes):
        row = [shape, fclass]
        df_out.loc[len(df_out) + idx] = row

    return df_out

def main():
    df = geopandas.read_file(FILE_IN_PATH)
    df = rectanglify(df)
    df.to_file(FILE_OUT_PATH)

main()