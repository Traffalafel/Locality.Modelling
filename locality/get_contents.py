import rasterio
import rasterio.merge
import rasterio.mask
import rasterio.transform
import rasterio.coords
from rasterio.io import MemoryFile
from rasterio.crs import CRS
from shapely.geometry import Polygon
import os
import math
import numpy as np
import matplotlib.pyplot as plt

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
    n_cols = int(width / pixel_size)
    n_rows = int(height / pixel_size)
    return n_rows, n_cols

def get_contents(heights_dir_path, point_sw, width, height, pixel_size):
    
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
                raise Exception()

    contents, transform  = rasterio.merge.merge(datasets)
    heights = contents[0,:,:]
    heights = np.flip(heights, axis=0)

    idx_w = int((bound_w - (min_file_x * TIF_FILE_KMS)) // pixel_size)
    idx_e = int((bound_e - (min_file_x * TIF_FILE_KMS)) // pixel_size)
    idx_s = int((bound_s - (min_file_y * TIF_FILE_KMS)) // pixel_size)
    idx_n = int((bound_n - (min_file_y * TIF_FILE_KMS)) // pixel_size)

    return heights[idx_w:idx_e, idx_s:idx_n]
