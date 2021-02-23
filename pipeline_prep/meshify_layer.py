def gen_materials_faces(materials):

    materials_faces = dict()

    n_rows = len(materials)
    n_cols = len(materials[0])

    for row in range(n_rows):
        for col in range(n_cols):
            material = materials[row][col]
            if material in materials_faces:
                materials_faces[material].append((row,col))
            else:
                materials_faces[material] = [(row,col)]
    
    return materials_faces

def gen_color_faces(heights, materials_faces, materials_names):
    n_rows, n_cols = heights.shape
    lines = []
    for material in materials_faces:
        material_name = materials_names[material]
        lines.append(f"usemtl {material_name}\n")
        for (row, col) in materials_faces[material]:

            heights_corners = [heights[row+i][col+j] for i in range(2) for j in range(2)]
            if any(h == -1 for h in heights_corners):
                continue

            offset = 1 + (row * n_cols) + col
            lines.append(f"f {offset} {offset+n_cols} {offset+1}\n")
            lines.append(f"f {offset+1} {offset+n_cols} {offset+n_cols+1}\n")
            
    return lines

def gen_monochrome_faces(heights):
    n_rows, n_cols = heights.shape
    lines = []
    for row in range(n_rows - 1):
        for col in range(n_cols - 1):

            heights_corners = [heights[row+i][col+j] for i in range(2) for j in range(2)]
            if any(h == -1 for h in heights_corners):
                continue
            
            offset = 1 + (row * n_cols) + col
            lines.append(f"f {offset} {offset+n_cols} {offset+1}\n")
            lines.append(f"f {offset+1} {offset+n_cols} {offset+n_cols+1}\n")

    return lines

def meshify_layer(heights, materials=None, materials_names=None, mtllib=None):

    n_rows, n_cols = heights.shape
    n_heights = n_rows*n_cols

    print(f"CREATING MESH")
    print(f"n_rows: {n_rows}")
    print(f"n_cols: {n_cols}")
    print(f"n_heights: {n_heights}")

    lines_out = []

    if mtllib is not None:
        lines_out.append(f"mtllib {mtllib}\n")

    # Grid vertices
    for row in range(n_rows):
        for col in range(n_cols):
            height = heights[row][col]
            if height is -1:
                continue
            lines_out.append(f"v {row+0.5} {col+0.5} {height}\n")

    # Grid faces
    if materials is not None:
        materials_faces = gen_materials_faces(materials)
        face_lines = gen_color_faces(heights, materials_faces, materials_names)
    else:
        face_lines = gen_monochrome_faces(heights)
    lines_out += face_lines

    return lines_out