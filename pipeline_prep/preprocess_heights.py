import rasterio
import os
import cv2 as cv
from aggregate import aggregate
import numpy as np

import matplotlib.pyplot as plt

# Heights in
TERRAIN_DIR = r"D:\PrintCitiesData\heights\terrain"
BUILDINGS_DIR = r"D:\PrintCitiesData\heights\buildings"
TREES_DIR = r"D:\PrintCitiesData\heights\trees"

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

    file_names = get_dir_files(os.path.join(TERRAIN_DIR, "raw"))

    for file_name in file_names:
        
        # Read DTM
        dtm_file_in_path = os.path.join(TERRAIN_DIR, "raw", file_name)
        dataset_dtm = rasterio.open(dtm_file_in_path)
        heights_dtm = dataset_dtm.read(1)

        # Clean DTM
        heights_dtm = cv.GaussianBlur(heights_dtm, (GAUSSIAN_SIZE,GAUSSIAN_SIZE), 0)

        # Get buildings
        buildings_file_in_path = os.path.join(BUILDINGS_DIR, "raw", file_name)
        dataset_buildings = rasterio.open(buildings_file_in_path)
        heights_buildings = dataset_buildings.read(1)

        # Clean buildings
        heights_buildings = cv.GaussianBlur(heights_buildings, (GAUSSIAN_SIZE,GAUSSIAN_SIZE), 0)

        # Save terrain 1x1
        file_path_out = os.path.join(TERRAIN_DIR, "1x1", file_name)
        save(heights_dtm, dataset_dtm.transform, file_path_out, dataset_dtm.crs)
        
        # Save buildings 1x1
        file_path_out = os.path.join(BUILDINGS_DIR, "1x1", file_name)
        save(heights_buildings, dataset_dtm.transform, file_path_out, dataset_dtm.crs)

        # Aggregate and save terrain 2x2
        heights_dtm_2x2, transform_2x2 = aggregate(heights_dtm, dataset_dtm.bounds, 2, AGGREG_METHOD)
        file_path_out = os.path.join(TERRAIN_DIR, "2x2", file_name)
        save(heights_dtm_2x2, transform_2x2, file_path_out, dataset_dtm.crs)
        
        # Aggregate and save buildings 2x2
        heights_buildings_2x2, transform_2x2 = aggregate(heights_buildings, dataset_dtm.bounds, 2, AGGREG_METHOD)
        file_path_out = os.path.join(BUILDINGS_DIR, "2x2", file_name)
        save(heights_buildings_2x2, transform_2x2, file_path_out, dataset_dtm.crs)

        print(f"saved {file_name}")

        break

main()