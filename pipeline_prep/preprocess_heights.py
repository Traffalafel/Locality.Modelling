import rasterio
import os
import cv2 as cv
from remove_strings import remove_strings
from aggregate import aggregate
import numpy as np

import matplotlib.pyplot as plt

# Heights in
TERRAIN_DIR = r"C:\data\heights\terrain"
BUILDINGS_DIR = r"C:\data\heights\buildings"
TREES_DIR = r"C:\data\heights\trees"

# Args
GAUSSIAN_SIZE = 3

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

def blur(heights, heights_terrain, blur_size):

    # Blur
    negative = cv.GaussianBlur(heights, (blur_size, blur_size), 0) == -1
    heights_blurred = np.maximum(heights, heights_terrain)
    heights_blurred = cv.GaussianBlur(heights_blurred, (blur_size, blur_size), 0)
    heights_blurred[negative] = -1

    return heights_blurred

def morph(heights, heights_terrain):
    
    heights_out = heights.copy()

    # Open
    kernel = np.ones((3,3), np.float32) 
    mask = heights_out != -1
    mask = cv.morphologyEx(mask.astype(np.uint8), cv.MORPH_OPEN, kernel)
    heights_out[mask == 0] = -1
    heights_out[mask == 1] = heights[mask == 1]

    # Close
    kernel = np.ones((3,3), np.float32) 
    mask = heights_out != -1
    mask = cv.morphologyEx(mask.astype(np.uint8), cv.MORPH_CLOSE, kernel)
    heights_out[mask == 0] = -1
    heights_out[mask == 1] = heights[mask == 1]

    return heights_out

def preprocess_DEM(file_name, heights_dir):

    file_name += ".tif"

    # Get terrain
    terrain_file_path = os.path.join(heights_dir, "terrain", "raw", file_name)
    dataset_terrain = rasterio.open(terrain_file_path)
    heights_terrain = dataset_terrain.read(1)
    
    # Get buildings
    buildings_file_path = os.path.join(heights_dir, "buildings", "raw", file_name)
    dataset_buildings = rasterio.open(buildings_file_path)
    heights_buildings = dataset_buildings.read(1)

    # Get trees
    trees_file_path = os.path.join(heights_dir, "trees", "raw", file_name)
    dataset_trees = rasterio.open(trees_file_path)
    heights_trees = dataset_trees.read(1)

    # Clean
    heights_buildings = blur(heights_buildings, heights_terrain, GAUSSIAN_SIZE)

    heights_trees = blur(heights_trees, heights_terrain, GAUSSIAN_SIZE)
    heights_trees = morph(heights_trees, heights_terrain)

    # Set pixels to max
    heights_trees[heights_buildings >= heights_trees] = -1
    heights_buildings[heights_buildings < heights_trees] = -1

    # Save buildings 1x1
    buildings_file_path_out = os.path.join(heights_dir, "buildings", "1x1", file_name)
    save(heights_buildings, dataset_buildings.transform, buildings_file_path_out, dataset_buildings.crs)
    
    # Save trees 1x1
    trees_file_path_out = os.path.join(heights_dir, "trees", "1x1", file_name)
    save(heights_trees, dataset_trees.transform, trees_file_path_out, dataset_trees.crs)

def main():
    heights_dir = r"C:\data\heights"
    buildings_dir_raw = os.path.join(heights_dir, "buildings", "raw")
    files_in = get_dir_file_names(buildings_dir_raw)
    for file_name in files_in:
        print(f"{file_name}")
        preprocess_DEM(file_name, heights_dir)

main()