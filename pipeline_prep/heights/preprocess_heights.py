import rasterio
import os
import cv2 as cv
import numpy as np
import sys
from locality import utils, constants

GAUSSIAN_SIZE_BUILDINGS = 3
GAUSSIAN_SIZE_TREES = 7
N_PIXELS = int(constants.TILE_SIZE / constants.PIXEL_SIZE)

def blur(heights, heights_terrain, blur_size):

    # Blur
    negative = cv.GaussianBlur(heights, (blur_size, blur_size), 0) == constants.NULL_HEIGHT
    heights_blurred = np.maximum(heights, heights_terrain)
    heights_blurred = cv.GaussianBlur(heights_blurred, (blur_size, blur_size), 0)
    heights_blurred[negative] = constants.NULL_HEIGHT

    return heights_blurred

def morph(heights, heights_terrain):
    
    heights_out = heights.copy()

    # Open
    kernel = np.ones((3,3), np.float32) 
    mask = heights_out != constants.NULL_HEIGHT
    mask = cv.morphologyEx(mask.astype(np.uint8), cv.MORPH_OPEN, kernel)
    heights_out[mask == 0] = constants.NULL_HEIGHT
    heights_out[mask == 1] = heights[mask == 1]

    # Close
    kernel = np.ones((3,3), np.float32) 
    mask = heights_out != constants.NULL_HEIGHT
    mask = cv.morphologyEx(mask.astype(np.uint8), cv.MORPH_CLOSE, kernel)
    heights_out[mask == 0] = constants.NULL_HEIGHT
    heights_out[mask == 1] = heights[mask == 1]

    return heights_out

def preprocess_DEM(file_name, heights_dir_path):

    file_name += ".tif"

    # Get terrain
    terrain_file_path = os.path.join(heights_dir_path, "terrain", "1x1", file_name)
    dataset_terrain = rasterio.open(terrain_file_path)
    heights_terrain = dataset_terrain.read(1)
    
    # Get buildings
    buildings_file_path = os.path.join(heights_dir_path, "buildings", "raw", file_name)
    if os.path.exists(buildings_file_path):
        dataset_buildings = rasterio.open(buildings_file_path)
        heights_buildings = dataset_buildings.read(1)
    else:
        heights_buildings = np.full((N_PIXELS, N_PIXELS), constants.NULL_HEIGHT, dtype=np.float32)

    # Get trees
    trees_file_path = os.path.join(heights_dir_path, "trees", "raw", file_name)
    if os.path.exists(trees_file_path):
        dataset_trees = rasterio.open(trees_file_path)
        heights_trees = dataset_trees.read(1)
    else:
        heights_trees = np.full((N_PIXELS, N_PIXELS), constants.NULL_HEIGHT, dtype=np.float32)

    # Clean
    heights_buildings = blur(heights_buildings, heights_terrain, GAUSSIAN_SIZE_BUILDINGS)

    heights_trees = blur(heights_trees, heights_terrain, GAUSSIAN_SIZE_TREES)
    heights_trees = morph(heights_trees, heights_terrain)

    # Set pixels to max
    heights_trees[heights_buildings >= heights_trees] = constants.NULL_HEIGHT
    heights_buildings[heights_buildings < heights_trees] = constants.NULL_HEIGHT

    # Save buildings 1x1
    buildings_file_path_out = os.path.join(heights_dir_path, "buildings", "1x1", file_name)
    utils.save_raster(heights_buildings, buildings_file_path_out, dataset_terrain.transform)
    
    # Save trees 1x1
    trees_file_path_out = os.path.join(heights_dir_path, "trees", "1x1", file_name)
    utils.save_raster(heights_trees, trees_file_path_out, dataset_terrain.transform)

def main():

    n_args = len(sys.argv)
    if n_args != 3:
        print(f"Args: <file_name> <heights_dir_path>")

    file_name = sys.argv[1]
    heights_dir_path = sys.argv[2]

    preprocess_DEM(file_name, heights_dir_path)

if __name__ == "__main__":
    main()