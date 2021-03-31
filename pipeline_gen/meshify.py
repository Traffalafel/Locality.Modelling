import numpy as np
import matplotlib.pyplot as plt
import pymeshlab

BOTTOM_HEIGHT = 0

def generate_vertices(heights, offset_x, offset_y, pixel_size):
    n_rows, n_cols = heights.shape
    xs = np.arange(n_cols)
    ys = np.arange(n_rows)
    xx, yy = np.meshgrid(xs, ys)
    xx = xx.reshape((n_rows, n_cols, -1))
    yy = yy.reshape((n_rows, n_cols, -1))
    vertices = np.append(xx, yy, axis=2)
    vertices = vertices.reshape((-1, 2))
    vertices = vertices.astype(np.float32) * pixel_size
    offset = np.array([offset_x, offset_y]) * pixel_size
    vertices += offset
    vertices = np.append(vertices, heights.reshape(-1, 1), axis=1)
    return vertices

def generate_bottom_vertices(n_rows, n_cols, height_bottom, offset_x, offset_y, pixel_size):

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

    vertices *= pixel_size
    offset = np.array([offset_x, offset_y]) * pixel_size
    vertices += offset
    heights = np.full((vertices.shape[0], 1), height_bottom, dtype=np.float32)
    vertices = np.append(vertices, heights, axis=1)
    return vertices

def generate_terrain_mesh(heights, mask, offset_x, offset_y, pixel_size):

    vertices = generate_vertices(heights, offset_x, offset_y, pixel_size)

    n_rows, n_cols = heights.shape

    idxs = np.arange((n_rows-1) * (n_cols-1))
    idxs = idxs.reshape((n_rows-1, n_cols-1))
    offsets = np.arange(n_rows-1).reshape((-1, 1))
    offsets = np.tile(offsets, n_cols-1)
    idxs = idxs + offsets

    top_left_idxs = np.array([3, 1, 0])
    bot_right_idxs = np.array([3, 2, 1])

    faces = np.empty((0,3), dtype=np.int32)

    idxs_terrain = idxs[mask]
    idxs_terrain = idxs_terrain.reshape(-1, 1)
    idxs_terrain = np.tile(idxs_terrain, 4)
    idxs_terrain[:,1] += n_cols
    idxs_terrain[:,2] += n_cols + 1
    idxs_terrain[:,3] += 1
    faces = np.append(faces, idxs_terrain[:,top_left_idxs], axis=0)
    faces = np.append(faces, idxs_terrain[:,bot_right_idxs], axis=0)

    mesh = pymeshlab.Mesh(
        vertex_matrix = vertices,
        face_matrix = faces
    )
    ms = pymeshlab.MeshSet()

    ms.add_mesh(mesh)

    ms.apply_filter("remove_unreferenced_vertices")

    return ms


def meshify_terrain(heights_terrain, mask_roads, mask_green, mask_water, offset_x, offset_y, pixel_size):

    n_rows, n_cols = heights_terrain.shape

    # TODO: remove
    # remove offsets
    mask_roads = mask_roads[:n_rows-1,:n_cols-1]
    mask_green = mask_green[:n_rows-1,:n_cols-1]
    mask_water = mask_water[:n_rows-1,:n_cols-1]

    # Create terrain mask
    mask_terrain = np.logical_or(mask_roads, mask_green)
    mask_terrain = np.logical_or(mask_terrain, mask_water)
    mask_terrain = np.logical_not(mask_terrain)

    # Make sure masks do not overlap
    mask_water[mask_roads] = False
    mask_green[mask_water] = False
    mask_green[mask_roads] = False
    
    # Create meshes
    ms_terrain = generate_terrain_mesh(heights_terrain, mask_terrain, offset_x, offset_y, pixel_size)
    ms_roads = generate_terrain_mesh(heights_terrain, mask_roads, offset_x, offset_y, pixel_size)
    ms_green = generate_terrain_mesh(heights_terrain, mask_green, offset_x, offset_y, pixel_size)
    ms_water = generate_terrain_mesh(heights_terrain, mask_water, offset_x, offset_y, pixel_size)

    return ms_terrain, ms_roads, ms_green, ms_water

