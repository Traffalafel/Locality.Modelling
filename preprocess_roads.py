import numpy as np
import geopandas
import rasterio
from shapely.geometry import Polygon
import os
import math
from rasterize import rasterize
from rectanglify import rectanglify
import matplotlib.pyplot as plt

# Args
FILE_IN_PATH = r"C:\Users\traff\source\repos\PrintCities.Modelling\shps\roads_cph.shp"
SHP_DIR_OUT_PATH = r"D:\PrintCitiesData\roads_shp"
TIF_DIR_OUT_PATH = r"D:\PrintCitiesData\roads_tif"
BOUNDS_W = 700000
BOUNDS_E = 731000
BOUNDS_S = 6170000
BOUNDS_N = 6201000
BOUNDS_SNAP = 1000

# Constants
ETRS89_UTM32N = 3044
ORIGINAL_PIXEL_SIZE = 0.4
AGGREG_SIZE = 4
ORIGINAL_SIZE = 2500

# Derived constants
PIXEL_SIZE = ORIGINAL_PIXEL_SIZE * AGGREG_SIZE
HEIGHT = int(ORIGINAL_SIZE / AGGREG_SIZE)
WIDTH = int(ORIGINAL_SIZE / AGGREG_SIZE)

def clip(dataframe, bounds):
    
    dataframe = dataframe.to_crs(ETRS89_UTM32N)

    bounds_w, bounds_e, bounds_s, bounds_n = bounds
    polygon = Polygon([
        (bounds_w, bounds_s),
        (bounds_w, bounds_n),
        (bounds_e, bounds_n),
        (bounds_e, bounds_s)
    ])
    poly_gdf = geopandas.GeoDataFrame([1], geometry=[polygon], crs=dataframe.crs)

    return geopandas.clip(dataframe, poly_gdf)
    
def main():

    # Compute bounds
    bounds_w = math.ceil(BOUNDS_W / BOUNDS_SNAP)
    bounds_e = math.floor(BOUNDS_E / BOUNDS_SNAP)
    bounds_s = math.ceil(BOUNDS_S / BOUNDS_SNAP)
    bounds_n = math.floor(BOUNDS_N / BOUNDS_SNAP)

    df = geopandas.read_file(FILE_IN_PATH)

    for y in range(bounds_s, bounds_n):
        for x in range(bounds_w, bounds_e):

            # Define bounds and clip
            bounds = (
                x*BOUNDS_SNAP + (PIXEL_SIZE/2),
                (x+1)*BOUNDS_SNAP + (PIXEL_SIZE/2),
                y*BOUNDS_SNAP + (PIXEL_SIZE/2),
                (y+1)*BOUNDS_SNAP + (PIXEL_SIZE/2)
            )
            df_clipped = clip(df, bounds)

            file_name = f"roads_{y}_{x}"

            if len(df_clipped) == 0:
                print(f"skipping {file_name}")
                continue

            # Save shp file
            file_path_shp = os.path.join(SHP_DIR_OUT_PATH, file_name + ".shp")
            df_clipped.to_file(file_path_shp)

            # Rectanglify
            df_clipped = rectanglify(df_clipped, bounds)

            if len(df_clipped) == 0:
                print(f"skipping {file_name}")
                continue

            file_path_shp_rect = os.path.join(SHP_DIR_OUT_PATH, file_name + "_rect.shp")
            df_clipped.to_file(file_path_shp_rect)

            # Rasterize and save
            file_path_tif = os.path.join(TIF_DIR_OUT_PATH, file_name + ".tif")
            pixels, transform = rasterize(df_clipped, bounds, HEIGHT, WIDTH)
            dataset_out = rasterio.open(
                file_path_tif,
                mode='w',
                driver='GTiff',
                height=HEIGHT,
                width=WIDTH,
                count=1,
                crs=df_clipped.crs,
                transform=transform,
                dtype=np.float32
            )
            dataset_out.write(pixels, 1)

            print(f"saved {file_name}")

main()