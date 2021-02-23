import os
import rasterio
from meshify_layer import meshify_layer
import numpy as np

# ARGS
USE_MATERIALS = True
MIN_THRESHOLD = None
HEIGHTS_BOOST = 3
MIN_DEPTH = 30
MTLLIB = r".\materials.mtl"

# Sources
HEIGHTS_DIR_PATH = r"D:\PrintCitiesData\DHM_overflade"
MATERIALS_DIRS_PATHS = [
    # r"D:\PrintCitiesData\roads_tif"
]

# Constants
AGGREG_SIZE = 4
ORIGINAL_PIXEL_SIZE = 0.4
PIXEL_SIZE = ORIGINAL_PIXEL_SIZE * AGGREG_SIZE
WGS84 = 4326
ETRS89_UTM_32N = 25832

def generate_layer(file_name, dir_out_path, n_splits):

    # Compute input files paths
    heights_file_path = os.path.join(HEIGHTS_DIR_PATH, file_name)
    materials_files_paths = [os.path.join(mat_dir, file_name) for mat_dir in MATERIALS_DIRS_PATHS]

    # Read heights
    dataset = rasterio.open(heights_file_path)
    heights = dataset.read(1)

    # Read materials
    if USE_MATERIALS:
        datasets_materials = [rasterio.open(path) for path in materials_files_paths]
        materials = [ds.read(1) for ds in datasets_materials]

    n_rows, n_cols = heights.shape
    len_row = int(n_rows // n_splits)
    len_col = int(n_cols // n_splits)

    for i in range(n_splits):
        for j in range(n_splits):

            # Compute indices
            min_x = i * len_row
            max_x = (i+1) * len_row
            min_y = j * len_col
            max_y = (j+1) * len_col
            
            # Get tile data
            heights_tile = heights[min_x:max_x,min_y:max_y]
            if USE_MATERIALS:
                materials_tile = np.zeros(shape=(len_row-1, len_col-1), dtype=np.int32)
                mats = [mat[min_x:max_x-1,min_y:max_y-1] for mat in materials]
                materials_name = dict()
                materials_name[0] = "0"
                for mat_idx, mat in enumerate(mats):
                    materials_tile[mat == 1] = mat_idx + 1
                    materials_name[mat_idx+1] = str(mat_idx+1)
            else:
                materials_tile = None
                materials_name = None

            # REMOVE
            heights[200:300,200:300] = -1
            # REMOVE
            
            # Create mesh
            mesh_lines = meshify_layer(
                heights_tile,
                None, 
                None,
                None
                # materials_tile,
                # materials_name,
                # MTLLIB
            )
            
            # Save
            file_out_name = f"{i}_{j}.obj"
            file_out_path = os.path.join(dir_out_path, file_out_name)
            with open(file_out_path, 'w+') as fd:
                fd.writelines(mesh_lines)

            break
        break
            
def main():
    generate_layer(
        "700_6171.tif", 
        r"C:\Users\traff\source\repos\PrintCities.Modelling\data\models",
        n_splits=4
    )

main()