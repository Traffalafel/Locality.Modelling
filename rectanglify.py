import geopandas
import numpy as np
from shapely.geometry import Polygon, LineString, MultiLineString
import matplotlib.pyplot as plt

# Args
FILE_IN_PATH = r"C:\Users\traff\source\repos\PrintCities.Modelling\shps\roads_clipped.shp"
FILE_OUT_PATH = r"C:\Users\traff\source\repos\PrintCities.Modelling\shps\roads_rect.shp"
WIDTH = 10.0

# Constants
ETRS89_UTM32N = 3044

def rectanglify(p1, p2, width):

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
    x_step_orth = N[0] * width / 2
    y_step_orth = N[1] * width / 2
    x_step = v[0] * width / 2
    y_step = v[1] * width / 2
    
    # Compute output points
    out1 = (x1-x_step_orth-x_step, y1-y_step_orth-y_step)
    out2 = (x1+x_step_orth-x_step, y1+y_step_orth-y_step)
    out3 = (x2+x_step_orth+x_step, y2+y_step_orth+y_step)
    out4 = (x2-x_step_orth+x_step, y2-y_step_orth+y_step)

    return Polygon([
        out1,
        out2,
        out3,
        out4
    ])

def rectanglify_line(geometry, width):
    outputs = []
    for idx, coord in enumerate(geometry.coords[:-1]):
        coord_next = geometry.coords[idx+1]
        rectangle = rectanglify(coord, coord_next, width)
        outputs.append(rectangle)
    return outputs

def rectanglify_dataframe(df, width):

    df_out = geopandas.GeoDataFrame(columns=['geometry', 'fclass'], crs=ETRS89_UTM32N)
    print(df_out)

    for idx, row in df.iterrows():
        geometry = row['geometry']
        fclass = row['fclass']

        if type(geometry) == MultiLineString:
            rectangles = []
            for line in geometry.geoms:
                r = rectanglify_line(line, WIDTH)
                rectangles += r

        if type(geometry) == LineString:
            rectangles = rectanglify_line(geometry, WIDTH)

        for idx, rectangle in enumerate(rectangles):
            row = [rectangle, fclass]
            df_out.loc[len(df_out) + idx] = row

    df_out.plot()
    plt.show()

def main():
    df = geopandas.read_file(FILE_IN_PATH)
    df = rectanglify_dataframe(df, WIDTH)
    # df.plot()
    # plt.show()

main()