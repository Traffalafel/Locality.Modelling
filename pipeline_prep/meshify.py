import numpy as np
import matplotlib.pyplot as plt
import pymeshlab

PIXEL_SIZE = 0.4

def extract_material(vertices, faces):
    
    # Find which vertices to keep
    vertices_keep = set()
    for face in faces:
        for v in face:
            vertices_keep.add(v)

    # Give new indices to vertices to keep
    new_idx = 0
    vertices_new_idxs = dict()
    vertices_new = []
    for old_idx, v in enumerate(vertices):
        if old_idx in vertices_keep:
            vertices_new.append(v)
            vertices_new_idxs[old_idx] = new_idx
            new_idx += 1

    # Set these new vertices in faces
    faces_new = []
    for face in faces:
        face_new = [vertices_new_idxs[v] for v in face]
        faces_new.append(face_new)

    return vertices_new, faces_new

def meshify_terrain(heights, roads_mask, green_mask, water_mask):
    pass

def generate_vertices(heights):
    n_rows, n_cols = heights.shape
    xs = np.arange(n_cols)
    ys = np.arange(n_rows)
    xx, yy = np.meshgrid(xs, ys)
    xx = xx.reshape((n_rows, n_cols, -1))
    yy = yy.reshape((n_rows, n_cols, -1))
    vertices = np.append(xx, yy, axis=2)
    vertices = vertices.reshape((-1, 2))
    vertices = vertices.astype(np.float32) * PIXEL_SIZE
    vertices = np.append(vertices, heights.reshape(-1, 1), axis=1)
    return vertices

def meshify_elevation(heights, heights_terrain):

    # Vertices
    vertices = generate_vertices(heights)
    vertices_terrain = generate_vertices(heights_terrain)
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
    faces = np.append(faces, grid_up_faces[:,top_left_idxs], axis=0)
    faces = np.append(faces, grid_up_faces[:,bot_right_idxs], axis=0)

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

    mesh = pymeshlab.Mesh(
        vertex_matrix = vertices,
        face_matrix = faces
    )
    ms = pymeshlab.MeshSet()
    ms.add_mesh(mesh)

    ms.apply_filter("remove_unreferenced_vertices")

    return ms

def meshify(heights, mapping=None, materials=None):

    n_rows, n_cols = heights.shape
    n_heights = n_rows*n_cols

    if mapping is None:
        shape = (heights.shape[0]-1, heights.shape[1]-1)
        mapping = np.zeros(shape)
        materials = set()
        materials.add(0)

    # Vertices
    vertices_global = []
    for row in range(n_rows):
        for col in range(n_cols):
            height = heights[row][col]
            vertices_global.append([row+0.5, col+0.5, height])

    # Faces
    vertices = dict()
    faces = dict()
    for material in materials:
        faces[material] = []
        idxs = np.argwhere(mapping == material)
        for row, col in idxs:
            
            heights_corners = [heights[row+i][col+j] for i in range(2) for j in range(2)]
            if any(h == -1 for h in heights_corners):
                continue

            offset = (row * n_cols) + col
            max_idx = heights_corners.index(max(heights_corners))
            if max_idx == 0 or max_idx == 3:
                # max is NW or SE
                faces[material].append([offset, offset+n_cols, offset+1])
                faces[material].append([offset+1, offset+n_cols, offset+n_cols+1])
            else:
                # max is SW or NE
                faces[material].append([offset, offset+n_cols, offset+n_cols+1])
                faces[material].append([offset, offset+n_cols+1, offset+1])

        vertices_mat, faces_mat = extract_material(vertices_global, faces[material])
        faces[material] = faces_mat
        vertices[material] = vertices_mat
        
    return vertices, faces    

def mesh_to_obj(vertices, faces):
    lines = []
    # lines.append(f"mtllib {mtllib}\n")
    for v in vertices:
        lines.append(f"v {v[0]} {v[1]} {v[2]}\n")
    # lines.append(f"newmtl {material_name}\n")
    for f in faces:
        lines.append(f"f {f[0]+1} {f[1]+1} {f[2]+1}\n")
    return lines

# # Top side vertices
# for col in range(n_cols):
#     lines_out.append(f"v {0.5*block_size} {(col+0.5)*block_size} 0\n")

# # Top side faces
# for col in range(n_cols-1):
#     lines_out.append(f"f {col+1} {col+2} {col+1+n_heights}\n")
#     lines_out.append(f"f {col+2} {col+1+n_heights} {col+2+n_heights}\n")

# # Bottom side vertices
# offset_hi = n_heights - n_cols
# offset_lo = n_cols + n_heights
# for col in range(n_cols):
#     lines_out.append(f"v {(n_rows-0.5)*block_size} {(col+0.5)*block_size} 0\n")

# # Bottom side faces
# offset_hi = n_heights - n_cols
# offset_lo = n_cols + n_heights
# for col in range(n_cols-1):
#     top = col+offset_hi
#     bot = col+offset_lo
#     lines_out.append(f"f {top+1} {top+2} {bot+1}\n")
#     lines_out.append(f"f {top+2} {bot+1} {bot+2}\n")

# # Left side vertices
# offset_hi = 1
# offset_lo = n_heights + n_cols * 2
# for row in range(n_rows):
#     lines_out.append(f"v {(row+0.5)*block_size} {0.5*block_size} 0\n")

# # Left side faces
# offset_hi = 1
# offset_lo = n_heights + n_cols * 2
# for row in range(n_rows-1):
#     lines_out.append(f"f {offset_hi} {offset_hi+n_cols} {row+offset_lo+1}\n")
#     lines_out.append(f"f {offset_hi+n_cols} {row+offset_lo+1} {row+offset_lo+2}\n")
#     offset_hi += n_cols

# # Right side vertices
# offset_hi = n_cols
# offset_lo = n_heights + n_cols * 2 + n_rows
# for row in range(n_rows):
#     lines_out.append(f"v {(row+0.5)*block_size} {(n_cols-0.5)*block_size} 0\n")

# # Right side faces
# offset_hi = n_cols
# offset_lo = n_heights + n_cols * 2 + n_rows
# for row in range(n_rows-1):
#     lines_out.append(f"f {offset_hi} {offset_hi+n_cols} {row+offset_lo+1}\n")
#     lines_out.append(f"f {offset_hi+n_cols} {row+offset_lo+1} {row+offset_lo+2}\n")
#     offset_hi += n_cols

# # Add bottom square
# offset_bottom = n_heights + n_rows*2 + n_cols*2
# lines_out.append(f"v {0.5*block_size} {0.5*block_size} 0\n")
# lines_out.append(f"v {0.5*block_size} {(n_cols-0.5)*block_size} 0\n")
# lines_out.append(f"v {(n_rows-0.5)*block_size} {0.5*block_size} 0\n")
# lines_out.append(f"v {(n_rows-0.5)*block_size} {(n_cols-0.5)*block_size} 0\n")
# lines_out.append(f"f {offset_bottom+2} {offset_bottom+3} {offset_bottom+1}\n")
# lines_out.append(f"f {offset_bottom+4} {offset_bottom+3} {offset_bottom+2}\n")