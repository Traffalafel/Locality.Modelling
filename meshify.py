import numpy as np
import pymeshlab

BOTTOM_HEIGHT = -10
NULL_HEIGHT = -1
MIN_HEIGHT_OFFSET = 1

def meshify_surface(heights):

    n_rows, n_cols = heights.shape
    dem_size = n_rows * n_cols

    # Vertices
    vertices = generate_vertices(heights)
    vertices_bottom = generate_bottom_vertices(n_rows, n_cols, BOTTOM_HEIGHT)
    vertices = np.append(vertices, vertices_bottom, axis=0)

    # Create grid indices
    grid_idxs = np.arange((n_rows-1) * (n_cols-1))
    grid_idxs = grid_idxs.reshape((n_rows-1, n_cols-1))
    offsets = np.arange(n_rows-1).reshape((-1, 1))
    offsets = np.tile(offsets, n_cols-1)
    grid_idxs = grid_idxs + offsets
    grid_idxs = grid_idxs.reshape((-1, 1))
    grid_idxs = np.tile(grid_idxs, 4)

    # Grid up faces
    grid_idxs[:,1] += n_cols
    grid_idxs[:,2] += n_cols + 1
    grid_idxs[:,3] += 1

    grid_vertices = vertices[grid_idxs]
    grid_heights = grid_vertices[:,:,2]
    grid_maxes = np.argmax(grid_heights, axis=1)

    grid_nw_se_idxs = np.isin(grid_maxes, [0,2])
    grid_sw_ne_idxs = np.isin(grid_maxes, [1,3])
    grid_nw_se_faces = grid_idxs[grid_nw_se_idxs]
    grid_sw_ne_faces = grid_idxs[grid_sw_ne_idxs]

    top_left_idxs = np.array([3, 1, 0])
    bot_right_idxs = np.array([3, 2, 1])
    top_right_idxs = np.array([3, 2, 0])
    bot_left_idxs = np.array([0, 2, 1])
    
    faces = np.empty((0,3), dtype=np.int32)
    faces = np.append(faces, grid_nw_se_faces[:,top_left_idxs], axis=0)
    faces = np.append(faces, grid_nw_se_faces[:,bot_right_idxs], axis=0)
    faces = np.append(faces, grid_sw_ne_faces[:,top_right_idxs], axis=0)
    faces = np.append(faces, grid_sw_ne_faces[:,bot_left_idxs], axis=0)

    # Top side faces
    faces_top = np.arange(n_cols-1, dtype=np.float32).reshape((-1, 1))
    faces_top = np.tile(faces_top, 4)
    faces_top[:,1] += 1
    faces_top[:,2] += dem_size + 1
    faces_top[:,3] += dem_size
    faces = np.append(faces, faces_top[:,top_left_idxs], axis=0)
    faces = np.append(faces, faces_top[:,bot_right_idxs], axis=0)
    
    # Bottom side faces
    faces_bot = np.arange(n_cols-1, dtype=np.float32)
    faces_bot = faces_bot.reshape((-1, 1))
    faces_bot = np.tile(faces_bot, 4)
    faces_bot[:,0] += dem_size - n_cols
    faces_bot[:,1] += dem_size + n_cols
    faces_bot[:,2] += dem_size + n_cols + 1
    faces_bot[:,3] += dem_size - n_cols + 1
    faces = np.append(faces, faces_bot[:,top_right_idxs], axis=0)
    faces = np.append(faces, faces_bot[:,bot_left_idxs], axis=0)

    side_start = 0
    side_stop = dem_size-2*n_cols+1
    side_step = n_cols
    side_offsets = np.arange(side_start, side_stop, side_step)

    # Left side faces
    faces_left = np.arange(n_rows-1, dtype=np.float32)
    faces_left = faces_left.reshape((-1, 1))
    faces_left = np.tile(faces_left, 4)
    faces_left[:,0] = side_offsets
    faces_left[:,1] += dem_size + 2*n_cols
    faces_left[:,2] += dem_size + 2*n_cols + 1
    faces_left[:,3] = side_offsets + n_cols
    faces = np.append(faces, faces_left[:,top_right_idxs], axis=0)
    faces = np.append(faces, faces_left[:,bot_left_idxs], axis=0)
    
    # Right side faces
    faces_right = np.arange(n_rows-1, dtype=np.float32)
    faces_right = faces_right.reshape((-1, 1))
    faces_right = np.tile(faces_right, 4)
    faces_right[:,0] = side_offsets + n_cols - 1
    faces_right[:,1] = side_offsets + 2*n_cols - 1
    faces_right[:,2] += dem_size + 2*n_cols + n_rows + 1
    faces_right[:,3] += dem_size + 2*n_cols + n_rows
    faces = np.append(faces, faces_right[:,top_right_idxs], axis=0)
    faces = np.append(faces, faces_right[:,bot_left_idxs], axis=0)

    # Bottom face
    idxs_bot = np.array([dem_size, dem_size+n_cols-1, dem_size+2*n_cols-1, dem_size+n_cols])
    idxs_bot = idxs_bot.reshape((-1,4))
    faces = np.append(faces, idxs_bot[:,top_right_idxs], axis=0)
    faces = np.append(faces, idxs_bot[:,bot_left_idxs], axis=0)

    mesh = pymeshlab.Mesh(
        vertex_matrix = vertices,
        face_matrix = faces
    )
    ms = pymeshlab.MeshSet()
    ms.add_mesh(mesh)
    ms.apply_filter("meshing_remove_unreferenced_vertices")

    return ms

def generate_vertices(heights):
    n_rows, n_cols = heights.shape
    xs = np.arange(n_cols)
    ys = np.arange(n_rows)
    xx, yy = np.meshgrid(xs, ys)
    xx = xx.reshape((n_rows, n_cols, -1))
    yy = yy.reshape((n_rows, n_cols, -1))
    vertices = np.append(xx, yy, axis=2)
    vertices = vertices.reshape((-1, 2))
    vertices = vertices.astype(np.float32)
    vertices = np.append(vertices, heights.reshape(-1, 1), axis=1)
    # vertices = vertices[:,[0,2,1]] # flips y/z
    return vertices

# Vertices that are located at the bottom on the edges
def generate_bottom_vertices(n_rows, n_cols, height_bottom):

    vertices = np.empty((0, 2), dtype=np.float32)

    # Top
    xs = np.arange(n_cols, dtype=np.float32).reshape((n_cols, 1))
    ys = np.full((n_cols, 1), 0, dtype=np.float32)
    top = np.append(xs, ys, axis=1)
    vertices = np.append(vertices, top, axis=0)

    # Bottom
    xs = np.arange(n_cols, dtype=np.float32).reshape((n_cols, 1))
    ys = np.full((n_cols, 1), n_rows-1, dtype=np.float32)
    bot = np.append(xs, ys, axis=1)
    vertices = np.append(vertices, bot, axis=0)

    # Left
    xs = np.full((n_rows, 1), 0, dtype=np.float32)
    ys = np.arange(n_rows, dtype=np.float32).reshape((n_rows, 1))
    left = np.append(xs, ys, axis=1)
    vertices = np.append(vertices, left, axis=0)
    
    # Right
    xs = np.full((n_rows, 1), n_cols-1, dtype=np.float32)
    ys = np.arange(n_rows, dtype=np.float32).reshape((n_rows, 1))
    right = np.append(xs, ys, axis=1)
    vertices = np.append(vertices, right, axis=0)

    heights = np.full((vertices.shape[0], 1), height_bottom, dtype=np.float32)
    vertices = np.append(vertices, heights, axis=1)
    return vertices
    