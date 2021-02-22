import rasterio
import sys
import matplotlib.pyplot as plt
import skimage.feature
import numpy as np

def main():

    file_path_in = sys.argv[1]
    file_path_out = sys.argv[2]
    dataset = rasterio.open(file_path_in)
    heights = dataset.read(1)

    average = np.mean(heights)

    sigma = 0.1
    low_threshold=average/3.5
    high_threshold=average/2

    print(heights.min())
    print(heights.max())
    print(average)

    edges = skimage.feature.canny(
        image=heights,
        sigma=sigma,
        low_threshold=low_threshold,
        high_threshold=high_threshold,
    )

    print(heights.shape)
    print(edges.shape)

    # plt.imshow(edges, cmap='gray')
    # plt.show()

    dataset_out = rasterio.open(
        file_path_out,
        mode="w",
        driver="GTiff",
        width=heights.shape[1],
        height=heights.shape[0],
        count=1,
        crs=dataset.crs,
        transform=dataset.transform,
        dtype=np.int32
    )
    dataset_out.write(edges.astype(np.int32), 1)

main()