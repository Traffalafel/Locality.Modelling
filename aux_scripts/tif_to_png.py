import rasterio
import sys
import numpy as np
from PIL import Image

def main():

    file_path_in = sys.argv[1]
    file_path_out = sys.argv[2]

    dataset = rasterio.open(file_path_in)
    heights = dataset.read(1)

    heights -= heights.min()
    heights /= heights.max()
    heights *= 255
    
    heights = heights.astype(np.uint8)

    img = Image.fromarray(heights)

    img.save(file_path_out)

main()