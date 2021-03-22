import numpy as np

def interpolate_points(start, end, count):
    slope = (end - start) / count
    return [start+slope*i for i in range(count)]

def interpolate(buildings, mask, limit_v=None, limit_h=None):
    interpolate_x(buildings, mask, limit_v, limit_h)
    interpolate_y(buildings, mask, limit_v, limit_h)

def interpolate_x(buildings, mask, limit_v, limit_h):

    n_rows, n_cols = buildings.shape

    for row in range(n_rows):

        interpolate = True
        interpolate_count = 0
        interpolate_start = None

        for col in range(n_cols):

            is_hit = buildings[row,col] != -1
            is_masked =  mask[row,col]
            
            if is_masked:
                interpolate = False
                interpolate_count = 0
                continue

            if limit_h is not None and interpolate_count > limit_h:
                interpolate = False
                interpolate_count = 0
                continue

            if is_hit:

                if interpolate and interpolate_count > 0:
                    # Interpolate
                    if interpolate_start is None:
                        interpolate_start = 0
                        val_start = buildings[row,col]
                    else:
                        val_start = buildings[row,interpolate_start]
                    val_end = buildings[row,col]

                    if limit_v is not None and abs(val_end - val_start) > limit_v:
                        interpolate = False
                        interpolate_count = 0
                        continue

                    new_vals = interpolate_points(val_start, val_end, interpolate_count+1)
                    for idx, val in enumerate(new_vals):
                        buildings[row,idx+interpolate_start] = val

                interpolate = True
                interpolate_count = 0
                interpolate_start = col
                continue

            # Not building nor mask
            interpolate_count += 1

def interpolate_y(buildings, mask, limit_v, limit_h):

    n_rows, n_cols = buildings.shape

    for col in range(n_cols):

        interpolate = True
        interpolate_count = 0
        interpolate_start = None

        for row in range(n_rows):

            is_hit = buildings[row,col] != -1
            is_masked =  mask[row,col]
            
            if is_masked:
                interpolate = False
                interpolate_count = 0
                continue

            if limit_h is not None and interpolate_count > limit_h:
                interpolate = False
                interpolate_count = 0
                continue

            if is_hit:

                if interpolate and interpolate_count > 0:
                    # Interpolate
                    if interpolate_start is None:
                        interpolate_start = 0
                        val_start = buildings[row,col]
                    else:
                        val_start = buildings[interpolate_start,col]
                    val_end = buildings[row,col]

                    if limit_v is not None and abs(val_end - val_start) > limit_v:
                        interpolate = False
                        interpolate_count = 0
                        continue

                    new_vals = interpolate_points(val_start, val_end, interpolate_count+1)
                    for idx, val in enumerate(new_vals):
                        buildings[idx+interpolate_start,col] = val

                interpolate = True
                interpolate_count = 0
                interpolate_start = row
                continue

            # Not building nor mask
            interpolate_count += 1
