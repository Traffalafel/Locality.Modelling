import numpy as np

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

def meshify_elevation(heights, heights_terrain):
    
    # S-N lines
    # W-E lines
    # SW-NE lines
    # NW-SE lines
    
    pass

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

def mesh_to_obj(vertices, faces, material_name, mtllib):
    lines = []
    lines.append(f"mtllib {mtllib}\n")
    for v in vertices:
        lines.append(f"v {v[0]} {v[1]} {v[2]}\n")
    lines.append(f"newmtl {material_name}\n")
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