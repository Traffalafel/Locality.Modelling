import numpy as np
import matplotlib.pyplot as plt
import pymeshlab
from locality import constants
import sys

BOTTOM_HEIGHT_DISTANCE = 3
INTERMEDIATE_HEIGHT_DISTANCE = 2
MIN_NULL_HEIGHT = -1000000
VERTICES_SCALE_FACTOR = 0.01

def get_intermediate_heights(heights):
    intermediate = heights - INTERMEDIATE_HEIGHT_DISTANCE
    intermediate[intermediate == constants.NULL_HEIGHT - INTERMEDIATE_HEIGHT_DISTANCE] = constants.NULL_HEIGHT
    return intermediate

def meshify_color(heights_terrain, heights_buildings, heights_trees, mask_roads, mask_green, mask_water, offset_x, offset_y, pixel_size, terrain_min_height_global):

    n_rows, n_cols = heights_terrain.shape

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

    heights_roads = np.full((n_rows, n_cols), constants.NULL_HEIGHT, dtype=np.float32)
    mask_roads = expand_mask(mask_roads)
    heights_roads[mask_roads] = heights_terrain[mask_roads]
    heights_roads_intermediate = get_intermediate_heights(heights_roads)
    ms_roads = meshify_terrain_features(heights_roads, heights_roads_intermediate, offset_x, offset_y, pixel_size)

    heights_green = np.full((n_rows, n_cols), constants.NULL_HEIGHT, dtype=np.float32)
    mask_green = expand_mask(mask_green)
    heights_green[mask_green] = heights_terrain[mask_green]
    heights_green_intermediate = get_intermediate_heights(heights_green)
    ms_green = meshify_terrain_features(heights_green, heights_green_intermediate, offset_x, offset_y, pixel_size)

    heights_water = np.full((n_rows, n_cols), constants.NULL_HEIGHT, dtype=np.float32)
    mask_water = expand_mask(mask_water)
    heights_water[mask_water] = heights_terrain[mask_water]
    heights_water_intermediate = get_intermediate_heights(heights_water)
    ms_water = meshify_terrain_features(heights_water, heights_water_intermediate, offset_x, offset_y, pixel_size)

    heights_terrain_expanded = np.full((n_rows, n_cols), constants.NULL_HEIGHT, dtype=np.float32)
    mask_terrain_expanded = expand_mask(mask_terrain)
    heights_terrain_expanded[mask_terrain_expanded] = heights_terrain[mask_terrain_expanded]

    heights_roads_intermediate[heights_roads_intermediate == constants.NULL_HEIGHT] = MIN_NULL_HEIGHT
    heights_green_intermediate[heights_green_intermediate == constants.NULL_HEIGHT] = MIN_NULL_HEIGHT
    heights_water_intermediate[heights_water_intermediate == constants.NULL_HEIGHT] = MIN_NULL_HEIGHT
    heights_terrain_intermediate = np.maximum(heights_roads_intermediate, heights_green_intermediate)
    heights_terrain_intermediate = np.maximum(heights_terrain_intermediate, heights_water_intermediate)
    heights_terrain_intermediate[heights_terrain_intermediate == MIN_NULL_HEIGHT] = constants.NULL_HEIGHT

    bottom_height = terrain_min_height_global - BOTTOM_HEIGHT_DISTANCE
    ms_terrain = meshify_terrain(heights_terrain_expanded, heights_terrain_intermediate, mask_terrain, offset_x, offset_y, pixel_size, bottom_height)

    ms_buildings = meshify_buildings_trees(heights_buildings, heights_terrain, offset_x, offset_y, pixel_size)
    ms_trees = meshify_buildings_trees(heights_trees, heights_terrain, offset_x, offset_y, pixel_size)

    return ms_terrain, ms_roads, ms_green, ms_water, ms_buildings, ms_trees

