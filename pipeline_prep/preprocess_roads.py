import numpy as np
import geopandas
import rasterio
import rasterio.features
import os
import math
from polygonize import polygonize

# Args
DIR_IN_PATH = r"D:\PrintCitiesData\shp\roads"
DIR_OUT_PATH = r"D:\PrintCitiesData\masks\roads"
ALL_TOUCHED = False
OFFSET_HALF = True

# Constants
TILE_SIZE = 1000
PIXEL_SIZE = 0.4 
N_PIXELS = int(TILE_SIZE / PIXEL_SIZE)

def get_file_bounds(file_name):
    file_name = file_name.split('.')[0]
    min_x = int(file_name.split('_')[0]) * TILE_SIZE
    max_x = min_x + TILE_SIZE
    min_y = int(file_name.split('_')[1]) * TILE_SIZE
    max_y = min_y + TILE_SIZE
    return (min_x, max_x, min_y, max_y)

def get_dir_files(dir_path):
    contents = os.listdir(dir_path)
    files = [c for c in contents if os.path.isfile(os.path.join(dir_path, c))]
    files_shp = [f for f in files if f.split(".")[1] == "shp"]
    return files_shp

def main():

    if not os.path.exists(DIR_OUT_PATH):
        os.mkdir(DIR_OUT_PATH)

    # Compute bounds
    files = get_dir_files(DIR_IN_PATH)

    for file_name in files:

        file_name = file_name.split(".")[0]
        file_path = os.path.join(DIR_IN_PATH, file_name + ".shp")
        df = geopandas.read_file(file_path)

        # Convert to polygons
        bounds = get_file_bounds(file_name)
        df = polygonize(df, bounds)

        if len(df) == 0:
            print(f"skipping {file_name}")
            continue

        if OFFSET_HALF:
            offset = PIXEL_SIZE / 2
        else:
            offset = 0

        for resolution in [1,2,4]:

            shape = N_PIXELS // resolution - 1

            # Rasterize
            transform = rasterio.transform.from_bounds(
                west = bounds[0] + offset * resolution,
                east = bounds[1] - offset * resolution,
                south = bounds[2] + offset * resolution,
                north = bounds[3] - offset * resolution,
                height = shape,
                width = shape
            )
            pixels = rasterio.features.rasterize(
                shapes=df['geometry'],
                out_shape=(shape, shape),
                fill=0,
                transform=transform,
                all_touched=ALL_TOUCHED,
                default_value=1,
                dtype=np.float32
            )

            print(f"resolution: {resolution}")
            print(f"shape: {pixels.shape}")

            # Save
            file = f"{file_name}.tif"
            resolution_string = f"{resolution}x{resolution}"
            file_path_tif = os.path.join(DIR_OUT_PATH, resolution_string, file)
            dataset_out = rasterio.open(
                file_path_tif,
                mode='w',
                driver='GTiff',
                height=shape,
                width=shape,
                count=1,
                crs=df.crs,
                transform=transform,
                dtype=np.float32
            )
            dataset_out.write(pixels, 1)

        print(f"saved {file_name}")

        break

main()