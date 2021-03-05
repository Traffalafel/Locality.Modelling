import numpy as np

def interpolate_points(start, end, count):
    slope = (end - start) / count
    return [start+slope*i for i in range(count)]

def interpolate_x(buildings, ground, limit):

    n_rows, n_cols = buildings.shape

    for row in range(n_rows):

        interpolate = True
        interpolate_count = 0
        interpolate_start = None

        for col in range(n_cols):

            is_building = buildings[row,col] != -1
            is_ground =  ground[row,col] != -1

            if is_building:

                if interpolate and interpolate_count > 0:
                    # Interpolate
                    if interpolate_start is None:
                        interpolate_start = 0
                        val_start = buildings[row,col]
                    else:
                        val_start = buildings[row,interpolate_start]
                    val_end = buildings[row,col]
                    new_vals = interpolate_points(val_start, val_end, interpolate_count+1)
                    for idx, val in enumerate(new_vals):
                        buildings[row,idx+interpolate_start] = val

                interpolate = True
                interpolate_count = 0
                interpolate_start = col
                continue

            if is_ground:
                interpolate = False
                interpolate_count = 0
                continue

            # Not building nor ground
            interpolate_count += 1

            if interpolate_count > limit:
                interpolate = False

def interpolate_y(buildings, ground, limit):

    n_rows, n_cols = buildings.shape

    for col in range(n_cols):

        interpolate = True
        interpolate_count = 0
        interpolate_start = None

        for row in range(n_rows):

            is_building = buildings[row,col] != -1
            is_ground =  ground[row,col] != -1

            if is_building:

                if interpolate and interpolate_count > 0:
                    # Interpolate
                    if interpolate_start is None:
                        interpolate_start = 0
                        val_start = buildings[row,col]
                    else:
                        val_start = buildings[interpolate_start,col]
                    val_end = buildings[row,col]
                    new_vals = interpolate_points(val_start, val_end, interpolate_count+1)
                    for idx, val in enumerate(new_vals):
                        buildings[idx+interpolate_start,col] = val

                interpolate = True
                interpolate_count = 0
                interpolate_start = row
                continue

            if is_ground:
                interpolate = False
                interpolate_count = 0
                continue

            # Not building nor ground
            interpolate_count += 1

            if interpolate_count > limit:
                interpolate = False

# def main():
    
#     buildings = np.array([
#         [-1, 100, 2],
#         [-1, 1, 100],
#         [-1, 1, 2],
#     ], dtype=np.float32)
#     ground = np.array([
#         [-1, -1, -1],
#         [-1, -1, -1],
#         [1, -1, -1],
#     ], dtype=np.float32)

#     interpolate_x(buildings, ground)

#     print(buildings)

# main()