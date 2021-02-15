import numpy as np
import rasterio.transform

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