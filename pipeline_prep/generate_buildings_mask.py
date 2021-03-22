import numpy as np
import geopandas
import rasterio
import rasterio.features
import os
from polygonize import polygonize
from clip import clip

# Args
FILE_IN_PATH = r"C:\data\GeoDanmark\buildings_cph.shp"
SHP_DIR_OUT_PATH = r"C:\data\shapes\buildings"
TIF_DIR_OUT_PATH = r"C:\data\masks\buildings"

ALL_TOUCHED = False
OFFSET_HALF = False

BOUNDS_W = 723
BOUNDS_E = 728
BOUNDS_S = 6175
BOUNDS_N = 6180

# Constants
TILE_SIZE = 1000
PIXEL_SIZE = 0.4 
N_PIXELS = int(TILE_SIZE / PIXEL_SIZE)

ETRS89_UTM32N = 25832

def main():

    if not os.path.exists(SHP_DIR_OUT_PATH):
        os.mkdir(SHP_DIR_OUT_PATH)
    if not os.path.exists(TIF_DIR_OUT_PATH):
        os.mkdir(TIF_DIR_OUT_PATH)

    df = geopandas.read_file(FILE_IN_PATH)
    df = df.to_crs(ETRS89_UTM32N)

    # Compute offset
    if OFFSET_HALF:
        offset = PIXEL_SIZE/2
    else:
        offset = 0

    for y in range(BOUNDS_S, BOUNDS_N):
        for x in range(BOUNDS_W, BOUNDS_E):
            
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

            # Rasterize
            transform = rasterio.transform.from_bounds(
                west = x * TILE_SIZE + offset,
                east = (x+1) * TILE_SIZE + offset,
                south = y * TILE_SIZE + offset,
                north = (y+1) * TILE_SIZE + offset,
                height = N_PIXELS,
                width = N_PIXELS
            )
            pixels = rasterio.features.rasterize(
                shapes=df_tile['geometry'],
                out_shape=(N_PIXELS, N_PIXELS),
                fill=0,
                transform=transform,
                all_touched=ALL_TOUCHED,
                default_value=1,
                dtype=np.uint8
            )

            # Save shp file
            file_name_shp = f"{file_name}.shp"
            file_path_shp = os.path.join(SHP_DIR_OUT_PATH, file_name_shp)
            df_tile.to_file(file_path_shp)

            # Save tif file
            file_name_tif = f"{file_name}.tif"
            file_path_tif = os.path.join(TIF_DIR_OUT_PATH, file_name_tif)
            dataset_out = rasterio.open(
                file_path_tif,
                mode='w',
                driver='GTiff',
                height=N_PIXELS,
                width=N_PIXELS,
                count=1,
                crs=df_tile.crs,
                transform=transform,
                dtype=np.uint8
            )
            dataset_out.write(pixels, 1)

            print(f"saved {file_name}")

main()