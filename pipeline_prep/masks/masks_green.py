import os
import sys
import geopandas
from locality import utils, constants

ALL_TOUCHED = True
FCLASSES_GREEN = [
    "forest",
    "park",
    "allotments",
    "meadow",
    "nature_reserve",
    "recreation_ground",
    "orchard",
    "vineyard",
    "scrub",
    "grass",
    "heath",
    "national_park",
    "village_green",
    "plant_nursery",
    "farmland",
    "farmyard"
]

def mask_green(file_path_in, dir_out_path):

    if not os.path.exists(dir_out_path):
        os.mkdir(dir_out_path)

    df = geopandas.read_file(file_path_in)
    file_name = utils.get_file_name(file_path_in)
    min_x, max_x, min_y, max_y = utils.get_file_bounds(file_name)
    bounds = (
        min_x + constants.OFFSET,
        max_x + constants.OFFSET,
        min_y + constants.OFFSET,
        max_y + constants.OFFSET
    )
    df = utils.clip(df, bounds)

    df = utils.filter_by_fclass(df, FCLASSES_GREEN)
    if len(df) == 0:
        return    

    file_name_tif = f"{file_name}.tif"
    bounds = (
        min_x + constants.OFFSET,
        max_x + constants.OFFSET,
        min_y + constants.OFFSET,
        max_y + constants.OFFSET
    )

    # Rasterize and save 1x1 
    file_path_1x1 = os.path.join(dir_out_path, "1x1", file_name_tif)
    pixels_1x1, transform_1x1 = utils.rasterize(df, constants.N_PIXELS_1x1, bounds, ALL_TOUCHED)
    utils.save_raster(pixels_1x1, file_path_1x1, transform_1x1)

    # Rasterize and save 2x2 
    file_path_2x2 = os.path.join(dir_out_path, "2x2", file_name_tif)
    pixels_2x2, transform_2x2 = utils.rasterize(df, constants.N_PIXELS_2x2, bounds, ALL_TOUCHED)
    utils.save_raster(pixels_2x2, file_path_2x2, transform_2x2)

def main():
    
    n_args = len(sys.argv)
    if n_args < 3:
        print("Args: <file_in_path> <dir_out_path>")

    file_in_path = sys.argv[1]
    dir_out_path = sys.argv[2]

    mask_green(file_in_path, dir_out_path)

if __name__ == "__main__":
    main()