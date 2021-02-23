import rasterio
import sys
from aggregate import aggregate

# Constants
AGGREG_SIZE = 4
AGGREG_METHOD = "max"

def main():

    file_path_in = sys.argv[1]
    file_path_out = sys.argv[2]

    dataset_in = rasterio.open(file_path_in)

    heights = dataset_in.read(1)
    heights, transform = aggregate(heights, dataset_in.bounds, AGGREG_SIZE, AGGREG_METHOD)

    dataset_out = rasterio.open(
        file_path_out,
        mode='w',
        driver='GTiff',
        width=heights.shape[0],
        height=heights.shape[1],
        count=1,
        dtype=heights.dtype,
        crs=dataset_in.crs,
        transform=transform
    )
    dataset_out.write(heights, 1)
    
main()