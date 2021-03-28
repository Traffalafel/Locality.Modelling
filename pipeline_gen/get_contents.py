import rasterio
import rasterio.merge
import rasterio.mask
from rasterio.io import MemoryFile
from shapely.geometry import Polygon
import os
import math
import numpy as np
import matplotlib.pyplot as plt

# Constants
TIF_FILE_KMS = 1000
ETRS89_UTM32_EPSG = 25832

def compute_bounds(point_sw, point_nw, point_se):

    point_ne = point_se + (point_nw - point_sw)
    
    bounds_w = point_sw[0] + 1
    bounds_e = point_ne[0] + 1
    bounds_s = point_se[1] + 1
    bounds_n = point_nw[1] + 1
    
    return (
        bounds_w,
        bounds_e,
        bounds_s,
        bounds_n
    )

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

def compute_shape(point_sw, point_nw, point_se, pixel_size):
    
    vec_sw_se = point_se - point_sw
    n_cols = int(np.linalg.norm(vec_sw_se) / pixel_size)

    vec_sw_nw = point_nw - point_sw
    n_rows = int(np.linalg.norm(vec_sw_nw) / pixel_size)

    return n_rows, n_cols

def take_rectangle(heights, point_sw, point_nw, point_se, pixel_size):

    n_rows, n_cols = compute_shape(point_sw, point_nw, point_se, pixel_size)

    xs = np.arange(n_cols)
    ys = np.arange(n_rows)
    xx, yy = np.meshgrid(xs, ys)
    xx = xx.reshape((n_rows, n_cols, -1))
    yy = yy.reshape((n_rows, n_cols, -1))
    idxs = np.append(xx, yy, axis=2)

    # Compute rotation matrix
    hyp = np.linalg.norm(vec_sw_se)
    cos_theta = vec_sw_se[0] / hyp
    sin_theta = -vec_sw_se[1] / hyp
    R = np.array([[cos_theta, -sin_theta], [sin_theta, cos_theta]])
    
    # Rotate and scale
    idxs = np.matmul(idxs, R)
    idxs[:,:] += (point_sw / pixel_size)
    
    idxs = np.round(idxs)
    idxs = idxs.astype(np.uint32)
    idxs = np.flip(idxs, axis=2)

    idxs = idxs.reshape((-1, 2))

    heights = heights[idxs[:,0], idxs[:,1]]
    heights = heights.reshape((n_rows, n_cols))

    return heights

def get_contents(heights_dir_path, point_sw, point_nw, point_se, pixel_size):
    
    bounds = compute_bounds(point_sw, point_nw, point_se)

    tif_paths = get_tif_paths(bounds, heights_dir_path)

    bound_w = math.floor(bounds[0] / TIF_FILE_KMS) * TIF_FILE_KMS
    bound_s = math.floor(bounds[2] / TIF_FILE_KMS) * TIF_FILE_KMS
    min_point = np.array([bound_w, bound_s])
    point_sw_local = point_sw - min_point
    point_nw_local = point_nw - min_point
    point_se_local = point_se - min_point

    datasets = []
    for tif_path in tif_paths:
        ds = rasterio.open(tif_path)
        datasets.append(ds)

    contents, transform  = rasterio.merge.merge(datasets)
    heights = contents[0,:,:]

    heights = np.flip(heights, axis=0)

    heights = take_rectangle(heights, point_sw_local, point_nw_local, point_se_local, pixel_size)

    return heights
