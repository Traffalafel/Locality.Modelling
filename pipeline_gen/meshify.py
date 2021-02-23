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

def gen_color_faces(n_rows, n_cols, materials_faces, materials_names):
    lines = []
    for material in materials_faces:
        material_name = materials_names[material]
        lines.append(f"usemtl {material_name}\n")
        for (row, col) in materials_faces[material]:
            offset = 1 + (row * n_cols) + col
            lines.append(f"f {offset} {offset+n_cols} {offset+1}\n")
            lines.append(f"f {offset+1} {offset+n_cols} {offset+n_cols+1}\n")
    return lines

def gen_monochrome_faces(n_rows, n_cols):
    lines = []
    count = 0
    for row in range(n_rows):
        for col in range(n_cols):
            if row != n_rows-1 and col != n_cols-1:
                # Not last row
                lines.append(f"f {count+1} {count+1+n_cols} {count+2}\n")
            if row != 0 and col != n_cols-1:
                # Not last col
                lines.append(f"f {count+1} {count+2} {count+2-n_cols}\n")
            count += 1
    return lines

def meshify(heights, block_size, base_height, materials=None, materials_names=None, mtllib=None):

    n_rows, n_cols = heights.shape
    n_heights = n_rows*n_cols

    print(f"CREATING MESH")
    print(f"n_rows: {n_rows}")
    print(f"n_cols: {n_cols}")
    print(f"n_heights: {n_heights}")

    min_y = heights.min()

    lines_out = []

    if mtllib is not None:
        lines_out.append(f"mtllib {mtllib}\n")

    # Grid vertices
    for row in range(n_rows):
        for col in range(n_cols):
            height = heights[row][col] - min_y + base_height
            lines_out.append(f"v {(row+0.5)*block_size} {(col+0.5)*block_size} {height}\n")

    # Grid faces
    if materials is not None:
        materials_faces = gen_materials_faces(materials)
        face_lines = gen_color_faces(n_rows, n_cols, materials_faces, materials_names)
    else:
        face_lines = gen_monochrome_faces(n_rows, n_cols)
    lines_out += face_lines

    # Top side vertices
    for col in range(n_cols):
        lines_out.append(f"v {0.5*block_size} {(col+0.5)*block_size} 0\n")

    # Top side faces
    for col in range(n_cols-1):
        lines_out.append(f"f {col+1} {col+2} {col+1+n_heights}\n")
        lines_out.append(f"f {col+2} {col+1+n_heights} {col+2+n_heights}\n")
    
    # Bottom side vertices
    offset_hi = n_heights - n_cols
    offset_lo = n_cols + n_heights
    for col in range(n_cols):
        lines_out.append(f"v {(n_rows-0.5)*block_size} {(col+0.5)*block_size} 0\n")

    # Bottom side faces
    offset_hi = n_heights - n_cols
    offset_lo = n_cols + n_heights
    for col in range(n_cols-1):
        top = col+offset_hi
        bot = col+offset_lo
        lines_out.append(f"f {top+1} {top+2} {bot+1}\n")
        lines_out.append(f"f {top+2} {bot+1} {bot+2}\n")

    # Left side vertices
    offset_hi = 1
    offset_lo = n_heights + n_cols * 2
    for row in range(n_rows):
        lines_out.append(f"v {(row+0.5)*block_size} {0.5*block_size} 0\n")

    # Left side faces
    offset_hi = 1
    offset_lo = n_heights + n_cols * 2
    for row in range(n_rows-1):
        lines_out.append(f"f {offset_hi} {offset_hi+n_cols} {row+offset_lo+1}\n")
        lines_out.append(f"f {offset_hi+n_cols} {row+offset_lo+1} {row+offset_lo+2}\n")
        offset_hi += n_cols
    
    # Right side vertices
    offset_hi = n_cols
    offset_lo = n_heights + n_cols * 2 + n_rows
    for row in range(n_rows):
        lines_out.append(f"v {(row+0.5)*block_size} {(n_cols-0.5)*block_size} 0\n")

    # Right side faces
    offset_hi = n_cols
    offset_lo = n_heights + n_cols * 2 + n_rows
    for row in range(n_rows-1):
        lines_out.append(f"f {offset_hi} {offset_hi+n_cols} {row+offset_lo+1}\n")
        lines_out.append(f"f {offset_hi+n_cols} {row+offset_lo+1} {row+offset_lo+2}\n")
        offset_hi += n_cols

    # Add bottom square
    offset_bottom = n_heights + n_rows*2 + n_cols*2
    lines_out.append(f"v {0.5*block_size} {0.5*block_size} 0\n")
    lines_out.append(f"v {0.5*block_size} {(n_cols-0.5)*block_size} 0\n")
    lines_out.append(f"v {(n_rows-0.5)*block_size} {0.5*block_size} 0\n")
    lines_out.append(f"v {(n_rows-0.5)*block_size} {(n_cols-0.5)*block_size} 0\n")
    lines_out.append(f"f {offset_bottom+2} {offset_bottom+3} {offset_bottom+1}\n")
    lines_out.append(f"f {offset_bottom+4} {offset_bottom+3} {offset_bottom+2}\n")

    return lines_out