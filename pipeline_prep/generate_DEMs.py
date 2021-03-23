import numpy as np
import cv2 as cv
import math
import os
import rasterio
from rasterio.crs import CRS
import rasterio.transform
import sys
import pylas
from interpolate import interpolate

import matplotlib.pyplot as plt

DIR_LIDAR = r"C:\data\lidar"
DIR_MASKS_BUILDINGS = r"C:\data\masks\buildings"

CLASS_NOISE = 1
CLASS_GROUND = 2
CLASS_VEGETATION_HIGH = 5
CLASS_VEGETATION_MEDIUM = 5
CLASS_BUILDINGS = 6
CLASSES_TREES = [CLASS_VEGETATION_HIGH, CLASS_VEGETATION_MEDIUM]
ETRS89_UTM32N = 25832

MIN_N_OF_RETURNS_TREES = 3
TILE_SIZE = 1000
PIXEL_SIZE = 0.4

def get_dir_file_names(dir_path):
    contents = os.listdir(dir_path)
    files = [c for c in contents if os.path.isfile(os.path.join(dir_path, c))]
    file_names = [f.split(".")[0] for f in files]
    return file_names

def get_file_bounds(file_name):
    file_name = file_name.split('.')[0]
    min_x = int(file_name.split('_')[0]) * TILE_SIZE
    max_x = min_x + TILE_SIZE
    min_y = int(file_name.split('_')[1]) * TILE_SIZE
    max_y = min_y + TILE_SIZE
    return (min_x, max_x, min_y, max_y)

def save_raster(values, file_path, transform):
    dataset = rasterio.open(
        file_path,
        mode="w",
        driver="GTiff",
        width=values.shape[1],
        height=values.shape[0],
        count=1,
        crs=CRS.from_epsg(ETRS89_UTM32N),
        transform=transform,
        dtype=values.dtype
    )
    dataset.write(values, 1)

