import numpy as np
import geopandas
import rasterio
import rasterio.features
from shapely.geometry import Polygon
import os
import math
from polygonize import polygonize

# Description
# Clips, rectanglifies and rasterizes road SPHs

# Args
FILE_IN_PATH = r"D:\PrintCitiesData\roads_shp\roads_cph.shp"
DIR_OUT_PATH = r"D:\PrintCitiesData\roads_2x2"
BOUNDS_W = 723000
BOUNDS_E = 728000
BOUNDS_S = 6175000
BOUNDS_N = 6180000
AGGREG_SIZE = 2
ALL_TOUCHED = False

# Constants
ETRS89_UTM32N = 3044
ORIGINAL_PIXEL_SIZE = 0.4
BOUNDS_SNAP = 1000
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

    if not os.path.exists(DIR_OUT_PATH):
        os.mkdir(DIR_OUT_PATH)

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

            # Convert to polygons
            df_clipped = polygonize(df_clipped, bounds)

            if len(df_clipped) == 0:
                print(f"skipping {file_name}")
                continue

            # Rasterize 
            transform = rasterio.transform.from_bounds(
                west = bounds[0],
                east = bounds[1],
                south = bounds[2],
                north = bounds[3],
                height = HEIGHT,
                width = WIDTH
            )
            pixels = rasterio.features.rasterize(
                shapes=df_clipped['geometry'],
                out_shape=(HEIGHT, WIDTH),
                fill=0,
                transform=transform,
                all_touched=ALL_TOUCHED,
                default_value=1,
                dtype=np.float32
            )

            # Save
            file_path_tif = os.path.join(DIR_OUT_PATH, file_name + ".tif")
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