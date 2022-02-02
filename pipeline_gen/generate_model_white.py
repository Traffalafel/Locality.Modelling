import numpy as np
import sys
import rasterio
from pyproj import Transformer
import os
import pymeshlab
from locality import constants
from locality import get_contents
from meshify import meshify_white
from pipeline_gen.generate_model_color import NULL_HEIGHT

# ARGS
HEIGHTS_TIFS_DIR_PATH = r"D:\PrintCitiesData\DHM_overflade_blurred_3"
ROADS_TIF_DIR_PATH = r"D:\PrintCitiesData\roads_tif"
BUILDINGS_TIF_DIR_PATH = r"D:\PrintCitiesData\buildings_tif"

# Constants
DEFAULT_OUTPUT_FORMAT = "stl"
ORIGINAL_PIXEL_SIZE = 0.4
NULL_HEIGHT = -1
CRS_WGS84 = 4326
CRS_ETRS89 = 25832
HEIGHT_OFFSET = 8
HEIGHTS_MULTIPLIER = 1

def get_heights(path, point_sw, width, height, pixel_size):
    n_rows, n_cols = get_contents.compute_shape(width, height, pixel_size)
    if os.path.exists(path):
        return get_contents.get_contents(path, point_sw, width, height, pixel_size)
    else:
        print(f"Could not find path {path}")
        return np.full((n_rows, n_cols), NULL_HEIGHT, dtype=np.float32)

def generate_model_white(data_dir_path, dir_out, point_sw, width, height, tiles_x, tiles_y, aggreg_size, model_name, output_format):

    pixel_size = ORIGINAL_PIXEL_SIZE * aggreg_size
    aggreg_string = f"{aggreg_size}x{aggreg_size}"

    # Add an extra pixel in each direction
    width = width + pixel_size
    height = height + pixel_size

    # Get heights
    heights_dir_path = os.path.join(data_dir_path, "heights", "surface", aggreg_string)
    heights = get_heights(heights_dir_path, point_sw, width, height, pixel_size)

    height_min = np.min(heights)
    heights -= height_min
    heights *= HEIGHTS_MULTIPLIER
    heights += HEIGHT_OFFSET

    n_rows, n_cols = get_contents.compute_shape(width, height, pixel_size)
    n_rows_tile = n_rows // tiles_y
    n_cols_tile = n_cols // tiles_x

    for tile_x in range(tiles_x):
        for tile_y in range(tiles_y):

            tile_name = f"{tile_x+1}_{tile_y+1}"
            print(f"{tile_name}")

            min_x = tile_x * n_cols_tile
            max_x = (tile_x+1) * n_cols_tile + 1
            min_y = tile_y * n_rows_tile
            max_y = (tile_y+1) * n_rows_tile + 1

            offset_x = min_x 
            offset_y = min_y

            heights_tile = heights[min_y:max_y, min_x:max_x]

            ms = meshify_white(heights_tile, offset_x, offset_y, pixel_size)

            # Save mesh
            file_out = f"{model_name} {tile_name}.{output_format}"
            file_out_path = os.path.join(dir_out, file_out)
            ms.save_current_mesh(file_out_path)

def main():

    data_dir = r"D:\data"
    dir_out = r"C:\Users\traff\source\repos\Locality.Modelling\data\models"

    if len(sys.argv) < 10:
        print("Usage: <sw_lat> <sw_lng> <width> <height> <tiles_x> <tiles_y> <aggreg_size> <model_name> <output_format>")
        return
    
    sw_lat = float(sys.argv[1])
    sw_lng = float(sys.argv[2])
    width = int(sys.argv[3])
    height = int(sys.argv[4])
    tiles_x = int(sys.argv[5])
    tiles_y = int(sys.argv[6])
    aggreg_size = int(sys.argv[7])
    model_name = sys.argv[8]

    if len(sys.argv) == 10:
        output_format = sys.argv[9]
    else:
        output_format = DEFAULT_OUTPUT_FORMAT

    # Convert coordinates
    transformer = Transformer.from_crs(CRS_WGS84, CRS_ETRS89)
    w, s = transformer.transform(sw_lat, sw_lng)
    point_sw = np.array([w, s], dtype=np.int32)

    model_dir_out = os.path.join(dir_out, f"{model_name}_{output_format}")
    if not os.path.exists(model_dir_out):
        os.mkdir(model_dir_out)

    generate_model_white(data_dir, dir_out, point_sw, width, height, tiles_x, tiles_y, aggreg_size, model_name, output_format)

main()
