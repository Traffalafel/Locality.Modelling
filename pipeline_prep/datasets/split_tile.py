import os
import sys
import geopandas
from locality import constants, utils

# Splits 10km tiles to 1km tiles

TILE_SIZE_10KM = 10000
TILE_SIZE_1KM = 1000

def split_tile(file_in_path, dir_out, margin=0, geometry=None):

    file_name = utils.get_file_name(file_in_path)
    file_name_x = int(file_name.split('_')[0])
    file_name_y = int(file_name.split('_')[1])
    min_x = file_name_x * TILE_SIZE_10KM
    min_y = file_name_y * TILE_SIZE_10KM

    offset = constants.OFFSET

    df = geopandas.read_file(file_in_path)

    for i in range(10):
        for j in range(10):

            west = min_x + (i * TILE_SIZE_1KM) + offset - margin
            east = west + TILE_SIZE_1KM + offset + margin
            south = min_y + (j * TILE_SIZE_1KM) + offset - margin
            north = south + TILE_SIZE_1KM + offset + margin
            bounds = (west, east, south, north)

            file_name_tile = f"{file_name_x*10+i}_{file_name_y*10+j}"
            df_tile = utils.clip(df, bounds)
            if (len(df_tile) == 0):
                continue

            if geometry is not None:
                df_tile = utils.filter_by_geometry(df_tile, geometry)

            file_path_tile = os.path.join(dir_out, f"{file_name_tile}.shp")
            df_tile.to_file(file_path_tile)

def main():

    n_args = len(sys.argv)
    if n_args < 3:
        print("Not enough args")
        return 

    file_in_path = sys.argv[1]
    dir_out_path = sys.argv[2]

    if n_args >= 4:
        margin = float(sys.argv[3])
    else:
        margin = 0

    if n_args >= 5:
        geometry = sys.argv[4]
    else:
        geometry = None

    split_tile(file_in_path, dir_out_path, margin, geometry)

if __name__ == "__main__":
    main()
