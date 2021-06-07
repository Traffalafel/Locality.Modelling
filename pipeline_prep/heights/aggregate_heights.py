import numpy as np
import rasterio
import rasterio.transform
import os
import sys

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

def aggregate_DEMs(file_name, heights_dir_path):

    heights_dir_in_path = os.path.join(heights_dir_path, "1x1")
    heights_dir_out_path = os.path.join(heights_dir_path, "2x2")

    file_name_tif = file_name + ".tif"
    file_in_path = os.path.join(heights_dir_in_path, file_name_tif)
    dataset = rasterio.open(file_in_path)
    heights_1x1 = dataset.read(1)

    heights_2x2, transform_2x2 = aggregate(heights_1x1, dataset.bounds, 2, AGGREG_METHOD)

    file_path_out = os.path.join(heights_dir_out_path, file_name_tif)
    save(heights_2x2, transform_2x2, file_path_out, dataset.crs)
    
def main():
    
    n_args = len(sys.argv)
    if n_args != 3:
        print(f"Args: <file_name> <heights_dir_path>")
        
    file_name = sys.argv[1]
    heights_dir_path = sys.argv[1]
    aggregate_DEMs(file_name, heights_dir_path)

main()