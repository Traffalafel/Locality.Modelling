import rasterio
import sys
import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np

def main():
    file_in_path = sys.argv[1]
    file_out_path = sys.argv[2]

    dataset = rasterio.open(file_in_path)
    heights = dataset.read(1)

    heights = cv.GaussianBlur(heights,(3,3),0)

    dataset_out = rasterio.open(
        file_out_path,
        mode='w',
        driver="GTiff",
        width=heights.shape[1],
        height=heights.shape[0],
        count=1,
        crs=dataset.crs,
        transform=dataset.transform,
        dtype=heights.dtype
    )
    dataset_out.write(heights, 1)

main()