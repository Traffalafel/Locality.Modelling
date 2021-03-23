import os
import rasterio
from meshify import meshify_elevation, meshify_terrain
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
HEIGHTS_TERRAIN_DIR = r"C:\data\heights\terrain"
HEIGHTS_BUILDINGS_DIR = r"C:\data\heights\buildings"
HEIGHTS_TREES_DIR = r"C:\data\heights\trees"

# Masks
MASKS_ROADS_DIR = r"C:\data\masks\roads"
MASKS_GREEN_DIR = r"C:\data\masks\green"
MASKS_WATER_DIR = r"C:\data\masks\water"

# Constants
RESOLUTION = f"{AGGREG_SIZE}x{AGGREG_SIZE}"

def generate_mesh(file_name, dir_out):

    file_name_raster = file_name + ".tif"

    print("Terrain meshes")

    # Load terrain heights
    terrain_file_path = os.path.join(HEIGHTS_TERRAIN_DIR, "raw", file_name_raster)
    dataset_terrain = rasterio.open(terrain_file_path)
    heights_terrain = dataset_terrain.read(1)
    
    # Roads mask
    roads_file_path = os.path.join(MASKS_ROADS_DIR, file_name_raster)
    dataset_roads = rasterio.open(roads_file_path)
    mask_roads = dataset_roads.read(1)
    mask_roads = mask_roads == 1

    # Green mask
    green_file_path = os.path.join(MASKS_GREEN_DIR, file_name_raster)
    dataset_green = rasterio.open(green_file_path)
    mask_green = dataset_green.read(1)
    mask_green = mask_green == 1

    # Water mask
    water_file_path = os.path.join(MASKS_WATER_DIR, file_name_raster)
    dataset_water = rasterio.open(water_file_path)
    mask_water = dataset_water.read(1)
    mask_water = mask_water == 1
    # mask_water = np.full(heights_terrain.shape, False)

    mask_total = np.logical_or(mask_roads, mask_green)
    mask_total = np.logical_or(mask_total, mask_water)
    ms_terrain, ms_roads, ms_green, ms_water = meshify_terrain(heights_terrain, mask_roads, mask_green, mask_water)

    # Save terrain
    file_terrain_out = file_name + "_terrain.stl"
    file_out_path = os.path.join(dir_out, file_terrain_out)
    ms_terrain.save_current_mesh(file_out_path)
    
    # Save roads
    file_roads_out = file_name + "_roads.stl"
    file_out_path = os.path.join(dir_out, file_roads_out)
    ms_roads.save_current_mesh(file_out_path)
    
    # Save green
    file_green_out = file_name + "_green.stl"
    file_out_path = os.path.join(dir_out, file_green_out)
    ms_green.save_current_mesh(file_out_path)

    # Save water
    file_water_out = file_name + "_water.stl"
    file_out_path = os.path.join(dir_out, file_water_out)
    ms_water.save_current_mesh(file_out_path)

    # Create and save building mesh
    print("Buildings mesh")
    
    # Load buildings heights
    buildings_file_path = os.path.join(HEIGHTS_BUILDINGS_DIR, "1x1", file_name_raster)
    dataset_buildings = rasterio.open(buildings_file_path)
    heights_buildings = dataset_buildings.read(1)

    # Load terrain heights
    terrain_file_path = os.path.join(HEIGHTS_TERRAIN_DIR, "raw", file_name_raster)
    dataset_terrain = rasterio.open(terrain_file_path)
    heights_terrain = dataset_terrain.read(1)

    mesh_buildings = meshify_elevation(heights_buildings, heights_terrain)

    file_buildings_out = file_name + "_buildings.stl"
    file_out_path = os.path.join(dir_out, file_buildings_out)
    mesh_buildings.save_current_mesh(file_out_path)
    
    # Create and save trees mesh
    print("Trees mesh")

    # Load terrain heights
    terrain_file_path = os.path.join(HEIGHTS_TERRAIN_DIR, "raw", file_name_raster)
    dataset_terrain = rasterio.open(terrain_file_path)
    heights_terrain = dataset_terrain.read(1)

    # Trees heights
    trees_file_path = os.path.join(HEIGHTS_TREES_DIR, "1x1", file_name_raster)
    dataset_trees = rasterio.open(trees_file_path)
    heights_trees = dataset_trees.read(1)

    mesh_trees = meshify_elevation(heights_trees, heights_terrain)

    file_trees_out = file_name + "_trees.stl"
    file_out_path = os.path.join(dir_out, file_trees_out)
    mesh_trees.save_current_mesh(file_out_path)

def main():
    file_name = r"725_6175"
    dir_out = r"C:\Users\traff\source\repos\PrintCities.Modelling\data\models"
    generate_mesh(
        file_name,
        dir_out
    )

main()