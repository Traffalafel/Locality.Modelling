import rasterio
import os
import cv2 as cv
from aggregate import aggregate
import numpy as np

import matplotlib.pyplot as plt

# Heights in
IN_DTM_DIR = r"D:\PrintCitiesData\DTM"
IN_DEM_DIR = r"D:\PrintCitiesData\DEM"

# Masks in
MASK_BUILDINGS_DIR = r"D:\PrintCitiesData\masks\buildings"

# Heights out
OUT_TERRAIN_DIR = r"D:\PrintCitiesData\heights\terrain"
OUT_BUILDINGS_DIR = r"D:\PrintCitiesData\heights\buildings"
OUT_TREES_DIR = r"D:\PrintCitiesData\heights\trees"

# Args
AGGREG_METHOD = "max"
GAUSSIAN_SIZE = 3
BUILDINGS_THRESHOLD = 1
TREES_THRESHOLD = 1

def get_dir_files(dir_path):
    contents = os.listdir(dir_path)
    files = [c for c in contents if os.path.isfile(os.path.join(dir_path, c))]
    files_tif = [f for f in files if f.split(".")[1] == "tif"]
    return files_tif

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

def main():

    file_names = get_dir_files(IN_DTM_DIR)

    for file_name in file_names:
        
        # Read DTM
        dtm_file_in_path = os.path.join(IN_DTM_DIR, file_name)
        dataset_dtm = rasterio.open(dtm_file_in_path)
        heights_dtm = dataset_dtm.read(1)

        # Read DEM
        dem_file_in_path = os.path.join(IN_DEM_DIR, file_name)
        dataset_dem = rasterio.open(dem_file_in_path)
        heights_dem = dataset_dem.read(1)

        assert(heights_dtm.shape == heights_dem.shape)

        # DTM clean
        heights_dtm = cv.GaussianBlur(heights_dtm, (GAUSSIAN_SIZE,GAUSSIAN_SIZE), 0)

        # Generate buildings
        heights_buildings = heights_dem - heights_dtm
        heights_buildings = cv.GaussianBlur(heights_buildings, (GAUSSIAN_SIZE,GAUSSIAN_SIZE), 0)

        # Mask buildings
        buildings_file_path = os.path.join(MASK_BUILDINGS_DIR, file_name)
        dataset_buildings = rasterio.open(buildings_file_path)
        buildings = dataset_buildings.read(1)
        heights_buildings[buildings == 0] = 0

        # Open and close buildings
        mask = heights_buildings > BUILDINGS_THRESHOLD
        mask = np.float32(mask)
        kernel_size = 9
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
        mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
        heights_buildings[mask == 0] = 0

        # # Create trees heights
        # heights_trees = heights_dem - heights_dtm - heights_buildings
        # heights_trees = cv.GaussianBlur(heights_trees, (GAUSSIAN_SIZE,GAUSSIAN_SIZE), 0)
        # mask_trees = heights_trees > TREES_THRESHOLD
        # heights_trees[mask_trees == 0] = 0

        # Save terrain 1x1
        file_path_out = os.path.join(OUT_TERRAIN_DIR, "1x1", file_name)
        save(heights_dtm, dataset_dtm.transform, file_path_out, dataset_dtm.crs)
        
        # Save buildings 1x1
        file_path_out = os.path.join(OUT_BUILDINGS_DIR, "1x1", file_name)
        save(heights_buildings, dataset_dtm.transform, file_path_out, dataset_dtm.crs)

        # # Save trees 1x1
        # file_path_out = os.path.join(OUT_TREES_DIR, "1x1", file_name)
        # save(heights_trees, dataset_dtm.transform, file_path_out, dataset_dtm.crs)

        # Aggregate and save terrain 2x2
        heights_dtm_2x2, transform_2x2 = aggregate(heights_dtm, dataset_dtm.bounds, 2, AGGREG_METHOD)
        file_path_out = os.path.join(OUT_TERRAIN_DIR, "2x2", file_name)
        save(heights_dtm_2x2, transform_2x2, file_path_out, dataset_dtm.crs)
        
        # Aggregate and save buildings 2x2
        heights_buildings_2x2, transform_2x2 = aggregate(heights_buildings, dataset_dtm.bounds, 2, AGGREG_METHOD)
        file_path_out = os.path.join(OUT_BUILDINGS_DIR, "2x2", file_name)
        save(heights_buildings_2x2, transform_2x2, file_path_out, dataset_dtm.crs)
        
        # # Aggregate and save trees 2x2
        # heights_trees_2x2, transform_2x2 = aggregate(heights_trees, dataset_dtm.bounds, 2, AGGREG_METHOD)
        # file_path_out = os.path.join(OUT_TREES_DIR, "2x2", file_name)
        # save(heights_trees_2x2, transform_2x2, file_path_out, dataset_dtm.crs)

        print(f"saved {file_name}")

        break

main()