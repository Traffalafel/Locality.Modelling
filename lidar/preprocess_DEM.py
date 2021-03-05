import os
import sys
import rasterio

def get_file_name(path):
    head, tail = os.path.split(path)
    return tail.split('.')[0]

def main():
    file_path_in = sys.argv[1]
    dir_out = sys.argv[2]

    dataset = rasterio.open(file_path_in)
    heights = dataset.read(1)

    # Gaussian filter

    file_name = get_file_name(file_path_in)
    file_path_out = os.path.join(dir_out, file_name + ".tif")

main()