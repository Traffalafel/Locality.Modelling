import numpy as np
import geopandas
import rasterio
from shapely.geometry import Polygon
import os
import sys
import math

# Args
TILE_SIZE = 1000
OFFSET_HALF = True
# BOUNDS_W = 700000
# BOUNDS_E = 730000
# BOUNDS_S = 6170000
# BOUNDS_N = 6200000

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
    
    bounds_w, bounds_e, bounds_s, bounds_n = bounds
    polygon = Polygon([
        (bounds_w, bounds_s),
        (bounds_w, bounds_n),
        (bounds_e, bounds_n),
        (bounds_e, bounds_s)
    ])
    poly_gdf = geopandas.GeoDataFrame([1], geometry=[polygon], crs=dataframe.crs)

    df_out = geopandas.clip(dataframe, poly_gdf)

    # Filter out non-polygon rows
    df_out = df_out[df_out['geometry'].apply(lambda x: x.type == "Polygon")]

    return df_out
    
def main():

    # Parse arguments
    file_in_path = sys.argv[1]
    dir_out_path = sys.argv[2]
    
    bounds_w = int(sys.argv[3])
    bounds_e = int(sys.argv[4])
    bounds_s = int(sys.argv[5])
    bounds_n = int(sys.argv[6])
    
    print("Loading shapefile")
    df = geopandas.read_file(file_in_path)

    min_x, min_y, max_x, max_y = df['geometry'].total_bounds
    
    # Compute bounds
    bounds_w = math.ceil(bounds_w / TILE_SIZE)
    bounds_e = math.floor(bounds_e / TILE_SIZE)
    bounds_s = math.ceil(bounds_s / TILE_SIZE)
    bounds_n = math.floor(bounds_n / TILE_SIZE)

    # Compute offset
    if OFFSET_HALF:
        offset = PIXEL_SIZE/2
    else:
        offset = 0


    print("Converting to ETRS89 UTM 32N")
    df = df.to_crs(ETRS89_UTM32N)

    for y in range(bounds_s, bounds_n):
        for x in range(bounds_w, bounds_e):
            
            file_name = f"{x}_{y}"
            
            # Define bounds and clip
            bounds = (
                x*TILE_SIZE + offset,
                (x+1)*TILE_SIZE + offset,
                y*TILE_SIZE + offset,
                (y+1)*TILE_SIZE + offset
            )
            df_tile = clip(df, bounds)

            if len(df_tile) == 0:
                print(f"skipping {file_name}")
                continue

            # Save shp file
            file_path_shp = os.path.join(dir_out_path, file_name + ".shp")
            df_tile.to_file(file_path_shp)

            print(f"saved {file_name}")

main()