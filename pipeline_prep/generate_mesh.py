import os
import rasterio
from meshify import meshify, mesh_to_obj, meshify_elevation
import numpy as np
import cv2 as cv
from aggregate import aggregate

# ARGS
USE_MATERIALS = True
MIN_THRESHOLD = None
HEIGHTS_BOOST = 3
MIN_DEPTH = 30
MTLLIB = r".\materials.mtl"
AGGREG_SIZE = 2
AGGREG_METHOD = "max"

# Heights
HEIGHTS_TERRAIN_DIR = r"D:\PrintCitiesData\heights\terrain"
HEIGHTS_BUILDINGS_DIR = r"D:\PrintCitiesData\heights\buildings"
HEIGHTS_TREES_DIR = r"D:\PrintCitiesData\heights\trees"

# Masks
MASKS_ROADS_DIR = r"D:\PrintCitiesData\masks\roads"
MASKS_WATER_DIR = r""
MASKS_GRASS_DIR = r""

# Constants
RESOLUTION = f"{AGGREG_SIZE}x{AGGREG_SIZE}"

def set_neighbors(heights, heights_terrain):
    n_rows, n_cols = heights.shape

    right = np.logical_and(heights[:,:n_cols-1] != -1, heights[:,1:] == -1)
    right = np.append(np.full((n_rows,1), False), right, axis=1)

    left = np.logical_and(heights[:,1:] != -1, heights[:,:n_cols-1] == -1)
    left = np.append(left, np.full((n_rows,1), False), axis=1)

    top = np.logical_and(heights[:n_rows-1,:] != -1, heights[1:,:] == -1)
    top = np.append(np.full((1,n_cols), False), top, axis=0)

    bot = np.logical_and(heights[1:,:] != -1, heights[:n_rows-1,:] == -1)
    bot = np.append(bot, np.full((1,n_cols), False), axis=0)

    idxs = np.logical_or(right, left)
    idxs = np.logical_or(idxs, top)
    idxs = np.logical_or(idxs, bot)

    heights[idxs] = heights_terrain[idxs]

def generate_mesh(file_name, dir_out):

    file_name = file_name + ".tif"

    # Terrain heights
    terrain_file_path = os.path.join(HEIGHTS_TERRAIN_DIR, "raw", file_name)
    dataset_terrain = rasterio.open(terrain_file_path)
    heights_terrain = dataset_terrain.read(1)
    
    # Building heights
    buildings_file_path = os.path.join(HEIGHTS_BUILDINGS_DIR, "1x1", file_name)
    dataset_buildings = rasterio.open(buildings_file_path)
    heights_buildings = dataset_buildings.read(1)

    # Create and save terrain mesh

    # Create and save building mesh
    mesh_buildings = meshify_elevation(heights_buildings, heights_terrain)
    file_buildings_out = file_name + "_building.obj"
    file_out_path = os.path.join(dir_out, file_buildings_out)
    mesh_buildings.save_current_mesh(file_out_path)

    # # Trees heights
    # trees_file_path = os.path.join(HEIGHTS_TREES_DIR, "1x1", file_name)
    # dataset_trees = rasterio.open(trees_file_path)
    # heights_trees = dataset_trees.read(1)

    # TODO: 

    # file_terrain_out = file_name + "_terrain.obj"
    # file_out_path = os.path.join(dir_out, file_terrain_out)
    # with open(file_out_path, 'w+') as fd:
    #     fd.writelines(lines_terrain)

    # file_trees_out = file_name + "_trees.obj"
    # file_out_path = os.path.join(dir_out, file_trees_out)
    # with open(file_out_path, 'w+') as fd:
    #     fd.writelines(lines_trees)
    
    # file_roads_out = file_name + "_road.obj"
    # file_out_path = os.path.join(dir_out, file_roads_out)
    # with open(file_out_path, 'w+') as fd:
    #     fd.writelines(lines_roads)

def main():
    file_name = r"710_6180"
    dir_out = r"C:\Users\traff\source\repos\PrintCities.Modelling\data\models"
    generate_mesh(
        file_name,
        dir_out
    )

main()