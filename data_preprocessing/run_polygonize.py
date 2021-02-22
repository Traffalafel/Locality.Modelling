import geopandas
from polygonize import polygonize
import matplotlib.pyplot as plt
import os
import sys

# Arguments
TILE_SIZE = 1000

# Constants
ETRS89_UTM32N = 25832

def get_file_bounds(file_path):
    head, tail = os.path.split(file_path)
    file_name = tail.split('.')[0]
    min_x = file_name.split('_')[0]
    max_x = min_x + TILE_SIZE
    min_y = file_name.split('_')[1]
    max_y = min_y + TILE_SIZE
    return (min_x, max_x, min_y, max_y)

def main():

    # Parse arguments
    file_in_path = sys.argv[1]
    dir_out_path = sys.argv[2]

    df = geopandas.read_file(file_in_path)
    df = df.to_crs(ETRS89_UTM32N)
    bounds = get_file_bounds(file_in_path)
    
    df = polygonize(df, bounds)

    # Save
    file_out_name = f"{bounds[0]}_{bounds[2]}.shp"
    file_out_path = os.path.join(dir_out_path, file_out_name)
    df.to_file(file_out_path)

main()