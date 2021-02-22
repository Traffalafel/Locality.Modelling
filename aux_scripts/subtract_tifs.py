import rasterio
import sys

def main():

    file_1 = sys.argv[1]
    file_2 = sys.argv[2]
    file_out = sys.argv[3]

    dataset_1 = rasterio.open(file_1)
    heights_1 = dataset_1.read(1)
    
    dataset_2 = rasterio.open(file_2)
    heights_2 = dataset_2.read(1)

    heights_new = heights_1 - heights_2

    dataset_new = rasterio.open(
        file_out,
        "w",
        driver="GTiff",
        width=heights_1.shape[1],
        height=heights_1.shape[0],
        count=1,
        crs=dataset_1.crs,
        transform=dataset_1.transform,
        dtype=heights_2.dtype
    )
    dataset_new.write(heights_new, 1)

main()