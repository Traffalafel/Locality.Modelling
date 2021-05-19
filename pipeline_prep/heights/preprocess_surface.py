import rasterio
import os
import cv2 as cv
import numpy as np

import matplotlib.pyplot as plt

# Heights in
SURFACE_DIR_PATH = r"D:\data\heights\surface"

# Args
NULL_HEIGHT = -1
GAUSSIAN_SIZE = 3
ORIGINAL_PIXEL_SIZE = 0.4
TILE_SIZE_M = 1000
N_PIXELS = int(TILE_SIZE_M / ORIGINAL_PIXEL_SIZE)

def get_dir_file_names(dir_path):
    contents = os.listdir(dir_path)
    files = [c for c in contents if os.path.isfile(os.path.join(dir_path, c))]
    file_names = [f.split(".")[0] for f in files]
    return file_names

def save(heights, transform, file_path, crs):
    dataset_out = rasterio.open(
        file_path,
        mode='w',
        driver='GTiff',
        width=heights.shape[0],
        height=heights.shape[1],
        count=1,
        dtype=heights.dtype,
        crs=crs,
        transform=transform
    )
    dataset_out.write(heights, 1)

def preprocess_DEM(file_name, heights_dir):

    file_name += ".tif"
    surface_file_path_out = os.path.join(heights_dir, "surface", "1x1", file_name)
    if os.path.exists(surface_file_path_out):
        print(f"Output {file_name} already exists, skipping")
        return
        
    # Get surface
    surface_file_path = os.path.join(heights_dir, "surface", "raw", file_name)
    dataset_surface = rasterio.open(surface_file_path)
    heights_surface = dataset_surface.read(1)
    
    # Apply Gaussian blur
    heights_surface = cv.GaussianBlur(heights_surface, (GAUSSIAN_SIZE, GAUSSIAN_SIZE), 0)

    # Save surface 1x1
    save(heights_surface, dataset_surface.transform, surface_file_path_out, dataset_surface.crs)

    print(f"{file_name} preprocessed")

def main():
    heights_dir = r"D:\data\heights"
    surface_dir_raw = os.path.join(heights_dir, "surface", "raw")
    files_in = get_dir_file_names(surface_dir_raw)
    for file_name in files_in:
        preprocess_DEM(file_name, heights_dir)

main()