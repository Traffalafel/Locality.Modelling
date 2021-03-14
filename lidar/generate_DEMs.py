import numpy as np
import math
import os
import rasterio
from rasterio.crs import CRS
import rasterio.transform
import sys
from create_heights import create_heights
from interpolate import interpolate

CLASS_GROUND = 2
CLASS_BUILDINGS = 6
CLASSES_TREES = [5, 4]
ETRS89_UTM32N = 25832

TILE_SIZE = 1000
PIXEL_SIZE = 0.4

def get_file_name(file_path):
    head, tail = os.path.split(file_path)
    file_name = tail.split(".")[0]
    return file_name

def get_dir_files(dir_path):
    contents = os.listdir(dir_path)
    files = [c for c in contents if os.path.isfile(os.path.join(dir_path, c))]
    files = [f.split(".")[0] for f in files]
    return files

def get_file_bounds(file_name):
    file_name = file_name.split('.')[0]
    min_x = int(file_name.split('_')[0]) * TILE_SIZE
    max_x = min_x + TILE_SIZE
    min_y = int(file_name.split('_')[1]) * TILE_SIZE
    max_y = min_y + TILE_SIZE
    return (min_x, max_x, min_y, max_y)

def generate_DEM(file_path_in, dir_out):
    
    print(file_path_in)

    dem_size = int(TILE_SIZE / PIXEL_SIZE)
    
    print("Generating ground")
    heights_ground = create_heights(file_path_in, [CLASS_GROUND], 1, PIXEL_SIZE, dem_size)

    print("Generating buildings")
    heights_buildings = create_heights(file_path_in, [CLASS_BUILDINGS], 1, PIXEL_SIZE, dem_size)

    print("Interpolating buildings")
    interpolate(heights_buildings, heights_ground)

    print("Generating trees")
    heights_trees = create_heights(file_path_in, CLASSES_TREES, 1, PIXEL_SIZE, dem_size)

    file_name = get_file_name(file_path_in)
    bounds = get_file_bounds(file_name)
    transform = rasterio.transform.from_bounds(
        west=bounds[0],
        east=bounds[1],
        south=bounds[2],
        north=bounds[3],
        width=dem_size,
        height=dem_size,
    )

    print("Saving buildings")
    file_path_buildings = os.path.join(dir_out, "buildings", "raw", f"{file_name}.tif")
    dataset = rasterio.open(
        file_path_buildings,
        mode="w",
        driver="GTiff",
        width=dem_size,
        height=dem_size,
        count=1,
        crs=CRS.from_epsg(ETRS89_UTM32N),
        transform=transform,
        dtype=heights_buildings.dtype
    )
    dataset.write(heights_buildings, 1)
    
    print("Saving trees")
    file_path_trees = os.path.join(dir_out, "trees", "raw", f"{file_name}.tif")
    dataset = rasterio.open(
        file_path_trees,
        mode="w",
        driver="GTiff",
        width=dem_size,
        height=dem_size,
        count=1,
        crs=CRS.from_epsg(ETRS89_UTM32N),
        transform=transform,
        dtype=heights_trees.dtype
    )
    dataset.write(heights_trees, 1)

def main():
    file_in = r"D:\PrintCitiesData\lidar\710_6180.las"
    dir_out = r"D:\PrintCitiesData\heights"
    generate_DEM(file_in, dir_out)

main()