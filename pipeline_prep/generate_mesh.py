import os
import rasterio
from meshify import meshify, mesh_to_obj
import numpy as np

# ARGS
USE_MATERIALS = True
MIN_THRESHOLD = None
HEIGHTS_BOOST = 3
MIN_DEPTH = 30
MTLLIB = r".\materials.mtl"

# Heights
HEIGHTS_TERRAIN_DIR = r"D:\PrintCitiesData\heights\terrain\2x2"
HEIGHTS_BUILDINGS_DIR = r"D:\PrintCitiesData\heights\buildings\2x2"

# Masks
MASKS_ROADS_DIR = r"D:\PrintCitiesData\masks\roads\2x2"
# MASKS_WATER_DIR = r""
# MASKS_GRASS_DIR = r""

# Constants
TILE_SIZE = 1000
PIXEL_SIZE = 0.4
N_PIXELS = TILE_SIZE / PIXEL_SIZE
WGS84 = 4326
ETRS89_UTM_32N = 25832

def generate_mesh(file_name, dir_out):

    file_name = file_name + ".tif"

    # Terrain heights
    terrain_file_path = os.path.join(HEIGHTS_TERRAIN_DIR, file_name)
    dataset_terrain = rasterio.open(terrain_file_path)
    heights_terrain = dataset_terrain.read(1)
    
    # Building heights
    buildings_file_path = os.path.join(HEIGHTS_BUILDINGS_DIR, file_name)
    dataset_buildings = rasterio.open(buildings_file_path)
    heights_buildings = dataset_buildings.read(1)
    not_building_idxs = heights_buildings <= 0
    heights_buildings += heights_terrain
    heights_buildings[not_building_idxs] = -1

    # Road masks
    roads_file_path = os.path.join(MASKS_ROADS_DIR, file_name)
    dataset_roads = rasterio.open(roads_file_path)
    mask_roads = dataset_roads.read(1)

    materials = set()
    materials.add(0)
    materials.add(1)

    vertices_terrain, faces_terrain = meshify(
        heights_terrain,
        mask_roads,
        materials
    )

    vertices_buildings, faces_buildings = meshify(
        heights_buildings,
        None,
        None
    )

    lines_buildings = mesh_to_obj(vertices_buildings[0], faces_buildings[0], "building", MTLLIB)
    lines_terrain = mesh_to_obj(vertices_terrain[0], faces_terrain[0], "terrain", MTLLIB)
    lines_roads = mesh_to_obj(vertices_terrain[1], faces_terrain[1], "road", MTLLIB)

    file_buildings_out = file_name + "_building.obj"
    file_out_path = os.path.join(dir_out, file_buildings_out)
    with open(file_out_path, 'w+') as fd:
        fd.writelines(lines_buildings)

    file_terrain_out = file_name + "_terrain.obj"
    file_out_path = os.path.join(dir_out, file_terrain_out)
    with open(file_out_path, 'w+') as fd:
        fd.writelines(lines_terrain)
    
    file_roads_out = file_name + "_road.obj"
    file_out_path = os.path.join(dir_out, file_roads_out)
    with open(file_out_path, 'w+') as fd:
        fd.writelines(lines_roads)

def main():
    file_name = r"723_6175"
    dir_out = r"C:\Users\traff\source\repos\PrintCities.Modelling\data\models"
    generate_mesh(
        file_name,
        dir_out
    )

main()