def create_heights(las, step_size, dem_size):
    
    # Get parameters
    x_scale = las.header.x_scale
    x_offset = las.header.x_offset
    x_min = las.header.x_min
    y_scale = las.header.y_scale
    y_offset = las.header.y_offset
    y_min = las.header.y_min
    z_scale = las.header.z_scale
    z_offset = las.header.z_offset
    
    # Compute coordinates
    points = np.array([[p[0], p[1], p[2]] for p in las.points])
    scale = np.array([x_scale, y_scale, z_scale])
    offset = np.array([x_offset, y_offset, z_offset])
    points = (points * scale) + offset
    mins = np.array([x_min, y_min])
    idxs_2d = points[:,:2]
    idxs_2d = ((idxs_2d - mins) // step_size).astype(np.int32)
    idxs_1d = idxs_2d[:,0] * dem_size + idxs_2d[:,1]
    z_heights = points[:,2]

    # Compute sums
    heights = np.zeros(dem_size**2, dtype=np.float32)
    np.maximum.at(heights, idxs_1d, z_heights)
    heights = heights.reshape((dem_size, dem_size))
    
    # averages = heights / counts
    heights[heights == 0] = -1

    heights = np.transpose(heights)
    heights = np.flip(heights, axis=0)

    return heights

def erode(heights):
    
    null_val = -1
    n_rows, n_cols = heights.shape

    # Vertical
    vertical_n = heights[:n_rows-3, :] == null_val
    vertical_s = heights[3:, :] == null_val
    vertical = np.logical_and(vertical_n, vertical_s)
    row_false = np.full(n_cols, False)
    vertical_1 = np.insert(vertical, 0, row_false, axis=0)
    vertical_1 = np.append(vertical_1, row_false.reshape(1,-1), axis=0)
    vertical_1 = np.append(vertical_1, row_false.reshape(1,-1), axis=0)
    vertical_2 = np.insert(vertical, 0, row_false, axis=0)
    vertical_2 = np.insert(vertical_2, 0, row_false, axis=0)
    vertical_2 = np.append(vertical_2, row_false.reshape(1,-1), axis=0)
    vertical_idxs = np.logical_or(vertical_1, vertical_2)
    heights[vertical_idxs] = -1
    
    # Horizontal
    horizontal_w = heights[:, :n_cols-3] == null_val
    horizontal_e = heights[:, 3:] == null_val
    horizontal = np.logical_and(horizontal_w, horizontal_e)
    col_false = np.full(n_rows, False)
    horizontal_1 = np.insert(horizontal, 0, col_false, axis=1)
    horizontal_1 = np.append(horizontal_1, col_false.reshape(-1,1), axis=1)
    horizontal_1 = np.append(horizontal_1, col_false.reshape(-1,1), axis=1)
    horizontal_2 = np.insert(horizontal, 0, col_false, axis=1)
    horizontal_2 = np.insert(horizontal_2, 0, col_false, axis=1)
    horizontal_2 = np.append(horizontal_2, col_false.reshape(-1,1), axis=1)
    horizontal_idxs = np.logical_or(horizontal_1, horizontal_2)
    heights[horizontal_idxs] = -1

def generate_DEM(file_name, dir_out):
    
    dem_size = int(TILE_SIZE / PIXEL_SIZE)
    
    # Get buildings mask
    file_mask_buildings_path = os.path.join(DIR_MASKS_BUILDINGS, file_name + ".tif")
    dataset_mask_buildings = rasterio.open(file_mask_buildings_path)
    mask_buildings = dataset_mask_buildings.read(1)
    mask_buildings = mask_buildings.astype(np.uint8)

    # Dilate buildings mask
    kernel = np.ones((5,5))
    mask_buildings = cv.dilate(mask_buildings, kernel, iterations=1)
    mask_buildings = mask_buildings == 1

    file_las_path = os.path.join(DIR_LIDAR, file_name + ".las")

    # Get buildings heights
    print("Buildings")
    las_buildings = pylas.read(file_las_path)
    las_buildings.points = las_buildings.points[las_buildings.classification == CLASS_BUILDINGS]
    heights_buildings = create_heights(las_buildings, PIXEL_SIZE, dem_size)

    # Set buildings that have been falsely classified as vegetation
    falsely_classified = np.full((dem_size, dem_size), -1, np.float32)
    las_trees = pylas.read(file_las_path)
    las_trees.points = las_trees.points[np.isin(las_trees.classification, CLASSES_TREES)]
    las_trees.points = las_trees.points[las_trees['number_of_returns'] < MIN_N_OF_RETURNS_TREES]
    heights_trees = create_heights(las_trees, PIXEL_SIZE, dem_size)
    falsely_classified[mask_buildings] = heights_trees[mask_buildings]
    falsely_classified[heights_buildings != -1] = -1
    heights_buildings = np.maximum(heights_buildings, falsely_classified)
    
    # Get terrain heights
    print("Terrain")
    las_terrain = pylas.read(file_las_path)
    las_terrain.points = las_terrain.points[las_terrain.classification == CLASS_GROUND]
    las_terrain.points = las_terrain.points[las_terrain['number_of_returns'] == 1]
    heights_terrain = create_heights(las_terrain, PIXEL_SIZE, dem_size)
    erode(heights_terrain)

    # Get trees heights
    print("Trees")
    las_trees = pylas.read(file_las_path)
    las_trees.points = las_trees.points[np.isin(las_trees.classification, CLASSES_TREES)]
    las_trees.points = las_trees.points[las_trees['number_of_returns'] >= MIN_N_OF_RETURNS_TREES]
    heights_trees = create_heights(las_trees, PIXEL_SIZE, dem_size)
    
    # Interpolate trees
    print("Interpolating trees")
    mask_interpolation_trees = heights_terrain != -1
    mask_interpolation_trees = mask_interpolation_trees.astype(np.uint8)
    kernel = np.ones((5,5))
    mask_interpolation_trees = cv.erode(mask_interpolation_trees, kernel, iterations=1)
    mask_interpolation_trees = mask_interpolation_trees == 1
    interpolate(heights_trees, mask_interpolation_trees, limit_v=None, limit_h=6)
    erode(heights_trees)

    # Interpolate buildings
    print("Interpolating buildings")
    mask_interpolation_trees = mask_buildings == False
    interpolate(heights_buildings, mask_interpolation_trees, limit_v=8, limit_h=10)
    interpolate(heights_buildings, mask_interpolation_trees, limit_v=8, limit_h=10)
    
    # Create bounds
    bounds = get_file_bounds(file_name)
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
    save_raster(heights_buildings, file_path_buildings, transform)
    
    # Save trees
    file_path_trees = os.path.join(dir_out, "trees", "raw", f"{file_name}.tif")
    save_raster(heights_trees, file_path_trees, transform)


def main():
    dir_out = r"C:\data\heights"
    files_in = get_dir_file_names(DIR_LIDAR)
    for file_name in files_in:
        print(f"{file_name}")
        generate_DEM(file_name, dir_out)

main()