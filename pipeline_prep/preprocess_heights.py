import rasterio
import os
import cv2 as cv
from aggregate import aggregate

import matplotlib.pyplot as plt

# In
DTM_RAW_DIR_PATH = r"D:\PrintCitiesData\DTM\DTM_raw"
DEM_RAW_DIR_PATH = r"D:\PrintCitiesData\DEM\DEM_raw"

# Out
DTM_1x1_DIR_PATH = r"D:\PrintCitiesData\DTM\DTM_1x1"
DTM_2x2_DIR_PATH = r"D:\PrintCitiesData\DTM\DTM_2x2"
DTM_4x4_DIR_PATH = r"D:\PrintCitiesData\DTM\DTM_4x4"
SUB_1x1_DIR_PATH = r"D:\PrintCitiesData\SUB\SUB_1x1"
SUB_2x2_DIR_PATH = r"D:\PrintCitiesData\SUB\SUB_2x2"
SUB_4x4_DIR_PATH = r"D:\PrintCitiesData\SUB\SUB_4x4"

# Args
AGGREG_METHOD = "max"
GAUSSIAN_SIZE = 5
SUBTRACTED_THRESHOLD = 1.5

def fill_holes(heights):
    n_rows, n_cols = heights.shape
    for row in range(1, n_rows-1):
        for col in range(1, n_cols-1):
            if heights[row,col] >= SUBTRACTED_THRESHOLD:
                continue
            idxs = [(row-1,col-1),(row-1,col+1),(row+1,col-1),(row+1,col+1)]
            hs = [heights[idx] for idx in idxs]
            hs = [h for h in hs if h >= SUBTRACTED_THRESHOLD]
            if len(hs) >= 3:
                heights[row,col] = sum(hs)/len(hs)

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

    file_names = get_dir_files(DTM_RAW_DIR_PATH)

    for file_name in file_names:
        
        # Read DTM
        dtm_file_in_path = os.path.join(DTM_RAW_DIR_PATH, file_name)
        dataset_dtm = rasterio.open(dtm_file_in_path)
        heights_dtm = dataset_dtm.read(1)

        # Read DEM
        dem_file_in_path = os.path.join(DEM_RAW_DIR_PATH, file_name)
        dataset_dem = rasterio.open(dem_file_in_path)
        heights_dem = dataset_dem.read(1)

        assert(heights_dtm.shape == heights_dem.shape)

        # DTM clean
        heights_dtm = cv.GaussianBlur(heights_dtm, (GAUSSIAN_SIZE,GAUSSIAN_SIZE), 0)

        # Subtracted
        heights_sub = heights_dem - heights_dtm
        mask_sub = heights_sub == 0
        heights_sub = cv.GaussianBlur(heights_sub, (GAUSSIAN_SIZE,GAUSSIAN_SIZE), 0)
        heights_sub[mask_sub] = 0
        heights_sub[heights_sub <= SUBTRACTED_THRESHOLD] = 0
        # fill_holes(heights_sub)

        # Save DTM 1x1
        file_path_out = os.path.join(DTM_1x1_DIR_PATH, file_name)
        save(heights_dtm, dataset_dtm.transform, file_path_out, dataset_dtm.crs)
        
        # Save SUB 1x1
        file_path_out = os.path.join(SUB_1x1_DIR_PATH, file_name)
        save(heights_sub, dataset_dtm.transform, file_path_out, dataset_dtm.crs)

        # Aggregate and save DTM 2x2
        heights_dtm_2x2, transform_2x2 = aggregate(heights_dtm, dataset_dtm.bounds, 2, AGGREG_METHOD)
        file_path_out = os.path.join(DTM_2x2_DIR_PATH, file_name)
        save(heights_dtm_2x2, transform_2x2, file_path_out, dataset_dtm.crs)
        
        # Aggregate and save SUB 2x2
        heights_sub_2x2, transform_2x2 = aggregate(heights_sub, dataset_dtm.bounds, 2, AGGREG_METHOD)
        file_path_out = os.path.join(SUB_2x2_DIR_PATH, file_name)
        save(heights_sub_2x2, transform_2x2, file_path_out, dataset_dtm.crs)

        print(f"saved {file_name}")

main()