def meshify_white(heights, offset_x, offset_y, pixel_size):

    n_rows, n_cols = heights.shape
    dem_size = n_rows * n_cols

    # Vertices
    vertices = generate_vertices(heights, offset_x, offset_y, pixel_size)
    vertices_bottom = generate_bottom_vertices(n_rows, n_cols, offset_x, offset_y, pixel_size)
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
    ms.apply_filter("remove_unreferenced_vertices")

    return ms

def meshify_terrain(heights_top, intermediate_bottom_heights, mask, offset_x, offset_y, pixel_size, bottom_height):

    n_rows, n_cols = heights_top.shape
    dem_size = n_rows * n_cols

    vertices_top = generate_vertices(heights_top, offset_x, offset_y, pixel_size)
    vertices_bot = generate_vertices(intermediate_bottom_heights, offset_x, offset_y, pixel_size)
    vertices = np.append(vertices_top, vertices_bot, axis=0)
    vertices_bottom_sides = generate_bottom_vertices(n_rows, n_cols, offset_x, offset_y, pixel_size, bottom_height)
    vertices = np.append(vertices, vertices_bottom_sides, axis=0)

    idxs = generate_idxs(n_rows, n_cols)
    faces = np.empty((0,3), dtype=np.int32)

    # Compute corners
    nw = heights_top[:n_rows-1,:n_cols-1] != constants.NULL_HEIGHT
    sw = heights_top[1:,:n_cols-1] != constants.NULL_HEIGHT
    ne = heights_top[:n_rows-1,1:] != constants.NULL_HEIGHT
    se = heights_top[1:,1:] != constants.NULL_HEIGHT

    top_left_idxs = np.array([3, 1, 0])
    bot_right_idxs = np.array([3, 2, 1])
    top_right_idxs = np.array([3, 2, 0])
    bot_left_idxs = np.array([0, 2, 1])

    # Top
    idxs_terrain = idxs[mask]
    idxs_terrain = idxs_terrain.reshape(-1, 1)
    idxs_terrain = np.tile(idxs_terrain, 4)
    idxs_terrain[:,1] += n_cols
    idxs_terrain[:,2] += n_cols + 1
    idxs_terrain[:,3] += 1
    faces = np.append(faces, idxs_terrain[:,top_left_idxs], axis=0)
    faces = np.append(faces, idxs_terrain[:,bot_right_idxs], axis=0)

    # horizontal lines facing south
    horizontal_s = np.logical_and(nw, ne)
    horizontal_bottom = np.logical_or(np.logical_not(sw), np.logical_not(se))
    horizontal_s = np.logical_and(horizontal_s, horizontal_bottom)
    horizontal_s_faces = idxs[horizontal_s].reshape(-1, 1)
    horizontal_s_faces = np.tile(horizontal_s_faces, 4)
    horizontal_s_faces[:,1] += dem_size
    horizontal_s_faces[:,2] += dem_size + 1
    horizontal_s_faces[:,3] += 1
    faces = np.append(faces, horizontal_s_faces[:,top_left_idxs], axis=0)
    faces = np.append(faces, horizontal_s_faces[:,bot_right_idxs], axis=0)

    # horizontal lines facing north
    horizontal_n = np.logical_and(sw, se)
    horizontal_top = np.logical_or(np.logical_not(nw), np.logical_not(ne))
    horizontal_n = np.logical_and(horizontal_n, horizontal_top)
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
    vertical_right = np.logical_or(np.logical_not(ne), np.logical_not(se))
    vertical_e = np.logical_and(vertical_e, vertical_right)
    vertical_e_faces = idxs[vertical_e].reshape(-1, 1)
    vertical_e_faces = np.tile(vertical_e_faces, 4)
    vertical_e_faces[:,1] += n_cols
    vertical_e_faces[:,2] += dem_size + n_cols
    vertical_e_faces[:,3] += dem_size
    faces = np.append(faces, vertical_e_faces[:,top_left_idxs], axis=0)
    faces = np.append(faces, vertical_e_faces[:,bot_right_idxs], axis=0)
    
    # vertical lines facing west
    vertical_w = np.logical_and(ne, se)
    vertical_left = np.logical_or(np.logical_not(nw), np.logical_not(sw))
    vertical_w = np.logical_and(vertical_w, vertical_left)
    vertical_w_faces = idxs[vertical_w].reshape(-1, 1)
    vertical_w_faces += 1
    vertical_w_faces = np.tile(vertical_w_faces, 4)
    vertical_w_faces[:,1] += dem_size
    vertical_w_faces[:,2] += dem_size + n_cols
    vertical_w_faces[:,3] += n_cols
    faces = np.append(faces, vertical_w_faces[:,top_left_idxs], axis=0)
    faces = np.append(faces, vertical_w_faces[:,bot_right_idxs], axis=0)

    # Facing upwards - bottom
    up_bottom = np.logical_or(np.logical_not(sw), np.logical_not(nw))
    up_bottom = np.logical_or(up_bottom, np.logical_not(se))
    up_bottom = np.logical_or(up_bottom, np.logical_not(ne))
    up_bottom_faces = idxs[up_bottom].reshape(-1, 1)
    up_bottom_faces = np.tile(up_bottom_faces, 4)
    up_bottom_faces[:,0] += dem_size
    up_bottom_faces[:,1] += dem_size + n_cols
    up_bottom_faces[:,2] += dem_size + n_cols + 1
    up_bottom_faces[:,3] += dem_size + 1
    faces = np.append(faces, up_bottom_faces[:,top_left_idxs], axis=0)
    faces = np.append(faces, up_bottom_faces[:,bot_right_idxs], axis=0)

    # Sideways face - north, bottom
    left = heights_top[0,:n_cols-1] != constants.NULL_HEIGHT
    right = heights_top[0,1:] != constants.NULL_HEIGHT
    faces_top_bottom_idxs = np.logical_or(np.logical_not(left), np.logical_not(right))
    faces_top = np.arange(n_cols-1, dtype=np.float32).reshape((-1, 1))
    faces_top = faces_top[faces_top_bottom_idxs]
    faces_top = np.tile(faces_top, 4)
    faces_top[:,0] += dem_size
    faces_top[:,1] += dem_size + 1
    faces_top[:,2] += 2*dem_size + 1
    faces_top[:,3] += 2*dem_size
    faces = np.append(faces, faces_top[:,top_left_idxs], axis=0)
    faces = np.append(faces, faces_top[:,bot_right_idxs], axis=0)
    # Sideways face - north, top
    left = heights_top[0,:n_cols-1] != constants.NULL_HEIGHT
    right = heights_top[0,1:] != constants.NULL_HEIGHT
    faces_top_bottom_idxs = np.logical_and(left, right)
    faces_top = np.arange(n_cols-1, dtype=np.float32).reshape((-1, 1))
    faces_top = faces_top[faces_top_bottom_idxs]
    faces_top = np.tile(faces_top, 4)
    faces_top[:,0] += 0
    faces_top[:,1] += 1
    faces_top[:,2] += 2*dem_size + 1
    faces_top[:,3] += 2*dem_size
    faces = np.append(faces, faces_top[:,top_left_idxs], axis=0)
    faces = np.append(faces, faces_top[:,bot_right_idxs], axis=0)

    # Sideways face - south, bottom
    left = heights_top[n_rows-1,:n_cols-1] != constants.NULL_HEIGHT
    right = heights_top[n_rows-1,1:] != constants.NULL_HEIGHT
    faces_bot_bottom_idxs = np.logical_or(np.logical_not(left), np.logical_not(right))
    faces_bot = np.arange(n_cols-1, dtype=np.float32).reshape((-1, 1))
    faces_bot = faces_bot[faces_bot_bottom_idxs]
    faces_bot = np.tile(faces_bot, 4)
    faces_bot[:,0] += 2*dem_size - n_cols
    faces_bot[:,1] += 2*dem_size + n_cols
    faces_bot[:,2] += 2*dem_size + n_cols + 1
    faces_bot[:,3] += 2*dem_size - n_cols + 1
    faces = np.append(faces, faces_bot[:,top_left_idxs], axis=0)
    faces = np.append(faces, faces_bot[:,bot_right_idxs], axis=0)
    # Sideways face - south, top
    left = heights_top[n_rows-1,:n_cols-1] != constants.NULL_HEIGHT
    right = heights_top[n_rows-1,1:] != constants.NULL_HEIGHT
    faces_bot_bottom_idxs = np.logical_and(left, right)
    faces_bot = np.arange(n_cols-1, dtype=np.float32).reshape((-1, 1))
    faces_bot = faces_bot[faces_bot_bottom_idxs]
    faces_bot = np.tile(faces_bot, 4)
    faces_bot[:,0] += dem_size - n_cols
    faces_bot[:,1] += 2*dem_size + n_cols
    faces_bot[:,2] += 2*dem_size + n_cols + 1
    faces_bot[:,3] += dem_size - n_cols + 1
    faces = np.append(faces, faces_bot[:,top_left_idxs], axis=0)
    faces = np.append(faces, faces_bot[:,bot_right_idxs], axis=0)

    offsets_sides = np.arange(0, dem_size-n_cols-n_rows, n_cols-1, dtype=np.float32)

    # Sideways face - left, bottom
    top = heights_top[:n_rows-1,0] != constants.NULL_HEIGHT
    bot = heights_top[1:,0] != constants.NULL_HEIGHT
    faces_left_bottom_idxs = np.logical_or(np.logical_not(top), np.logical_not(bot))
    faces_left = np.arange(n_rows-1, dtype=np.float32)
    faces_left = faces_left[faces_left_bottom_idxs]
    faces_left = faces_left.reshape((-1, 1))
    faces_left = np.tile(faces_left, 4)
    offsets_left = offsets_sides[faces_left_bottom_idxs]
    faces_left[:,0] += offsets_left + dem_size
    faces_left[:,1] += 2*dem_size + 2*n_cols
    faces_left[:,2] += 2*dem_size + 2*n_cols + 1
    faces_left[:,3] += offsets_left + dem_size + n_cols
    faces = np.append(faces, faces_left[:,top_right_idxs], axis=0)
    faces = np.append(faces, faces_left[:,bot_left_idxs], axis=0)
    # Sideways face - left, top
    top = heights_top[:n_rows-1,0] != constants.NULL_HEIGHT
    bot = heights_top[1:,0] != constants.NULL_HEIGHT
    faces_left_top_idxs = np.logical_and(top, bot)
    faces_left = np.arange(n_rows-1, dtype=np.float32)
    faces_left = faces_left[faces_left_top_idxs]
    faces_left = faces_left.reshape((-1, 1))
    faces_left = np.tile(faces_left, 4)
    offsets_left = offsets_sides[faces_left_top_idxs]
    faces_left[:,0] += offsets_left
    faces_left[:,1] += 2*dem_size + 2*n_cols
    faces_left[:,2] += 2*dem_size + 2*n_cols + 1
    faces_left[:,3] += offsets_left + n_cols
    faces = np.append(faces, faces_left[:,top_right_idxs], axis=0)
    faces = np.append(faces, faces_left[:,bot_left_idxs], axis=0)

    # Sideways face - right, bottom
    top = heights_top[:n_rows-1,n_cols-1] != constants.NULL_HEIGHT
    bot = heights_top[1:,n_cols-1] != constants.NULL_HEIGHT
    faces_right_bottom_idxs = np.logical_or(np.logical_not(top), np.logical_not(bot))
    faces_right = np.arange(n_rows-1, dtype=np.float32)
    faces_right = faces_right[faces_right_bottom_idxs]
    faces_right = faces_right.reshape((-1, 1))
    faces_right = np.tile(faces_right, 4)
    offsets_left = offsets_sides[faces_right_bottom_idxs]
    faces_right[:,0] += offsets_left + dem_size + n_cols - 1
    faces_right[:,1] += offsets_left + dem_size + 2*n_cols - 1
    faces_right[:,2] += 2*dem_size + 2*n_cols + n_rows + 1
    faces_right[:,3] += 2*dem_size + 2*n_cols + n_rows
    faces = np.append(faces, faces_right[:,top_right_idxs], axis=0)
    faces = np.append(faces, faces_right[:,bot_left_idxs], axis=0)
    # Sideways face - right, top
    top = heights_top[:n_rows-1,n_cols-1] != constants.NULL_HEIGHT
    bot = heights_top[1:,n_cols-1] != constants.NULL_HEIGHT
    faces_right_top_idxs = np.logical_and(top, bot)
    faces_right = np.arange(n_rows-1, dtype=np.float32)
    faces_right = faces_right[faces_right_top_idxs]
    faces_right = faces_right.reshape((-1, 1))
    faces_right = np.tile(faces_right, 4)
    offsets_left = offsets_sides[faces_right_top_idxs]
    faces_right[:,0] += offsets_left + n_cols - 1
    faces_right[:,1] += offsets_left + 2*n_cols - 1
    faces_right[:,2] += 2*dem_size + 2*n_cols + n_rows + 1
    faces_right[:,3] += 2*dem_size + 2*n_cols + n_rows
    faces = np.append(faces, faces_right[:,top_right_idxs], axis=0)
    faces = np.append(faces, faces_right[:,bot_left_idxs], axis=0)

    # Bottom face
    idxs_bot = np.array([2*dem_size, 2*dem_size+n_cols-1, 2*dem_size+2*n_cols-1, 2*dem_size+n_cols])
    idxs_bot = idxs_bot.reshape((-1,4))
    faces = np.append(faces, idxs_bot[:,top_right_idxs], axis=0)
    faces = np.append(faces, idxs_bot[:,bot_left_idxs], axis=0)

    mesh = pymeshlab.Mesh(
        vertex_matrix = vertices,
        face_matrix = faces
    )
    ms = pymeshlab.MeshSet()
    ms.add_mesh(mesh)
    ms.apply_filter("remove_unreferenced_vertices")

    return ms

