# Extracts a 1x1km tile from a raw shapefile dataset

import sys
import geopandas
from shapely.geometry import geo
from locality import utils

def main():

    tile_id = sys.argv[1]
    file_in_path = sys.argv[2]
    destination_file_path = sys.argv[3]

    print("Reading input file")
    df = geopandas.read_file(file_in_path)

    print("Clipping")
    bounds = utils.get_file_bounds(tile_id)
    df_clipped = utils.clip(df, bounds)

    print("Writing output file")
    df_clipped.to_file(destination_file_path)

if __name__ == "__main__":
    main()