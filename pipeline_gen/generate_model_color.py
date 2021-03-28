import numpy as np
import sys
import rasterio
from pyproj import Transformer
import os
import pymeshlab
from get_contents import get_contents, compute_shape
from meshify import meshify_elevation, meshify_terrain

# ARGS
HEIGHTS_TIFS_DIR_PATH = r"D:\PrintCitiesData\DHM_overflade_blurred_3"
ROADS_TIF_DIR_PATH = r"D:\PrintCitiesData\roads_tif"
BUILDINGS_TIF_DIR_PATH = r"D:\PrintCitiesData\buildings_tif"

# Constants
ORIGINAL_PIXEL_SIZE = 0.4
CRS_WGS84 = 4326
CRS_ETRS89 = 25832
NULL_HEIGHT = -1

def generate_meshimport(tile_name, mesh_type, color_string):

    s = f'<MLMesh label="{tile_name}_{mesh_type}" visible="1" filename="{tile_name}_{mesh_type}.ply">\n'
    s += f'<RenderingOption pointSize="3" wireWidth="1" wireColor="64 64 64 255" boxColor="234 234 234 255" pointColor="131 149 69 255" solidColor="{color_string} 255">100001000000000000000000000001011000001010100000000100111011110000001001</RenderingOption>\n'
    s += "</MLMesh>\n"
    return s

def generate_meshlab_project(dir_out, tiles_x, tiles_y):

    s = "<!DOCTYPE MeshLabDocument>\n"
    s += "<MeshLabProject>\n"
    s += "<MeshGroup>\n"

    for tile_x in range(tiles_x):
        for tile_y in range(tiles_y):
            tile_name = f"{tile_x+1}_{tile_y+1}"
            s += generate_meshimport(tile_name, "buildings", "212 212 212")
            s += generate_meshimport(tile_name, "green", "98 161 116")
            s += generate_meshimport(tile_name, "roads", "77 77 77")
            s += generate_meshimport(tile_name, "terrain", "152 147 141")
            s += generate_meshimport(tile_name, "trees", "53 170 100")
            s += generate_meshimport(tile_name, "water", "45 106 163")

    s += "</MeshGroup>\n"
    s += "<RasterGroup/>\n"
    s += "</MeshLabProject>\n"

    file_path = os.path.join(dir_out, "project.mlp")
    with open(file_path, "w+") as fd:
        fd.write(s) 

def get_heights(path, point_sw, point_nw, point_se, pixel_size):
    n_rows, n_cols = compute_shape(point_sw, point_nw, point_se, pixel_size)
    if os.path.exists(path):
        return get_contents(path, point_sw, point_nw, point_se, pixel_size)
    else:
        return np.full((n_rows, n_cols), NULL_HEIGHT, dtype=np.float32)

def get_mask(path, point_sw, point_nw, point_se, pixel_size):
    n_rows, n_cols = compute_shape(point_sw, point_nw, point_se, pixel_size)
    if os.path.exists(path):
        mask = get_contents(path, point_sw, point_nw, point_se, pixel_size)
        return mask == 1
    else:
        return np.full((n_rows, n_cols), False, dtype=bool)