def meshify_terrain_features(heights_top, intermediate_bottom_heights, offset_x, offset_y, pixel_size):

    vertices_top = generate_vertices(heights_top, offset_x, offset_y, pixel_size)
    vertices_bot = generate_vertices(intermediate_bottom_heights, offset_x, offset_y, pixel_size)
    vertices = np.append(vertices_top, vertices_bot, axis=0)

    n_rows, n_cols = heights_top.shape
    dem_size = n_rows * n_cols
    
    idxs = generate_idxs(n_rows, n_cols)
    faces = np.empty((0,3), dtype=np.int32)

    # Compute corners
    nw = heights_top[:n_rows-1,:n_cols-1] != -1
    sw = heights_top[1:,:n_cols-1] != -1
    ne = heights_top[:n_rows-1,1:] != -1
    se = heights_top[1:,1:] != -1

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
    horizontal_bottom = np.logical_or(np.logical_not(sw), np.logical_not(se))
    horizontal_s = np.logical_and(horizontal_s, horizontal_bottom)
    horizontal_s_faces = idxs[horizontal_s].reshape(-1, 1)
    horizontal_s_faces = np.tile(horizontal_s_faces, 4)
    horizontal_s_faces[:,1] += dem_size
    horizontal_s_faces[:,2] += dem_size + 1
    horizontal_s_faces[:,3] += 1
    faces = np.append(faces, horizontal_s_faces[:,top_left_idxs], axis=0)
    faces = np.append(faces, horizontal_s_faces[:,bot_right_idxs], axis=0)

    # horizontal lines facing north
    horizontal_n = np.logical_and(sw, se)
    horizontal_top = np.logical_or(np.logical_not(nw), np.logical_not(ne))
    horizontal_n = np.logical_and(horizontal_n, horizontal_top)
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
    vertical_right = np.logical_or(np.logical_not(ne), np.logical_not(se))
    vertical_e = np.logical_and(vertical_e, vertical_right)
    vertical_e_faces = idxs[vertical_e].reshape(-1, 1)
    vertical_e_faces = np.tile(vertical_e_faces, 4)
    vertical_e_faces[:,1] += n_cols
    vertical_e_faces[:,2] += dem_size + n_cols
    vertical_e_faces[:,3] += dem_size
    faces = np.append(faces, vertical_e_faces[:,top_left_idxs], axis=0)
    faces = np.append(faces, vertical_e_faces[:,bot_right_idxs], axis=0)
    
    # vertical lines facing west
    vertical_w = np.logical_and(ne, se)
    vertical_left = np.logical_or(np.logical_not(nw), np.logical_not(sw))
    vertical_w = np.logical_and(vertical_w, vertical_left)
    vertical_w_faces = idxs[vertical_w].reshape(-1, 1)
    vertical_w_faces += 1
    vertical_w_faces = np.tile(vertical_w_faces, 4)
    vertical_w_faces[:,1] += dem_size
    vertical_w_faces[:,2] += dem_size + n_cols
    vertical_w_faces[:,3] += n_cols
    faces = np.append(faces, vertical_w_faces[:,top_left_idxs], axis=0)
    faces = np.append(faces, vertical_w_faces[:,bot_right_idxs], axis=0)

    # Sideways faces - upwards
    left = heights_top[0,:n_cols-1] != constants.NULL_HEIGHT
    right = heights_top[0,1:] != constants.NULL_HEIGHT
    idxs_sideways_n = np.logical_and(left, right)
    faces_sideways_n = np.arange(n_cols-1, dtype=np.float32)
    faces_sideways_n = faces_sideways_n[idxs_sideways_n]
    faces_sideways_n = faces_sideways_n.reshape((-1, 1))
    faces_sideways_n = np.tile(faces_sideways_n, 4)
    faces_sideways_n[:,0] += 0
    faces_sideways_n[:,1] += 1
    faces_sideways_n[:,2] += dem_size + 1
    faces_sideways_n[:,3] += dem_size
    faces = np.append(faces, faces_sideways_n[:,top_right_idxs], axis=0)
    faces = np.append(faces, faces_sideways_n[:,bot_left_idxs], axis=0)

    # Sideways faces - southwards
    left = heights_top[n_rows-1,:n_cols-1] != constants.NULL_HEIGHT
    right = heights_top[n_rows-1,1:] != constants.NULL_HEIGHT
    idxs_sideways_s = np.logical_and(left, right)
    faces_sideways_s = np.arange(n_cols-1, dtype=np.float32)
    faces_sideways_s = faces_sideways_s[idxs_sideways_s]
    faces_sideways_s = faces_sideways_s.reshape((-1, 1))
    faces_sideways_s = np.tile(faces_sideways_s, 4)
    faces_sideways_s[:,0] += dem_size - n_cols
    faces_sideways_s[:,1] += 2*dem_size - n_cols
    faces_sideways_s[:,2] += 2*dem_size - n_cols + 1
    faces_sideways_s[:,3] += dem_size - n_cols + 1
    faces = np.append(faces, faces_sideways_s[:,top_right_idxs], axis=0)
    faces = np.append(faces, faces_sideways_s[:,bot_left_idxs], axis=0)

    # Sideways faces - left
    top = heights_top[:n_rows-1,0] != constants.NULL_HEIGHT
    bot = heights_top[1:,0] != constants.NULL_HEIGHT
    idxs_sideways_w = np.logical_and(top, bot)
    faces_sideways_w = np.arange(0, dem_size-n_cols, n_cols, dtype=np.float32)
    faces_sideways_w = faces_sideways_w[idxs_sideways_w]
    faces_sideways_w = faces_sideways_w.reshape((-1, 1))
    faces_sideways_w = np.tile(faces_sideways_w, 4)
    faces_sideways_w[:,0] += 0
    faces_sideways_w[:,1] += dem_size
    faces_sideways_w[:,2] += dem_size + n_cols
    faces_sideways_w[:,3] += n_cols
    faces = np.append(faces, faces_sideways_w[:,top_right_idxs], axis=0)
    faces = np.append(faces, faces_sideways_w[:,bot_left_idxs], axis=0)

    # Sideways faces - right
    top = heights_top[:n_rows-1,n_cols-1] != constants.NULL_HEIGHT
    bot = heights_top[1:,n_cols-1] != constants.NULL_HEIGHT
    idxs_sideways_e = np.logical_and(top, bot)
    faces_sideways_e = np.arange(0, dem_size-n_cols, n_cols, dtype=np.float32)
    faces_sideways_e = faces_sideways_e[idxs_sideways_e]
    faces_sideways_e = faces_sideways_e.reshape((-1, 1))
    faces_sideways_e = np.tile(faces_sideways_e, 4)
    faces_sideways_e[:,0] += n_cols - 1
    faces_sideways_e[:,1] += 2*n_cols - 1
    faces_sideways_e[:,2] += dem_size + 2*n_cols - 1
    faces_sideways_e[:,3] += dem_size + n_cols - 1
    faces = np.append(faces, faces_sideways_e[:,top_right_idxs], axis=0)
    faces = np.append(faces, faces_sideways_e[:,bot_left_idxs], axis=0)

    mesh = pymeshlab.Mesh(
        vertex_matrix = vertices,
        face_matrix = faces
    )
    ms = pymeshlab.MeshSet()
    ms.add_mesh(mesh)
    ms.apply_filter("remove_unreferenced_vertices")

    return ms

