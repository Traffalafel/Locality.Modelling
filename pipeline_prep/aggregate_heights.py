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

def generate_2d_idxs(n_rows, n_cols, aggreg_size):

    xs = np.arange(0, n_cols*aggreg_size, aggreg_size)
    ys = np.arange(0, n_rows*aggreg_size, aggreg_size)
    xx, yy = np.meshgrid(xs, ys)
    xx = xx.reshape((n_rows, n_cols, -1))
    yy = yy.reshape((n_rows, n_cols, -1))
    idxs = np.append(yy, xx, axis=2)

    return idxs

def aggregate_heights(heights, aggreg_size, aggreg_method):

    n_rows, n_cols = heights.shape
    n_rows_new = n_rows // aggreg_size
    n_cols_new = n_cols // aggreg_size

    idxs = generate_2d_idxs(n_rows_new, n_cols_new, aggreg_size)
    idxs = np.tile(idxs, 4)
    idxs = idxs.reshape((-1, 4, 2))
    idxs[:,1,0] += 1
    idxs[:,2,1] += 1
    idxs[:,3,0] += 1
    idxs[:,3,1] += 1
    idxs = idxs.reshape((-1, 2))

    heights_new = heights[idxs[:,0], idxs[:,1]]
    heights_new = heights_new.reshape((-1, 4))
    heights_new = np.amax(heights_new, axis=1)
    heights_new = heights_new.reshape((n_rows_new, n_cols_new))

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

def aggregate_DEMs(dir_in_path, dir_out_path):

    file_names = get_dir_file_names(dir_in_path)

    for file_name in file_names:

        file_name_raster = file_name + ".tif"

        file_in_path = os.path.join(dir_in_path, file_name_raster)
        dataset = rasterio.open(file_in_path)
        heights_1x1 = dataset.read(1)
        heights_2x2, transform_2x2 = aggregate(heights_1x1, dataset.bounds, 2, AGGREG_METHOD)
        file_path_out = os.path.join(dir_out_path, file_name_raster)
        save(heights_2x2, transform_2x2, file_path_out, dataset.crs)

        print(f"{file_in_path}")
    
def main():
    
    heights_dir = r"D:\data\heights"

    buildings_dir_1x1 = os.path.join(heights_dir, "buildings", "1x1")
    buildings_dir_2x2 = os.path.join(heights_dir, "buildings", "2x2")
    aggregate_DEMs(buildings_dir_1x1, buildings_dir_2x2)

    terrain_dir_1x1 = os.path.join(heights_dir, "terrain", "1x1")
    terrain_dir_2x2 = os.path.join(heights_dir, "terrain", "2x2")
    aggregate_DEMs(terrain_dir_1x1, terrain_dir_2x2)
    
    surface_dir_1x1 = os.path.join(heights_dir, "surface", "1x1")
    surface_dir_2x2 = os.path.join(heights_dir, "surface", "2x2")
    aggregate_DEMs(surface_dir_1x1, surface_dir_2x2)

    trees_dir_1x1 = os.path.join(heights_dir, "trees", "1x1")
    trees_dir_2x2 = os.path.join(heights_dir, "trees", "2x2")
    aggregate_DEMs(trees_dir_1x1, trees_dir_2x2)

main()