def generate_model_color(data_dir_path, dir_out, point_sw, point_nw, point_se, tiles_x, tiles_y, aggreg_size):

    pixel_size = ORIGINAL_PIXEL_SIZE * aggreg_size
    aggreg_string = f"{aggreg_size}x{aggreg_size}"

    # Get heights
    heights_terrain_dir_path = os.path.join(data_dir_path, "heights", "terrain", aggreg_string)
    heights_terrain = get_heights(heights_terrain_dir_path, point_sw, point_nw, point_se, pixel_size)
    
    heights_buildings_dir_path = os.path.join(data_dir_path, "heights", "buildings", aggreg_string)
    heights_buildings = get_heights(heights_buildings_dir_path, point_sw, point_nw, point_se, pixel_size)

    heights_trees_dir_path = os.path.join(data_dir_path, "heights", "trees", aggreg_string)
    heights_trees = get_heights(heights_trees_dir_path, point_sw, point_nw, point_se, pixel_size)
    
    # Get masks
    mask_roads_dir_path = os.path.join(data_dir_path, "masks", "roads", aggreg_string)
    mask_roads = get_mask(mask_roads_dir_path, point_sw, point_nw, point_se, pixel_size)
   
    mask_green_dir_path = os.path.join(data_dir_path, "masks", "green", aggreg_string)
    mask_green = get_mask(mask_green_dir_path, point_sw, point_nw, point_se, pixel_size)

    mask_water_dir_path = os.path.join(data_dir_path, "masks", "water", aggreg_string)
    mask_water = get_mask(mask_water_dir_path, point_sw, point_nw, point_se, pixel_size)

    n_rows, n_cols = compute_shape(point_sw, point_nw, point_se, pixel_size)
    n_rows_tile = n_rows // tiles_y
    n_cols_tile = n_cols // tiles_x

    for tile_x in range(tiles_x):
        for tile_y in range(tiles_y):

            tile_name = f"{tile_x+1}_{tile_y+1}"
            print(tile_name)

            min_x = tile_x * n_cols_tile
            max_x = (tile_x+1) * n_cols_tile + 1
            min_y = tile_y * n_rows_tile
            max_y = (tile_y+1) * n_rows_tile + 1

            offset_x = min_x 
            offset_y = min_y

            heights_terrain_tile = heights_terrain[min_y:max_y, min_x:max_x]
            heights_buildings_tile = heights_buildings[min_y:max_y, min_x:max_x]
            heights_trees_tile = heights_trees[min_y:max_y, min_x:max_x]
            mask_roads_tile = mask_roads[min_y:max_y, min_x:max_x]
            mask_green_tile = mask_green[min_y:max_y, min_x:max_x]
            mask_water_tile = mask_water[min_y:max_y, min_x:max_x]

            ms_terrain, ms_roads, ms_green, ms_water = meshify_terrain(heights_terrain_tile, mask_roads_tile, mask_green_tile, mask_water_tile, offset_x, offset_y, pixel_size)

            # Save terrain
            file_terrain_out = f"{tile_name}_terrain.ply"
            file_out_path = os.path.join(dir_out, file_terrain_out)
            ms_terrain.save_current_mesh(file_out_path)
            
            # Save roads
            file_roads_out = f"{tile_name}_roads.ply"
            file_out_path = os.path.join(dir_out, file_roads_out)
            ms_roads.save_current_mesh(file_out_path)
            
            # Save green
            file_green_out = f"{tile_name}_green.ply"
            file_out_path = os.path.join(dir_out, file_green_out)
            ms_green.save_current_mesh(file_out_path)

            # Save water
            file_water_out = f"{tile_name}_water.ply"
            file_out_path = os.path.join(dir_out, file_water_out)
            ms_water.save_current_mesh(file_out_path)

            ms_buildings = meshify_elevation(heights_buildings_tile, heights_terrain_tile, offset_x, offset_y, pixel_size)

            # Save buildings
            file_buildings_out = f"{tile_name}_buildings.ply"
            file_out_path = os.path.join(dir_out, file_buildings_out)
            ms_buildings.save_current_mesh(file_out_path)

            ms_trees = meshify_elevation(heights_trees_tile, heights_terrain_tile, offset_x, offset_y, pixel_size)

            # Save trees
            file_trees_out = f"{tile_name}_trees.ply"
            file_out_path = os.path.join(dir_out, file_trees_out)
            ms_trees.save_current_mesh(file_out_path)

def main():

    data_dir = r"C:\data"
    dir_out = r"C:\Users\traff\source\repos\PrintCities.Modelling\data\models"
    aggreg_size = 2

    sw_lat = float(sys.argv[1])
    sw_lng = float(sys.argv[2])
    nw_lat = float(sys.argv[3])
    nw_lng = float(sys.argv[4])
    se_lat = float(sys.argv[5])
    se_lng = float(sys.argv[6])
    tiles_x = int(sys.argv[7])
    tiles_y = int(sys.argv[8])

    # Convert coordinates
    transformer = Transformer.from_crs(CRS_WGS84, CRS_ETRS89)
    
    sw_x, sw_y = transformer.transform(sw_lat, sw_lng)
    point_sw = np.array([sw_x, sw_y])
    point_sw = point_sw.astype(np.uint32)

    nw_x, nw_y = transformer.transform(nw_lat, nw_lng)
    point_nw = np.array([nw_x, nw_y])
    point_nw = point_nw.astype(np.uint32)
    
    se_x, se_y = transformer.transform(se_lat, se_lng)
    point_se = np.array([se_x, se_y])
    point_se = point_se.astype(np.uint32)

    generate_model_color(data_dir, dir_out, point_sw, point_nw, point_se, tiles_x, tiles_y, aggreg_size)

    generate_meshlab_project(dir_out, tiles_x, tiles_y)

main()
