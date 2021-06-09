import rasterio
import rasterio.merge
import rasterio.mask
import rasterio.transform
import rasterio.coords
from rasterio.io import MemoryFile
from rasterio.crs import CRS
import os
import math
import numpy as np
from locality import utils, constants

# Constants
TIF_FILE_KMS = 1000
ORIGINAL_PIXEL_SIZE = 0.4
ETRS89_UTM32N = 25832
N_PIXELS = int(TIF_FILE_KMS / ORIGINAL_PIXEL_SIZE)

def get_tif_paths(bounds, tifs_dir_path):
    
    bounds_w, bounds_e, bounds_s, bounds_n = bounds

    min_file_x = math.floor(bounds_w / TIF_FILE_KMS)
    min_file_y = math.floor(bounds_s / TIF_FILE_KMS)
    max_file_x = math.floor(bounds_e / TIF_FILE_KMS)
    max_file_y = math.floor(bounds_n / TIF_FILE_KMS)

    file_paths = []
    for file_x in range(min_file_x, max_file_x+1):
        for file_y in range(min_file_y, max_file_y+1):
            file_name = f"{file_x}_{file_y}.tif"
            file_path = os.path.join(tifs_dir_path, file_name)
            file_paths.append(file_path)

    return file_paths

def compute_shape(width, height, pixel_size):
    n_cols = math.ceil(width / pixel_size)
    n_rows = math.ceil(height / pixel_size)
    return n_rows, n_cols

def get_contents(heights_dir_path, point_sw, width, height, pixel_size, null_val=constants.NULL_HEIGHT):
    
    bound_w = point_sw[0]
    bound_s = point_sw[1]
    bound_e = bound_w + width
    bound_n = bound_s + height

    min_file_x = math.floor(bound_w / TIF_FILE_KMS)
    min_file_y = math.floor(bound_s / TIF_FILE_KMS)
    max_file_x = math.floor(bound_e / TIF_FILE_KMS)
    max_file_y = math.floor(bound_n / TIF_FILE_KMS)

    datasets = []
    for file_x in range(min_file_x, max_file_x+1):
        for file_y in range(min_file_y, max_file_y+1):
            file_name = f"{file_x}_{file_y}.tif"
            file_path = os.path.join(heights_dir_path, file_name)
            if os.path.exists(file_path):
                ds = rasterio.open(file_path)
                datasets.append(ds)
            else:
                print(f"File doesn't exist: {file_path}")
                width_pixels = int(TIF_FILE_KMS / pixel_size)
                height_pixels = int(TIF_FILE_KMS / pixel_size)
                transform = rasterio.transform.from_bounds(
                    west = file_x * TIF_FILE_KMS,
                    south = file_y* TIF_FILE_KMS,
                    east = (file_x+1) * TIF_FILE_KMS,
                    north = (file_y+1) * TIF_FILE_KMS,
                    width = width_pixels,
                    height = height_pixels
                )
                crs = CRS.from_epsg(ETRS89_UTM32N)
                memfile = MemoryFile()
                ds = memfile.open(
                    driver="GTiff",
                    width=width_pixels,
                    height=height_pixels,
                    count=1,
                    crs=crs,
                    transform=transform,
                    dtype=np.float32
                )
                array = np.full((height_pixels, width_pixels), null_val, dtype=np.float32)
                ds.write(array, 1)
                datasets.append(ds)

    contents, transform  = rasterio.merge.merge(datasets)
    heights = contents[0,:,:]
    heights = np.flip(heights, axis=0)
    heights = np.transpose(heights, (0, 1))

    idx_w = int((bound_w - (min_file_x * TIF_FILE_KMS)) // pixel_size)
    idx_e = int((bound_e - (min_file_x * TIF_FILE_KMS)) // pixel_size)
    idx_s = int((bound_s - (min_file_y * TIF_FILE_KMS)) // pixel_size)
    idx_n = int((bound_n - (min_file_y * TIF_FILE_KMS)) // pixel_size)

    heights_output = heights[idx_s:idx_n, idx_w:idx_e]

    return heights_output