def meshify_elevation(heights, heights_terrain, offset_x, offset_y, pixel_size):

    # Vertices
    vertices = generate_vertices(heights, offset_x, offset_y, pixel_size)
    vertices_terrain = generate_vertices(heights_terrain, offset_x, offset_y, pixel_size)
    vertices = np.append(vertices, vertices_terrain, axis=0)

    n_rows, n_cols = heights.shape
    dem_size = n_rows * n_cols

    # Compute corners
    nw = heights[:n_rows-1,:n_cols-1] != -1
    sw = heights[1:,:n_cols-1] != -1
    ne = heights[:n_rows-1,1:] != -1
    se = heights[1:,1:] != -1

    idxs = np.arange((n_rows-1) * (n_cols-1))
    idxs = idxs.reshape((n_rows-1, n_cols-1))
    offsets = np.arange(n_rows-1).reshape((-1, 1))
    offsets = np.tile(offsets, n_cols-1)
    idxs = idxs + offsets
    
    faces = np.empty((0,3), dtype=np.int32)

    top_left_idxs = np.array([3, 1, 0])
    bot_right_idxs = np.array([3, 2, 1])
    top_right_idxs = np.array([3, 2, 0])
    bot_left_idxs = np.array([0, 2, 1])

    # Grid facing up
    grid_up = np.logical_and(nw, sw)
    grid_up = np.logical_and(grid_up, ne)
    grid_up = np.logical_and(grid_up, se)
    grid_up_faces = idxs[grid_up]
    grid_up_faces = grid_up_faces.reshape(-1, 1)
    grid_up_faces = np.tile(grid_up_faces, 4)
    grid_up_faces[:,1] += n_cols
    grid_up_faces[:,2] += n_cols + 1
    grid_up_faces[:,3] += 1

    grid_up_vertices = vertices[grid_up_faces]
    grid_up_heights = grid_up_vertices[:,:,2]
    grid_up_maxes = np.argmax(grid_up_heights, axis=1)

    grid_up_nw_se_idxs = np.isin(grid_up_maxes, [0,2])
    grid_up_sw_ne_idxs = np.isin(grid_up_maxes, [1,3])
    grid_up_nw_se_faces = grid_up_faces[grid_up_nw_se_idxs]
    grid_up_sw_ne_faces = grid_up_faces[grid_up_sw_ne_idxs]

    faces = np.append(faces, grid_up_nw_se_faces[:,top_left_idxs], axis=0)
    faces = np.append(faces, grid_up_nw_se_faces[:,bot_right_idxs], axis=0)
    faces = np.append(faces, grid_up_sw_ne_faces[:,top_right_idxs], axis=0)
    faces = np.append(faces, grid_up_sw_ne_faces[:,bot_left_idxs], axis=0)

    # Grid facing down
    grid_down_faces = idxs[grid_up].reshape(-1, 1)
    grid_down_faces += dem_size
    grid_down_faces = np.tile(grid_down_faces, 4)
    grid_down_faces[:,1] += 1
    grid_down_faces[:,2] += n_cols + 1
    grid_down_faces[:,3] += n_cols
    faces = np.append(faces, grid_down_faces[:,top_left_idxs], axis=0)
    faces = np.append(faces, grid_down_faces[:,bot_right_idxs], axis=0)

    # horizontal lines facing south
    horizontal_s = np.logical_and(nw, ne)
    horizontal_s = np.logical_and(horizontal_s, np.logical_not(sw))
    horizontal_s = np.logical_and(horizontal_s, np.logical_not(se))
    horizontal_s_faces = idxs[horizontal_s].reshape(-1, 1)
    horizontal_s_faces = np.tile(horizontal_s_faces, 4)
    horizontal_s_faces[:,1] += dem_size
    horizontal_s_faces[:,2] += dem_size + 1
    horizontal_s_faces[:,3] += 1
    faces = np.append(faces, horizontal_s_faces[:,top_left_idxs], axis=0)
    faces = np.append(faces, horizontal_s_faces[:,bot_right_idxs], axis=0)

    # horizontal lines facing north
    horizontal_n = np.logical_and(sw, se)
    horizontal_n = np.logical_and(horizontal_n, np.logical_not(nw))
    horizontal_n = np.logical_and(horizontal_n, np.logical_not(ne))
    horizontal_n_faces = idxs[horizontal_n].reshape(-1, 1)
    horizontal_n_faces += n_cols
    horizontal_n_faces = np.tile(horizontal_n_faces, 4)
    horizontal_n_faces[:,1] += 1
    horizontal_n_faces[:,2] += dem_size + 1
    horizontal_n_faces[:,3] += dem_size
    faces = np.append(faces, horizontal_n_faces[:,top_left_idxs], axis=0)
    faces = np.append(faces, horizontal_n_faces[:,bot_right_idxs], axis=0)

    # vertical lines facing east
    vertical_e = np.logical_and(nw, sw)
    vertical_e = np.logical_and(vertical_e, np.logical_not(ne))
    vertical_e = np.logical_and(vertical_e, np.logical_not(se))
    vertical_e_faces = idxs[vertical_e].reshape(-1, 1)
    vertical_e_faces = np.tile(vertical_e_faces, 4)
    vertical_e_faces[:,1] += n_cols
    vertical_e_faces[:,2] += dem_size + n_cols
    vertical_e_faces[:,3] += dem_size
    faces = np.append(faces, vertical_e_faces[:,top_left_idxs], axis=0)
    faces = np.append(faces, vertical_e_faces[:,bot_right_idxs], axis=0)
    
    # vertical lines facing west
    vertical_w = np.logical_and(ne, se)
    vertical_w = np.logical_and(vertical_w, np.logical_not(nw))
    vertical_w = np.logical_and(vertical_w, np.logical_not(sw))
    vertical_w_faces = idxs[vertical_w].reshape(-1, 1)
    vertical_w_faces += 1
    vertical_w_faces = np.tile(vertical_w_faces, 4)
    vertical_w_faces[:,1] += dem_size
    vertical_w_faces[:,2] += dem_size + n_cols
    vertical_w_faces[:,3] += n_cols
    faces = np.append(faces, vertical_w_faces[:,top_left_idxs], axis=0)
    faces = np.append(faces, vertical_w_faces[:,bot_right_idxs], axis=0)

    # Index arrays for corners
    top_idxs = np.array([0, 1, 4])
    bot_idxs = np.array([3, 2, 5])
    side_idxs_1 = np.array([1, 2, 4])
    side_idxs_2 = np.array([2, 3, 4])

    # SW-NE-NW
    sw_ne_nw = np.logical_and(sw, ne)
    sw_ne_nw = np.logical_and(sw_ne_nw, nw)
    sw_ne_nw = np.logical_and(sw_ne_nw, np.logical_not(se))
    sw_ne_nw_faces = idxs[sw_ne_nw].reshape(-1, 1)
    sw_ne_nw_faces = np.tile(sw_ne_nw_faces, 6)
    sw_ne_nw_faces[:,1] += n_cols
    sw_ne_nw_faces[:,2] += dem_size + n_cols
    sw_ne_nw_faces[:,3] += dem_size + 1
    sw_ne_nw_faces[:,4] += 1
    sw_ne_nw_faces[:,5] += dem_size
    faces = np.append(faces, sw_ne_nw_faces[:,top_idxs], axis=0)
    faces = np.append(faces, sw_ne_nw_faces[:,bot_idxs], axis=0)
    faces = np.append(faces, sw_ne_nw_faces[:,side_idxs_1], axis=0)
    faces = np.append(faces, sw_ne_nw_faces[:,side_idxs_2], axis=0)

    # SW-NE-SE
    sw_ne_se = np.logical_and(sw, ne)
    sw_ne_se = np.logical_and(sw_ne_se, se)
    sw_ne_se = np.logical_and(sw_ne_se, np.logical_not(nw))
    sw_ne_se_faces = idxs[sw_ne_se].reshape(-1, 1)
    sw_ne_se_faces = np.tile(sw_ne_se_faces, 6)
    sw_ne_se_faces[:,0] += n_cols + 1
    sw_ne_se_faces[:,1] += 1
    sw_ne_se_faces[:,2] += dem_size + 1
    sw_ne_se_faces[:,3] += dem_size + n_cols
    sw_ne_se_faces[:,4] += n_cols
    sw_ne_se_faces[:,5] += dem_size + n_cols + 1
    faces = np.append(faces, sw_ne_se_faces[:,top_idxs], axis=0)
    faces = np.append(faces, sw_ne_se_faces[:,bot_idxs], axis=0)
    faces = np.append(faces, sw_ne_se_faces[:,side_idxs_1], axis=0)
    faces = np.append(faces, sw_ne_se_faces[:,side_idxs_2], axis=0)

    # NW-SE-NE
    nw_se_ne = np.logical_and(nw, se)
    nw_se_ne = np.logical_and(nw_se_ne, ne)
    nw_se_ne = np.logical_and(nw_se_ne, np.logical_not(sw))
    nw_se_ne_faces = idxs[nw_se_ne].reshape(-1, 1)
    nw_se_ne_faces = np.tile(nw_se_ne_faces, 6)
    nw_se_ne_faces[:,0] += 1
    nw_se_ne_faces[:,2] += dem_size
    nw_se_ne_faces[:,3] += dem_size + n_cols + 1
    nw_se_ne_faces[:,4] += n_cols + 1
    nw_se_ne_faces[:,5] += dem_size + 1
    faces = np.append(faces, nw_se_ne_faces[:,top_idxs], axis=0)
    faces = np.append(faces, nw_se_ne_faces[:,bot_idxs], axis=0)
    faces = np.append(faces, nw_se_ne_faces[:,side_idxs_1], axis=0)
    faces = np.append(faces, nw_se_ne_faces[:,side_idxs_2], axis=0)

    # NW-SE-SW
    nw_se_sw = np.logical_and(nw, se)
    nw_se_sw = np.logical_and(nw_se_sw, sw)
    nw_se_sw = np.logical_and(nw_se_sw, np.logical_not(ne))
    nw_se_sw_faces = idxs[nw_se_sw].reshape(-1, 1)
    nw_se_sw_faces = np.tile(nw_se_sw_faces, 6)
    nw_se_sw_faces[:,0] += n_cols
    nw_se_sw_faces[:,1] += n_cols + 1
    nw_se_sw_faces[:,2] += dem_size + n_cols + 1
    nw_se_sw_faces[:,3] += dem_size
    nw_se_sw_faces[:,5] += dem_size + n_cols
    faces = np.append(faces, nw_se_sw_faces[:,top_idxs], axis=0)
    faces = np.append(faces, nw_se_sw_faces[:,bot_idxs], axis=0)
    faces = np.append(faces, nw_se_sw_faces[:,side_idxs_1], axis=0)
    faces = np.append(faces, nw_se_sw_faces[:,side_idxs_2], axis=0)

    mesh = pymeshlab.Mesh(
        vertex_matrix = vertices,
        face_matrix = faces
    )
    ms = pymeshlab.MeshSet()
    ms.add_mesh(mesh)

    ms.apply_filter("remove_unreferenced_vertices")

    return ms

def meshify_surface(heights, offset_x, offset_y, pixel_size):

    n_rows, n_cols = heights.shape
    dem_size = n_rows * n_cols

    # Vertices
    vertices = generate_vertices(heights, offset_x, offset_y, pixel_size)
    vertices_bottom = generate_bottom_vertices(n_rows, n_cols, BOTTOM_HEIGHT, offset_x, offset_y, pixel_size)
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

    # ms.apply_filter("remove_unreferenced_vertices")

    return ms
