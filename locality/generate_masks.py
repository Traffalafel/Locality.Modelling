import geopandas
import os
import numpy as np
import rasterio
from shapely.geometry import Polygon
from rasterio.crs import CRS
from locality import utils, constants

def generate_masks(dir_in, dir_out, f_transform=None, offset_half=True, all_touched=False):
    
    if not os.path.exists(dir_out):
        os.mkdir(dir_out)
    
    if offset_half:
        offset = constants.PIXEL_SIZE/2
    else:
        offset = 0

    file_paths_in = utils.get_directory_file_paths(dir_in)
    for file_path_in in file_paths_in:

        if utils.get_file_extension(file_path_in) != "shp":
            continue

        df = geopandas.read_file(file_path_in)
        file_name = utils.get_file_name(file_path_in)
        bounds = utils.get_file_bounds(file_name)
        bounds = tuple(b + offset for b in bounds)
        df = utils.clip(df, bounds)

        if f_transform is not None:
            df = f_transform(df)

        if len(df) == 0:
                print(f"Skipping {file_name}")
                continue

        file_name_tif = f"{file_name}.tif"

        # Rasterize and save 1x1 
        file_path_1x1 = os.path.join(dir_out, "1x1", file_name_tif)
        pixels_1x1, transform_1x1 = utils.rasterize(df, constants.N_PIXELS_1x1, bounds, all_touched)
        utils.save_raster(pixels_1x1, file_path_1x1, transform_1x1)

        # Rasterize and save 2x2 
        file_path_2x2 = os.path.join(dir_out, "2x2", file_name_tif)
        pixels_2x2, transform_2x2 = utils.rasterize(df, constants.N_PIXELS_2x2, bounds, all_touched)
        utils.save_raster(pixels_2x2, file_path_2x2, transform_2x2)

        print(f"Saved {file_name}")