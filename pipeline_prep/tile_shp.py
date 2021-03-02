import numpy as np
import geopandas
import rasterio
import os
import sys
import math
from clip import clip

# Args
TILE_SIZE = 1000
OFFSET_HALF = False
BOUNDS_W = 723000
BOUNDS_E = 728000
BOUNDS_S = 6175000
BOUNDS_N = 6180000

# Constants
ETRS89_UTM32N = 3044
CLIP_MARGIN = 2 # add 2 metres to clipping bounds

def main():

    # Parse arguments
    file_in_path = sys.argv[1]
    dir_out_path = sys.argv[2]
    
    bounds_w = BOUNDS_W
    bounds_e = BOUNDS_E
    bounds_s = BOUNDS_S
    bounds_n = BOUNDS_N
    
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
                x*TILE_SIZE + offset - CLIP_MARGIN,
                (x+1)*TILE_SIZE + offset + CLIP_MARGIN,
                y*TILE_SIZE + offset - CLIP_MARGIN,
                (y+1)*TILE_SIZE + offset + CLIP_MARGIN
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