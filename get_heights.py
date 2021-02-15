import rasterio
import rasterio.merge
import rasterio.mask
from rasterio.io import MemoryFile
from shapely.geometry import Polygon
import os
import math

# Arguments
AGGREG_SIZE = 4

# Constants
TIF_FILE_KMS = 1000
ETRS89_UTM32_EPSG = 25832

def get_tif_paths(bounds, aggreg_size, tifs_dir_path):
    
    bounds_w, bounds_e, bounds_s, bounds_n = bounds

    min_file_x = math.floor(bounds_w / TIF_FILE_KMS)
    min_file_y = math.floor(bounds_s / TIF_FILE_KMS)
    max_file_x = math.floor(bounds_e / TIF_FILE_KMS)
    max_file_y = math.floor(bounds_n / TIF_FILE_KMS)

    file_paths = []
    for file_x in range(min_file_x, max_file_x+1):
        for file_y in range(min_file_y, max_file_y+1):
            file_name = f"DSM_1km_{file_y}_{file_x}.tif"
            file_path = os.path.join(tifs_dir_path, file_name)
            file_paths.append(file_path)

    return file_paths


def mask_data(heights, transform, bounds):

    bounds_w, bounds_e, bounds_s, bounds_n = bounds

    with MemoryFile() as memfile:
        dataset = memfile.open(
            driver="GTiff", 
            count=1, 
            crs=ETRS89_UTM32_EPSG,
            height=heights.shape[0],
            width=heights.shape[1],
            transform=transform,
            dtype=heights.dtype
        )
        dataset.write(heights, 1)

        polygon = Polygon([
            (bounds_w, bounds_s),
            (bounds_w, bounds_n),
            (bounds_e, bounds_n),
            (bounds_e, bounds_s)
        ])

        contents_new, transform_new = rasterio.mask.mask(dataset, [polygon], crop=True)
        heights_new = contents_new[0,:,:]
        return heights_new, transform_new


def get_heights(tifs_dir_path, bounds):
    bounds_w, bounds_e, bounds_s, bounds_n = bounds

    tif_paths = get_tif_paths(bounds, AGGREG_SIZE, tifs_dir_path)
    datasets = []
    for tif_path in tif_paths:
        ds = rasterio.open(tif_path)
        datasets.append(ds)

    contents, transform  = rasterio.merge.merge(datasets)
    heights = contents[0,:,:]

    heights, transform = mask_data(heights, transform, bounds)

    return heights, transform


# def main():

#     # Parse arguments
#     tifs_dir_path = sys.argv[1]
#     tif_out_path = sys.argv[2]
#     bounds_w = sys.argv[3]
#     bounds_e = sys.argv[4]
#     bounds_s = sys.argv[5]
#     bounds_n = sys.argv[6]
#     bounds = (bounds_w, bounds_e, bounds_s, bounds_n)
    
#     heights, transform = get_region_heights(tifs_dir_path, bounds)

#     dataset_out = rasterio.open(
#         tif_out_path,
#         mode='w',
#         driver='GTiff',
#         height=heights.shape[0],
#         width=heights.shape[1],
#         count=1,
#         crs=ETRS89_UTM32_EPSG,
#         transform=transform,
#         dtype=heights.dtype
#     )
#     dataset_out.write(heights, 1)

# main()