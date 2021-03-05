import numpy as np
import pylas
import math
import os
import rasterio
from rasterio.crs import CRS
import rasterio.transform
from interpolate_DEM import interpolate_x, interpolate_y
import sys

CLASS_GROUND = 2
CLASS_BUILDINGS = 6
ETRS89_UTM32N = 25832

TILE_SIZE = 1000
STEP_SIZE = 0.4
MIN_BUCKET_SIZE = 1
INTERPOLATE_LIMIT_METERS = 100

# Computed constants
DEM_SIZE = int(TILE_SIZE / STEP_SIZE)
INTERPOLATE_LIMIT = math.floor(INTERPOLATE_LIMIT_METERS / STEP_SIZE)

def get_file_name(path):
    head, tail = os.path.split(path)
    return tail.split('.')[0]

def get_file_bounds(file_name):
    file_name = file_name.split('.')[0]
    min_x = int(file_name.split('_')[0]) * TILE_SIZE
    max_x = min_x + TILE_SIZE
    min_y = int(file_name.split('_')[1]) * TILE_SIZE
    max_y = min_y + TILE_SIZE
    return (min_x, max_x, min_y, max_y)

def create_heights(file_path, points_class, min_bucket_size):
    las = pylas.read(file_path)
    las.points = las.points[las.classification == points_class]

    x_scale = las.header.x_scale
    x_offset = las.header.x_offset
    x_min = las.header.x_min
    y_scale = las.header.y_scale
    y_offset = las.header.y_offset
    y_min = las.header.y_min
    z_scale = las.header.z_scale
    z_offset = las.header.z_offset

    points = np.array([[p[0], p[1], p[2]] for p in las.points])
    scale = np.array([x_scale, y_scale, z_scale])
    offset = np.array([x_offset, y_offset, z_offset])
    points = (points * scale) + offset

    coords = points[:,:2]
    mins = np.array([x_min, y_min])
    coords = ((coords - mins) // STEP_SIZE).astype(np.int32)

    buckets = dict()
    for idx, (x_bucket, y_bucket) in enumerate(coords):

        z_coord = points[idx,2]

        if x_bucket not in buckets:
            buckets[x_bucket] = dict()
        if y_bucket not in buckets[x_bucket]:
            buckets[x_bucket][y_bucket] = []
        
        buckets[x_bucket][y_bucket].append(z_coord)

    heights = np.full((DEM_SIZE, DEM_SIZE), -1)
    for x_bucket in buckets:
        for y_bucket in buckets[x_bucket]:
            z_values = buckets[x_bucket][y_bucket]
            if len(z_values) < min_bucket_size:
                continue
            avg_z = sum(z_values)/len(z_values)
            heights[x_bucket][y_bucket] = avg_z

    return heights

def main():
    
    # Create buckets
    file_path_in = sys.argv[1]
    dir_out = sys.argv[2]

    file_name = get_file_name(file_path_in)
    
    print("Generating buildings DEM")
    heights_buildings = create_heights(file_path_in, CLASS_BUILDINGS, MIN_BUCKET_SIZE)

    print("Generating ground DEM")
    heights_ground = create_heights(file_path_in, CLASS_GROUND, 1)
    
    print("Interpolating")
    interpolate_x(heights_buildings, heights_ground, INTERPOLATE_LIMIT)
    interpolate_y(heights_buildings, heights_ground, INTERPOLATE_LIMIT)

    print("Saving")

    bounds = get_file_bounds(file_name)
    transform = rasterio.transform.from_bounds(
        west=bounds[0],
        east=bounds[1],
        south=bounds[2],
        north=bounds[3],
        width=DEM_SIZE,
        height=DEM_SIZE,
    )

    file_path_buildings = os.path.join(dir_out, f"{file_name}.tif")
    dataset_buildings = rasterio.open(
        file_path_buildings,
        mode="w",
        driver="GTiff",
        width=DEM_SIZE,
        height=DEM_SIZE,
        count=1,
        crs=CRS.from_epsg(ETRS89_UTM32N),
        transform=transform,
        dtype=heights_buildings.dtype
    )
    dataset_buildings.write(heights_buildings, 1)

main()