import numpy as np
import sys
from get_contents import get_contents
from meshify import meshify
import rasterio
from pyproj import Transformer
from math import floor, ceil
from os.path import join

# ARGS
HEIGHTS_TIFS_DIR_PATH = r"D:\PrintCitiesData\DHM_overflade_4x4"
ROADS_TIF_DIR_PATH = r"D:\PrintCitiesData\roads_tif"
BUILDINGS_TIF_DIR_PATH = r"D:\PrintCitiesData\buildings_tif"
HEIGHTS_BOOST = 1.0
MATERIALS = False

# Constants
AGGREG_SIZE = 4
MIN_DEPTH = 30
ORIGINAL_PIXEL_SIZE = 0.4
PIXEL_SIZE = ORIGINAL_PIXEL_SIZE * AGGREG_SIZE

WGS84 = 4326
ETRS89_UTM_32N = 25832

def set_neigbors(array, n_dist, new_val):
    array_new = np.zeros(array.shape)
    n_x,n_y = array.shape
    for x in range(n_x):
        lo_x = max(x-n_dist, 0)
        hi_x = min(x+n_dist, n_x)
        for y in range(n_y):
            lo_y = max(y-n_dist, 0)
            hi_y = min(y+n_dist, n_y)
            if 1 in array[lo_x:hi_x,lo_y:hi_y]:
                array_new[x,y] = new_val
    return array_new

def main():
    
    # Parse args
    dir_out_path = sys.argv[1]
    name_out = sys.argv[2]
    bound_w = float(sys.argv[3])
    bound_s = float(sys.argv[4])
    size_metres = int(sys.argv[5])
    n_splits = int(sys.argv[6])

    bound_e = bound_w + size_metres
    bound_n = bound_s + size_metres

    bounds_heights = (bound_w, bound_e, bound_s, bound_n)

    # Get heights
    heights, _ = get_contents(HEIGHTS_TIFS_DIR_PATH, bounds_heights)

    # Heights boost
    for i in range(heights.shape[0]):
        for j in range(heights.shape[1]):
            heights[i][j] *= HEIGHTS_BOOST

    len_x, len_y = heights.shape

    if MATERIALS is True:

        # Create offsetted bounds for materials
        bound_materials_w = bound_w + (PIXEL_SIZE / 2)
        bound_materials_e = bound_e + (PIXEL_SIZE / 2)
        bound_materials_s = bound_s + (PIXEL_SIZE / 2)
        bound_materials_n = bound_n + (PIXEL_SIZE / 2)
        bounds_materials = (bound_materials_w, bound_materials_e, bound_materials_s, bound_materials_n)

        # Get roads
        # roads, _ = get_contents(ROADS_TIF_DIR_PATH, bounds_materials)
        # roads = roads.astype(np.int32)

        # Get buildings
        buildings, _ = get_contents(BUILDINGS_TIF_DIR_PATH, bounds_materials)
        buildings = buildings.astype(np.int32)
        buildings = buildings[1:,1:]
        # buildings = set_neigbors(buildings, 2, 1)

        # Create materials grid
        materials = np.zeros(shape=(len_x-1, len_y-1), dtype=np.int32)
        # materials[roads == 1] = 1
        materials[buildings == 1] = 2

        # Material names and mtllib
        materials_names = {
            0: "default",
            1: "road",
            2: "building"
        }
        mtllib = r".\materials.mtl"

    else:
        materials = None
        materials_names = None
        mtllib = None

    for row in range(n_splits):
        for col in range(n_splits):

            # Compute index bounds for heights
            min_x = floor(len_x/n_splits)*row
            max_x = floor(len_x/n_splits)*(row+1) + 1
            min_y = floor(len_y/n_splits)*col
            max_y = floor(len_y/n_splits)*(col+1) + 1

            # Compute index bounds for materials
            min_x_mat = floor(len_x/n_splits)*row
            max_x_mat = floor(len_x/n_splits)*(row+1)
            min_y_mat = floor(len_y/n_splits)*col
            max_y_mat = floor(len_y/n_splits)*(col+1)

            # Get tile and meshify
            tile = heights[min_x:max_x,min_y:max_y]

            if materials is not None:
                tile_materials = materials[min_x_mat:max_x_mat,min_y_mat:max_y_mat]
            else:
                tile_materials = None

            lines = meshify(tile, PIXEL_SIZE, MIN_DEPTH, tile_materials, materials_names, mtllib)

            # Save
            file_name = f"{name_out}_{row+1}_{col+1}.obj"
            file_out_path = join(dir_out_path, file_name)
            with open(file_out_path, 'w+') as fd:
                fd.writelines(lines)

main()