import numpy as np
import sys
import rasterio
from pyproj import Transformer
from math import floor, ceil
import os

import matplotlib.pyplot as plt

from get_contents import get_contents
from meshify import meshify_elevation, meshify_terrain

# ARGS
HEIGHTS_TIFS_DIR_PATH = r"D:\PrintCitiesData\DHM_overflade_blurred_3"
ROADS_TIF_DIR_PATH = r"D:\PrintCitiesData\roads_tif"
BUILDINGS_TIF_DIR_PATH = r"D:\PrintCitiesData\buildings_tif"
HEIGHTS_BOOST = 3
MATERIALS = False

# Constants
AGGREG_SIZE = 1
ORIGINAL_PIXEL_SIZE = 0.4
PIXEL_SIZE = ORIGINAL_PIXEL_SIZE * AGGREG_SIZE

def flip(array):
    array = np.flip(array, axis=0)
    return array

def generate_model_color(data_dir_path, dir_out, point_sw, point_nw, point_se, tiles_x, tiles_y):

    # Get heights
    heights_terrain_dir_path = os.path.join(data_dir_path, "heights", "terrain", "1x1")
    heights_terrain = get_contents(heights_terrain_dir_path, point_sw, point_nw, point_se, PIXEL_SIZE)
    heights_terrain = flip(heights_terrain)
    
    heights_buildings_dir_path = os.path.join(data_dir_path, "heights", "buildings", "1x1")
    heights_buildings = get_contents(heights_buildings_dir_path, point_sw, point_nw, point_se, PIXEL_SIZE)
    heights_buildings = flip(heights_buildings)

    heights_trees_dir_path = os.path.join(data_dir_path, "heights", "trees", "1x1")
    heights_trees = get_contents(heights_trees_dir_path, point_sw, point_nw, point_se, PIXEL_SIZE)
    heights_trees = flip(heights_trees)
    
    # Get masks
    mask_roads_dir_path = os.path.join(data_dir_path, "masks", "roads", "1x1")
    mask_roads = get_contents(mask_roads_dir_path, point_sw, point_nw, point_se, PIXEL_SIZE)
    mask_roads = mask_roads == 1
    mask_roads = flip(mask_roads)
   
    mask_green_dir_path = os.path.join(data_dir_path, "masks", "green", "1x1")
    mask_green = get_contents(mask_green_dir_path, point_sw, point_nw, point_se, PIXEL_SIZE)
    mask_green = mask_green == 1
    mask_green = flip(mask_green)

    mask_water_dir_path = os.path.join(data_dir_path, "masks", "water", "1x1")
    mask_water = get_contents(mask_water_dir_path, point_sw, point_nw, point_se, PIXEL_SIZE)
    mask_water = mask_water == 1
    mask_water = flip(mask_water)

    n_rows, n_cols = heights_terrain.shape
    len_row = n_rows // tiles_y
    len_col = n_cols // tiles_x

    plt.imsave(r"C:\Users\traff\Desktop\img.png", heights_terrain[:n_rows//2,:n_cols//2])

    for tile_x in range(tiles_x):
        for tile_y in range(tiles_y):

            tile_name = f"{tile_x+1}_{tile_y+1}"
            print(tile_name)

            min_x = tile_x * len_col
            max_x = (tile_x+1) * len_col + 1
            min_y = tile_y * len_row
            max_y = (tile_y+1) * len_row + 1

            offset_x = min_x 
            offset_y = min_y

            heights_terrain_tile = heights_terrain[min_y:max_y, min_x:max_x]
            heights_buildings_tile = heights_buildings[min_y:max_y, min_x:max_x]
            heights_trees_tile = heights_trees[min_y:max_y, min_x:max_x]
            mask_roads_tile = mask_roads[min_y:max_y, min_x:max_x]
            mask_green_tile = mask_green[min_y:max_y, min_x:max_x]
            mask_water_tile = mask_water[min_y:max_y, min_x:max_x]

            plt.imsave(f"C:\\Users\\traff\\Desktop\\{tile_name}.png", heights_terrain_tile)

            ms_terrain, ms_roads, ms_green, ms_water = meshify_terrain(heights_terrain_tile, mask_roads_tile, mask_green_tile, mask_water_tile, offset_x, offset_y)

            # Save terrain
            file_terrain_out = f"{tile_name}_terrain.stl"
            file_out_path = os.path.join(dir_out, file_terrain_out)
            ms_terrain.save_current_mesh(file_out_path)
            
            # Save roads
            file_roads_out = f"{tile_name}_roads.stl"
            file_out_path = os.path.join(dir_out, file_roads_out)
            ms_roads.save_current_mesh(file_out_path)
            
            # Save green
            file_green_out = f"{tile_name}_green.stl"
            file_out_path = os.path.join(dir_out, file_green_out)
            ms_green.save_current_mesh(file_out_path)

            # Save water
            file_water_out = f"{tile_name}_water.stl"
            file_out_path = os.path.join(dir_out, file_water_out)
            ms_water.save_current_mesh(file_out_path)

            mesh_buildings = meshify_elevation(heights_buildings_tile, heights_terrain_tile, offset_x, offset_y)

            # Save buildings
            file_buildings_out = f"{tile_name}_buildings.stl"
            file_out_path = os.path.join(dir_out, file_buildings_out)
            mesh_buildings.save_current_mesh(file_out_path)

            mesh_trees = meshify_elevation(heights_trees_tile, heights_terrain_tile, offset_x, offset_y)

            # Save trees
            file_trees_out = f"{tile_name}_trees.stl"
            file_out_path = os.path.join(dir_out, file_trees_out)
            mesh_trees.save_current_mesh(file_out_path)

def main():
    
    data_dir = r"C:\data"
    dir_out = r"C:\Users\traff\source\repos\PrintCities.Modelling\data\models"
    point_sw = np.array([723583, 6176488])
    point_nw = np.array([723786, 6176880])
    point_se = np.array([723892, 6176328])
    # point_sw = np.array([723000, 6176000])
    # point_nw = np.array([723000, 6176500])
    # point_se = np.array([723500, 6176000])
    tiles_x = 3
    tiles_y = 3

    generate_model_color(data_dir, dir_out, point_sw, point_nw, point_se, tiles_x, tiles_y)

main()

# def main():
    
#     # Parse args
#     dir_out_path = sys.argv[1]
#     name_out = sys.argv[2]
#     sw_lat = float(sys.argv[3])
#     sw_lng = float(sys.argv[4])
#     size_metres = int(sys.argv[5])
#     n_splits = int(sys.argv[6])

#     # Compute coordinates in ETRS89 UTM 32N
#     transformer = Transformer.from_crs(WGS84, ETRS89_UTM_32N)
#     bound_w, bound_s = transformer.transform(sw_lat, sw_lng)
#     bound_e = bound_w + size_metres
#     bound_n = bound_s + size_metres
#     bounds_heights = (bound_w, bound_e, bound_s, bound_n)

#     print(f"W: {bound_w}")
#     print(f"E: {bound_e}")
#     print(f"S: {bound_s}")
#     print(f"N: {bound_n}")

#     # Get heights
#     heights, _ = get_contents(HEIGHTS_TIFS_DIR_PATH, bounds_heights)

#     # Heights boost
#     for i in range(heights.shape[0]):
#         for j in range(heights.shape[1]):
#             heights[i][j] *= HEIGHTS_BOOST

#     len_x, len_y = heights.shape

#     if MATERIALS is True:

#         # Create offsetted bounds for materials
#         bound_materials_w = bound_w + (PIXEL_SIZE / 2)
#         bound_materials_e = bound_e + (PIXEL_SIZE / 2)
#         bound_materials_s = bound_s + (PIXEL_SIZE / 2)
#         bound_materials_n = bound_n + (PIXEL_SIZE / 2)
#         bounds_materials = (bound_materials_w, bound_materials_e, bound_materials_s, bound_materials_n)

#         # Get roads
#         # roads, _ = get_contents(ROADS_TIF_DIR_PATH, bounds_materials)
#         # roads = roads.astype(np.int32)

#         # Get buildings
#         buildings, _ = get_contents(BUILDINGS_TIF_DIR_PATH, bounds_materials)
#         buildings = buildings.astype(np.int32)
#         buildings = buildings[1:,1:]
#         # buildings = set_neigbors(buildings, 2, 1)

#         # Create materials grid
#         materials = np.zeros(shape=(len_x-1, len_y-1), dtype=np.int32)
#         # materials[roads == 1] = 1
#         materials[buildings == 1] = 2

#         # Material names and mtllib
#         materials_names = {
#             0: "default",
#             1: "road",
#             2: "building"
#         }
#         mtllib = r".\materials.mtl"

#     else:
#         materials = None
#         materials_names = None
#         mtllib = None

#     for row in range(n_splits):
#         for col in range(n_splits):

#             # Compute index bounds for heights
#             min_x = floor(len_x/n_splits)*row
#             max_x = floor(len_x/n_splits)*(row+1) + 1
#             min_y = floor(len_y/n_splits)*col
#             max_y = floor(len_y/n_splits)*(col+1) + 1

#             # Compute index bounds for materials
#             min_x_mat = floor(len_x/n_splits)*row
#             max_x_mat = floor(len_x/n_splits)*(row+1)
#             min_y_mat = floor(len_y/n_splits)*col
#             max_y_mat = floor(len_y/n_splits)*(col+1)

#             # Get tile and meshify
#             tile = heights[min_x:max_x,min_y:max_y]

#             if materials is not None:
#                 tile_materials = materials[min_x_mat:max_x_mat,min_y_mat:max_y_mat]
#             else:
#                 tile_materials = None

#             lines = meshify(tile, PIXEL_SIZE, MIN_DEPTH, tile_materials, materials_names, mtllib)

#             # Save
#             file_name = f"{name_out}_{row+1}_{col+1}.obj"
#             file_out_path = join(dir_out_path, file_name)
#             with open(file_out_path, 'w+') as fd:
#                 fd.writelines(lines)