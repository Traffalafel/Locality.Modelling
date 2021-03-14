import numpy as np
import pylas

def create_heights(file_path, classes, min_bucket_size, step_size, dem_size):
    las = pylas.read(file_path)
    las.points = las.points[np.isin(las.classification, classes)]

    # Get parameters
    x_scale = las.header.x_scale
    x_offset = las.header.x_offset
    x_min = las.header.x_min
    y_scale = las.header.y_scale
    y_offset = las.header.y_offset
    y_min = las.header.y_min
    z_scale = las.header.z_scale
    z_offset = las.header.z_offset
    
    # Compute coordinates
    points = np.array([[p[0], p[1], p[2]] for p in las.points])
    scale = np.array([x_scale, y_scale, z_scale])
    offset = np.array([x_offset, y_offset, z_offset])
    points = (points * scale) + offset
    mins = np.array([x_min, y_min])
    idxs_2d = points[:,:2]
    idxs_2d = ((idxs_2d - mins) // step_size).astype(np.int32)
    idxs_1d = idxs_2d[:,0] * dem_size + idxs_2d[:,1]
    z_heights = points[:,2]

    # Compute sums
    heights = np.zeros(dem_size**2, dtype=np.float32)
    np.add.at(heights, idxs_1d, z_heights)
    heights = heights.reshape((dem_size, dem_size))
    
    # Compute counts
    counts = np.zeros(dem_size**2, dtype=np.float32)
    np.add.at(counts, idxs_1d, 1)
    counts[counts == 0] = 1
    counts = counts.reshape((dem_size, dem_size))

    averages = heights / counts
    averages[averages == 0] = -1
    return averages