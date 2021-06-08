import numpy as np
import cv2 as cv
import os
import rasterio
import rasterio.transform
import sys
import pylas
from locality import utils, constants, interpolate

DIR_MASKS_BUILDINGS = r"D:\data\masks\buildings"
DIR_HEIGHTS = r"D:\data\heights"

CLASS_NOISE = 1
CLASS_GROUND = 2
CLASS_VEGETATION_HIGH = 5
CLASS_VEGETATION_MEDIUM = 5
CLASS_BUILDINGS = 6
CLASSES_TREES = [CLASS_VEGETATION_HIGH, CLASS_VEGETATION_MEDIUM]
MIN_N_OF_RETURNS_TREES = 3

def create_heights(las, step_size, dem_size, bounds=None):
    
    # Get parameters
    x_scale = las.header.x_scale
    x_offset = las.header.x_offset
    y_scale = las.header.y_scale
    y_offset = las.header.y_offset
    z_scale = las.header.z_scale
    z_offset = las.header.z_offset

    if bounds is not None:
        west, east, south, north = bounds
        x_min = west
        y_min = south
    else:
        x_min = las.header.x_min
        y_min = las.header.y_min

    # Compute coordinates
    points = np.array([[p[0], p[1], p[2]] for p in las.points])
    scale = np.array([x_scale, y_scale, z_scale])
    offset = np.array([x_offset, y_offset, z_offset])
    points = (points * scale) + offset
    mins = np.array([x_min, y_min])
    idxs_2d = points[:,:2]
    idxs_2d = ((idxs_2d - mins) // step_size)
    idxs_2d = idxs_2d.astype(np.int32)
    idxs_1d = idxs_2d[:,0] * dem_size + idxs_2d[:,1]
    z_heights = points[:,2]

    # Compute sums
    heights = np.zeros(dem_size**2, dtype=np.float32)
    np.maximum.at(heights, idxs_1d, z_heights)
    heights = heights.reshape((dem_size, dem_size))
    
    # averages = heights / counts
    heights[heights == 0] = constants.NULL_HEIGHT

    heights = np.transpose(heights)
    heights = np.flip(heights, axis=0)
    return heights

def erode(heights):
    
    n_rows, n_cols = heights.shape

    # Vertical
    vertical_n = heights[:n_rows-3, :] == constants.NULL_HEIGHT
    vertical_s = heights[3:, :] == constants.NULL_HEIGHT
    vertical = np.logical_and(vertical_n, vertical_s)
    row_false = np.full(n_cols, False)
    vertical_1 = np.insert(vertical, 0, row_false, axis=0)
    vertical_1 = np.append(vertical_1, row_false.reshape(1,-1), axis=0)
    vertical_1 = np.append(vertical_1, row_false.reshape(1,-1), axis=0)
    vertical_2 = np.insert(vertical, 0, row_false, axis=0)
    vertical_2 = np.insert(vertical_2, 0, row_false, axis=0)
    vertical_2 = np.append(vertical_2, row_false.reshape(1,-1), axis=0)
    vertical_idxs = np.logical_or(vertical_1, vertical_2)
    heights[vertical_idxs] = constants.NULL_HEIGHT
    
    # Horizontal
    horizontal_w = heights[:, :n_cols-3] == constants.NULL_HEIGHT
    horizontal_e = heights[:, 3:] == constants.NULL_HEIGHT
    horizontal = np.logical_and(horizontal_w, horizontal_e)
    col_false = np.full(n_rows, False)
    horizontal_1 = np.insert(horizontal, 0, col_false, axis=1)
    horizontal_1 = np.append(horizontal_1, col_false.reshape(-1,1), axis=1)
    horizontal_1 = np.append(horizontal_1, col_false.reshape(-1,1), axis=1)
    horizontal_2 = np.insert(horizontal, 0, col_false, axis=1)
    horizontal_2 = np.insert(horizontal_2, 0, col_false, axis=1)
    horizontal_2 = np.append(horizontal_2, col_false.reshape(-1,1), axis=1)
    horizontal_idxs = np.logical_or(horizontal_1, horizontal_2)
    heights[horizontal_idxs] = constants.NULL_HEIGHT

def generate_buildings(file_path):
    
    dem_size = int(constants.TILE_SIZE / constants.PIXEL_SIZE)
    file_name = utils.get_file_name(file_path)
    file_name_tif = file_name + ".tif"
    bounds = utils.get_file_bounds(file_name)

    # Get buildings mask
    file_mask_buildings_path = os.path.join(DIR_MASKS_BUILDINGS, "1x1", file_name_tif)
    if os.path.exists(file_mask_buildings_path):
        dataset_mask_buildings = rasterio.open(file_mask_buildings_path)
        mask_buildings = dataset_mask_buildings.read(1)
        mask_buildings = mask_buildings.astype(np.uint8)
    else:
        print(f"Could not find buildings mask file {file_mask_buildings_path}")
        mask_buildings = np.zeros((dem_size, dem_size), dtype=np.uint8)

    # Dilate buildings mask
    kernel = np.ones((5,5))
    mask_buildings = cv.dilate(mask_buildings, kernel, iterations=1)
    mask_buildings = mask_buildings == 1

    # Get surface heights
    file_heights_surface_path = os.path.join(DIR_HEIGHTS, "surface", "1x1", file_name_tif)
    if os.path.exists(file_heights_surface_path):
        dataset_heights_surface = rasterio.open(file_heights_surface_path)
        heights_surface = dataset_heights_surface.read(1)
    else:
        print(f"Could not find surface heights file {file_heights_surface_path}")
        heights_surface = np.full((dem_size, dem_size), constants.NULL_HEIGHT, dtype=np.float32)

    # Set surface heights that are not buildings to null
    heights_surface[mask_buildings == False] = constants.NULL_HEIGHT

    # Get buildings heights
    las_buildings = pylas.read(file_path)
    las_buildings.points = las_buildings.points[las_buildings.classification == CLASS_BUILDINGS]
    
    if las_buildings.points.size == 0:
        return np.full((dem_size, dem_size), constants.NULL_HEIGHT, dtype=np.float32)
    
    heights_buildings = create_heights(las_buildings, constants.PIXEL_SIZE, dem_size, bounds)

    # Set buildings that have been falsely classified as vegetation
    falsely_classified = np.full((dem_size, dem_size), constants.NULL_HEIGHT, np.float32)
    las_trees = pylas.read(file_path)
    las_trees.points = las_trees.points[np.isin(las_trees.classification, CLASSES_TREES)]
    las_trees.points = las_trees.points[las_trees['number_of_returns'] < MIN_N_OF_RETURNS_TREES]
    heights_trees = create_heights(las_trees, constants.PIXEL_SIZE, dem_size, bounds)
    falsely_classified[mask_buildings] = heights_trees[mask_buildings]
    falsely_classified[heights_buildings != constants.NULL_HEIGHT] = constants.NULL_HEIGHT
    heights_buildings = np.maximum(heights_buildings, falsely_classified)
    
    # Interpolate buildings
    mask_interpolation_trees = mask_buildings == False
    interpolate.interpolate(heights_buildings, mask_interpolation_trees, limit_v=8, limit_h=10)
    interpolate.interpolate(heights_buildings, mask_interpolation_trees, limit_v=8, limit_h=10)

    heights_buildings = np.maximum(heights_buildings, heights_surface)

    return heights_buildings

def generate_trees(file_path):

    dem_size = int(constants.TILE_SIZE / constants.PIXEL_SIZE)

    file_name = utils.get_file_name(file_path)
    bounds = utils.get_file_bounds(file_name)

    # Get terrain heights
    las_terrain = pylas.read(file_path)
    las_terrain.points = las_terrain.points[las_terrain.classification == CLASS_GROUND]
    las_terrain.points = las_terrain.points[las_terrain['number_of_returns'] == 1]
    if las_terrain.points.size != 0:
        heights_terrain = create_heights(las_terrain, constants.PIXEL_SIZE, dem_size, bounds)
    else:
        heights_terrain = np.full((dem_size, dem_size), constants.NULL_HEIGHT, dtype=np.float32)
    erode(heights_terrain)

    # Get trees heights
    las_trees = pylas.read(file_path)
    las_trees.points = las_trees.points[np.isin(las_trees.classification, CLASSES_TREES)]
    las_trees.points = las_trees.points[las_trees['number_of_returns'] >= MIN_N_OF_RETURNS_TREES]

    if las_trees.points.size == 0:
        return np.full((dem_size, dem_size), constants.NULL_HEIGHT, dtype=np.float32)

    heights_trees = create_heights(las_trees, constants.PIXEL_SIZE, dem_size, bounds)
    
    # Interpolate trees
    mask_interpolation_trees = heights_terrain != constants.NULL_HEIGHT
    mask_interpolation_trees = mask_interpolation_trees.astype(np.uint8)
    kernel = np.ones((5,5))
    mask_interpolation_trees = cv.erode(mask_interpolation_trees, kernel, iterations=1)
    mask_interpolation_trees = mask_interpolation_trees == 1
    interpolate(heights_trees, mask_interpolation_trees, limit_v=None, limit_h=6)
    erode(heights_trees)

    return heights_trees

def generate_DEM(file_path, dir_out):
    
    heights_buildings = generate_buildings(file_path)
    heights_trees = generate_trees(file_path)
    
    # Create bounds
    file_name = utils.get_file_name(file_path)
    dem_size = int(constants.TILE_SIZE / constants.PIXEL_SIZE)
    bounds = utils.get_file_bounds(file_name)
    transform = rasterio.transform.from_bounds(
        west=bounds[0],
        east=bounds[1],
        south=bounds[2],
        north=bounds[3],
        width=dem_size,
        height=dem_size,
    )

    # Save buildings
    file_path_buildings = os.path.join(dir_out, "buildings", "raw", f"{file_name}.tif")
    utils.save_raster(heights_buildings, file_path_buildings, transform)
    
    # Save trees
    file_path_trees = os.path.join(dir_out, "trees", "raw", f"{file_name}.tif")
    utils.save_raster(heights_trees, file_path_trees, transform)

    print(file_path_trees)

def main():

    n_args = len(sys.argv)
    if n_args != 3:
        print(f"Args: <file_in_path> <dir_out_path>")
    
    file_in_path = sys.argv[1]
    dir_out_path = sys.argv[2]

    generate_DEM(file_in_path, dir_out_path)

if __name__ == "__main__":
    main()