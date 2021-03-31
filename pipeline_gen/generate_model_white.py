import numpy as np
import sys
import rasterio
from pyproj import Transformer
import os
import pymeshlab
from get_contents import get_contents, compute_shape
from meshify import meshify_elevation, meshify_terrain, meshify_surface

# ARGS
HEIGHTS_TIFS_DIR_PATH = r"D:\PrintCitiesData\DHM_overflade_blurred_3"
ROADS_TIF_DIR_PATH = r"D:\PrintCitiesData\roads_tif"
BUILDINGS_TIF_DIR_PATH = r"D:\PrintCitiesData\buildings_tif"

# Constants
ORIGINAL_PIXEL_SIZE = 0.4
CRS_WGS84 = 4326
CRS_ETRS89 = 25832
NULL_HEIGHT = -1
HEIGHTS_EXTRA = 20
HEIGHTS_MULTIPLIER = 1.1

def get_heights(path, point_sw, point_nw, point_se, pixel_size):
    n_rows, n_cols = compute_shape(point_sw, point_nw, point_se, pixel_size)
    if os.path.exists(path):
        return get_contents(path, point_sw, point_nw, point_se, pixel_size)
    else:
        print(f"Could not find any file for {path}. Using NULL_HEIGHT={NULL_HEIGHT} instead...")
        return np.full((n_rows, n_cols), NULL_HEIGHT, dtype=np.float32)

def generate_model_white(data_dir_path, dir_out, point_sw, point_nw, point_se, tiles_x, tiles_y, aggreg_size):

    pixel_size = ORIGINAL_PIXEL_SIZE * aggreg_size
    aggreg_string = f"{aggreg_size}x{aggreg_size}"

    # Get heights
    heights_dir_path = os.path.join(data_dir_path, "heights", "surface", aggreg_string)
    heights = get_heights(heights_dir_path, point_sw, point_nw, point_se, pixel_size)

    heights *= HEIGHTS_MULTIPLIER
    heights += HEIGHTS_EXTRA

    n_rows, n_cols = compute_shape(point_sw, point_nw, point_se, pixel_size)
    n_rows_tile = n_rows // tiles_y
    n_cols_tile = n_cols // tiles_x

    for tile_x in range(tiles_x):
        for tile_y in range(tiles_y):

            tile_name = f"{tile_x+1}_{tile_y+1}"
            print(tile_name)

            min_x = tile_x * n_cols_tile
            max_x = (tile_x+1) * n_cols_tile + 1
            min_y = tile_y * n_rows_tile
            max_y = (tile_y+1) * n_rows_tile + 1

            offset_x = min_x 
            offset_y = min_y

            heights_tile = heights[min_y:max_y, min_x:max_x]

            ms = meshify_surface(heights_tile, offset_x, offset_y, pixel_size)

            # Save mesh
            file_out = f"{tile_name}.ply"
            file_out_path = os.path.join(dir_out, file_out)
            ms.save_current_mesh(file_out_path)

def main():

    data_dir = r"D:\data"
    dir_out = r"C:\Users\traff\source\repos\Locality.Modelling\data\models"
    aggreg_size = 2

    sw_lat = float(sys.argv[1])
    sw_lng = float(sys.argv[2])
    ne_lat = float(sys.argv[3])
    ne_lng = float(sys.argv[4])
    tiles_x = int(sys.argv[5])
    tiles_y = int(sys.argv[6])

    # Convert coordinates
    transformer = Transformer.from_crs(CRS_WGS84, CRS_ETRS89)
    
    sw_x, sw_y = transformer.transform(sw_lat, sw_lng)
    point_sw = np.array([sw_x, sw_y])
    point_sw = point_sw.astype(np.uint32)

    ne_x, ne_y = transformer.transform(ne_lat, ne_lng)
    point_ne = np.array([ne_x, ne_y])
    point_ne = point_ne.astype(np.uint32)

    point_nw = np.array([sw_x, ne_y])
    point_se = np.array([ne_x, sw_y])

    generate_model_white(data_dir, dir_out, point_sw, point_nw, point_se, tiles_x, tiles_y, aggreg_size)

main()
