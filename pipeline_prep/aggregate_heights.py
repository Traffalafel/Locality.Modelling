import numpy as np
import rasterio
import rasterio.transform
import os

AGGREG_METHOD = "max"

def get_dir_file_names(dir_path):
    contents = os.listdir(dir_path)
    files = [c for c in contents if os.path.isfile(os.path.join(dir_path, c))]
    file_names = [f.split(".")[0] for f in files]
    return file_names

def aggregate_heights(heights, aggreg_size, aggreg_method):

    n_rows, n_cols = heights.shape
    n_rows_new = n_rows // aggreg_size
    n_cols_new = n_cols // aggreg_size

    heights_new = np.zeros((n_rows_new, n_cols_new))

    # Aggregate neighbouring heights
    for row in range(n_rows_new):
        for col in range(n_cols_new):

            i_idxs = range(row*aggreg_size, (row*aggreg_size)+aggreg_size)
            j_idxs = range(col*aggreg_size, (col*aggreg_size)+aggreg_size)

            if aggreg_method == "min":
                height_new = min(heights[i][j] for i in i_idxs for j in j_idxs)
            if aggreg_method == "max":
                height_new = max(heights[i][j] for i in i_idxs for j in j_idxs)
            if aggreg_method == "avg":
                height_new = sum(heights[i][j] for i in i_idxs for j in j_idxs) / (aggreg_size**2)

            heights_new[row][col] = height_new

    return heights_new

def aggregate(heights, bounds, aggreg_size, aggreg_method):

    heights = aggregate_heights(heights, aggreg_size, aggreg_method)

    transform = rasterio.transform.from_bounds(
        west=bounds.left,
        south=bounds.bottom,
        east=bounds.right,
        north=bounds.top,
        width=heights.shape[0],
        height=heights.shape[1],
    )

    return heights, transform

def save(heights, transform, file_path, crs):
    dataset_out = rasterio.open(
        file_path,
        mode='w',
        driver='GTiff',
        width=heights.shape[0],
        height=heights.shape[1],
        count=1,
        dtype=heights.dtype,
        crs=crs,
        transform=transform
    )
    dataset_out.write(heights, 1)

def aggregate_DEM(file_name, heights_dir):

    file_name_raster = file_name + ".tif"

    # Aggregate and save surface 2x2
    surface_file_path = os.path.join(heights_dir, "surface", "1x1", file_name_raster)
    dataset_surface = rasterio.open(surface_file_path)
    heights_surface_1x1 = dataset_surface.read(1)
    heights_surface_2x2, transform_surface_2x2 = aggregate(heights_surface_1x1, dataset_surface.bounds, 2, AGGREG_METHOD)
    file_path_out_surface = os.path.join(heights_dir, "surface", "2x2", file_name_raster)
    save(heights_surface_2x2, transform_surface_2x2, file_path_out_surface, dataset_surface.crs)
    
    # Aggregate and save terrain 2x2
    terrain_file_path = os.path.join(heights_dir, "terrain", "1x1", file_name_raster)
    dataset_terrain = rasterio.open(terrain_file_path)
    heights_terrain_1x1 = dataset_terrain.read(1)
    heights_terrain_2x2, transform_terrain_2x2 = aggregate(heights_terrain_1x1, dataset_terrain.bounds, 2, AGGREG_METHOD)
    file_path_out_terrain = os.path.join(heights_dir, "terrain", "2x2", file_name_raster)
    save(heights_terrain_2x2, transform_terrain_2x2, file_path_out_terrain, dataset_terrain.crs)
    
    # Aggregate and save buildings 2x2
    buildings_file_path = os.path.join(heights_dir, "buildings", "1x1", file_name_raster)
    dataset_buildings = rasterio.open(buildings_file_path)
    heights_buildings_1x1 = dataset_buildings.read(1)
    heights_buildings_2x2, transform_buildings_2x2 = aggregate(heights_buildings_1x1, dataset_buildings.bounds, 2, AGGREG_METHOD)
    file_path_out_buildings = os.path.join(heights_dir, "buildings", "2x2", file_name_raster)
    save(heights_buildings_2x2, transform_buildings_2x2, file_path_out_buildings, dataset_buildings.crs)
    
    # Aggregate and save trees 2x2
    trees_file_path = os.path.join(heights_dir, "trees", "1x1", file_name_raster)
    dataset_trees = rasterio.open(trees_file_path)
    heights_trees_1x1 = dataset_trees.read(1)
    heights_trees_2x2, transform_trees_2x2 = aggregate(heights_trees_1x1, dataset_trees.bounds, 2, AGGREG_METHOD)
    file_path_out_trees = os.path.join(heights_dir, "trees", "2x2", file_name_raster)
    save(heights_trees_2x2, transform_trees_2x2, file_path_out_trees, dataset_trees.crs)

def main():
    heights_dir = r"D:\data\heights"
    terrain_dir_1x1 = os.path.join(heights_dir, "terrain", "1x1")
    files_in = get_dir_file_names(terrain_dir_1x1)
    for file_name in files_in:
        print(f"{file_name}")
        aggregate_DEM(file_name, heights_dir)

main()