# VERTEX ORDERING
# Top: dem_size
# Bottom: dem_size
def meshify_buildings_trees(heights_top, intermediate_bottom_heights, offset_x, offset_y, pixel_size):

    # Vertices
    vertices_top = generate_vertices(heights_top, offset_x, offset_y, pixel_size)
    vertices_bot = generate_vertices(intermediate_bottom_heights, offset_x, offset_y, pixel_size)
    vertices = np.append(vertices_top, vertices_bot, axis=0)

    n_rows, n_cols = heights_top.shape
    dem_size = n_rows * n_cols
    
    idxs = generate_idxs(n_rows, n_cols)
    faces = np.empty((0,3), dtype=np.int32)

    # Compute corners
    nw = heights_top[:n_rows-1,:n_cols-1] != -1
    sw = heights_top[1:,:n_cols-1] != -1
    ne = heights_top[:n_rows-1,1:] != -1
    se = heights_top[1:,1:] != -1

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
    top_idxs = np.array([4, 1, 0])
    bot_idxs = np.array([5, 2, 3])
    side_idxs_1 = np.array([4, 2, 1])
    side_idxs_2 = np.array([4, 3, 2])

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

    # Sideways faces - upwards
    left = heights_top[0,:n_cols-1] != constants.NULL_HEIGHT
    right = heights_top[0,1:] != constants.NULL_HEIGHT
    idxs_sideways_n = np.logical_and(left, right)
    faces_sideways_n = np.arange(n_cols-1, dtype=np.float32)
    faces_sideways_n = faces_sideways_n[idxs_sideways_n]
    faces_sideways_n = faces_sideways_n.reshape((-1, 1))
    faces_sideways_n = np.tile(faces_sideways_n, 4)
    faces_sideways_n[:,0] += 0
    faces_sideways_n[:,1] += 1
    faces_sideways_n[:,2] += dem_size + 1
    faces_sideways_n[:,3] += dem_size
    faces = np.append(faces, faces_sideways_n[:,top_right_idxs], axis=0)
    faces = np.append(faces, faces_sideways_n[:,bot_left_idxs], axis=0)

    # Sideways faces - southwards
    left = heights_top[n_rows-1,:n_cols-1] != constants.NULL_HEIGHT
    right = heights_top[n_rows-1,1:] != constants.NULL_HEIGHT
    idxs_sideways_s = np.logical_and(left, right)
    faces_sideways_s = np.arange(n_cols-1, dtype=np.float32)
    faces_sideways_s = faces_sideways_s[idxs_sideways_s]
    faces_sideways_s = faces_sideways_s.reshape((-1, 1))
    faces_sideways_s = np.tile(faces_sideways_s, 4)
    faces_sideways_s[:,0] += dem_size - n_cols
    faces_sideways_s[:,1] += 2*dem_size - n_cols
    faces_sideways_s[:,2] += 2*dem_size - n_cols + 1
    faces_sideways_s[:,3] += dem_size - n_cols + 1
    faces = np.append(faces, faces_sideways_s[:,top_right_idxs], axis=0)
    faces = np.append(faces, faces_sideways_s[:,bot_left_idxs], axis=0)

    # Sideways faces - left
    top = heights_top[:n_rows-1,0] != constants.NULL_HEIGHT
    bot = heights_top[1:,0] != constants.NULL_HEIGHT
    idxs_sideways_w = np.logical_and(top, bot)
    faces_sideways_w = np.arange(0, dem_size-n_cols, n_cols, dtype=np.float32)
    faces_sideways_w = faces_sideways_w[idxs_sideways_w]
    faces_sideways_w = faces_sideways_w.reshape((-1, 1))
    faces_sideways_w = np.tile(faces_sideways_w, 4)
    faces_sideways_w[:,0] += 0
    faces_sideways_w[:,1] += dem_size
    faces_sideways_w[:,2] += dem_size + n_cols
    faces_sideways_w[:,3] += n_cols
    faces = np.append(faces, faces_sideways_w[:,top_right_idxs], axis=0)
    faces = np.append(faces, faces_sideways_w[:,bot_left_idxs], axis=0)

    # Sideways faces - right
    top = heights_top[:n_rows-1,n_cols-1] != constants.NULL_HEIGHT
    bot = heights_top[1:,n_cols-1] != constants.NULL_HEIGHT
    idxs_sideways_e = np.logical_and(top, bot)
    faces_sideways_e = np.arange(0, dem_size-n_cols, n_cols, dtype=np.float32)
    faces_sideways_e = faces_sideways_e[idxs_sideways_e]
    faces_sideways_e = faces_sideways_e.reshape((-1, 1))
    faces_sideways_e = np.tile(faces_sideways_e, 4)
    faces_sideways_e[:,0] += n_cols - 1
    faces_sideways_e[:,1] += 2*n_cols - 1
    faces_sideways_e[:,2] += dem_size + 2*n_cols - 1
    faces_sideways_e[:,3] += dem_size + n_cols - 1
    faces = np.append(faces, faces_sideways_e[:,top_right_idxs], axis=0)
    faces = np.append(faces, faces_sideways_e[:,bot_left_idxs], axis=0)

    mesh = pymeshlab.Mesh(
        vertex_matrix = vertices,
        face_matrix = faces
    )
    ms = pymeshlab.MeshSet()
    ms.add_mesh(mesh)
    ms.apply_filter("remove_unreferenced_vertices")

    return ms

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
    # vertices = vertices[:,[0,2,1]] # flips y/z

    vertices *= VERTICES_SCALE_FACTOR

    return vertices

# Vertices that are located at the bottom on the edges
def generate_bottom_vertices(n_rows, n_cols, offset_x, offset_y, pixel_size, bottom_height=0):

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
    heights = np.full((vertices.shape[0], 1), bottom_height, dtype=np.float32)
    vertices = np.append(vertices, heights, axis=1)
    # vertices = vertices[:,[0,2,1]] # flips y/z

    vertices *= VERTICES_SCALE_FACTOR

    return vertices

def generate_idxs(n_rows, n_cols):
    idxs = np.arange((n_rows-1) * (n_cols-1))
    idxs = idxs.reshape((n_rows-1, n_cols-1))
    offsets = np.arange(n_rows-1).reshape((-1, 1))
    offsets = np.tile(offsets, n_cols-1)
    idxs = idxs + offsets
    return idxs
    
def expand_mask(mask):
    n_rows, n_cols = mask.shape
    mask_new = np.full((n_rows+1, n_cols+1), False, dtype=bool)
    mask_new[:n_rows,:n_cols][mask] = True
    mask_new[1:,1:][mask] = True
    mask_new[1:,:n_cols][mask] = True
    mask_new[:n_rows,1:][mask] = True
    return mask_new