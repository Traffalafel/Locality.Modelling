import numpy as np
import geopandas
import rasterio
import rasterio.features
import rasterio.transform
import sys
from os import listdir, mkdir
from os.path import join, isfile, exists

# Arguments
AGGREG_SIZE = 4
OFFSET_HALF = True
ALL_TOUCHED = True

# Constants
ORIGINAL_PIXEL_SIZE = 0.4
ORIGINAL_N_PIXELS = 2500

# Derived constants
PIXEL_SIZE = ORIGINAL_PIXEL_SIZE * AGGREG_SIZE
HEIGHT = int(ORIGINAL_N_PIXELS / AGGREG_SIZE)
WIDTH = int(ORIGINAL_N_PIXELS / AGGREG_SIZE)
TILE_SIZE = ORIGINAL_N_PIXELS * ORIGINAL_PIXEL_SIZE

def rasterize(dataframe, bounds, height, width, all_touched=False):

    x_min, x_max, y_min, y_max = bounds
    transform = rasterio.transform.from_bounds(
        west = x_min,
        south = y_min,
        east = x_max,
        north = y_max,
        height = height,
        width = width
    )

    geometries = dataframe['geometry']
    
    pixels = rasterio.features.rasterize(
        shapes=geometries,
        out_shape=(height, width),
        fill=0,
        transform=transform,
        all_touched=all_touched,
        default_value=1,
        dtype=np.float32
    )

    return pixels, transform

def get_dir_files(dir_path):
    contents = listdir(dir_path)
    files = [c for c in contents if isfile(join(dir_path, c))]
    files_shp = [f for f in files if f.split('.')[1] == "shp"]
    return files_shp

def get_file_bounds(file_name, offset):
    file_name = file_name.split('.')[0]
    min_x = float(file_name.split('_')[0]) * TILE_SIZE + offset
    min_y = float(file_name.split('_')[1]) * TILE_SIZE + offset
    max_x = min_x + TILE_SIZE
    max_y = min_y + TILE_SIZE
    return (min_x, max_x, min_y, max_y)

def main():

    if len(sys.argv) != 3:
        print("Arguments: <dir_in_path> <dir_out_path>")

    # Parse arguments
    dir_in_path = sys.argv[1]
    dir_out_path = sys.argv[2]
    
    if not exists(dir_out_path):
        mkdir(dir_out_path)

    if OFFSET_HALF:
        offset = PIXEL_SIZE / 2
    else:
        offset = 0

    files_in = get_dir_files(dir_in_path)
    for file_name in files_in:


        # Read file
        file_path = join(dir_in_path, file_name)
        df = geopandas.read_file(file_path)
        
        # Rasterize
        bounds = get_file_bounds(file_name, offset)
        pixels, transform = rasterize(df, bounds, HEIGHT, WIDTH, ALL_TOUCHED)

        # Save file
        file_out_name = file_name.split('.')[0] + ".tif"
        file_out_path = join(dir_out_path, file_out_name)
        dataset_out = rasterio.open(
            file_out_path,
            mode='w',
            driver='GTiff',
            height=HEIGHT,
            width=WIDTH,
            count=1,
            crs=df.crs,
            transform=transform,
            dtype=np.float32
        )
        dataset_out.write(pixels, 1)

        print(f"Saved {file_out_path}")

main()