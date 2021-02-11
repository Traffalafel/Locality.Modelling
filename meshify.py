def meshify(heights, block_size, ground_depth):

    n_rows = len(heights)
    n_cols = len(heights[0])
    n_heights = n_rows*n_cols

    print(f"n_rows: {n_rows}")
    print(f"n_cols: {n_cols}")
    print(f"n_heights: {n_heights}")

    min_y = min(min(heights[i] for i in range(n_rows)))

    lines_out = []
    # Generate vertices
    for row in range(n_rows):
        for col in range(n_cols):
            height = heights[row][col] - min_y + ground_depth
            lines_out.append(f"v {(col+0.5)*block_size} {(row+0.5)*block_size} {height}\n")

    # Generate faces
    count = 0
    for row in range(n_rows):
        for col in range(n_cols):

            if row != n_rows-1 and col != n_cols-1:
                # Not last row
                lines_out.append(f"f {count+2} {count+1+n_cols} {count+1}\n")

            if row != 0 and col != n_cols-1:
                # Not last col
                lines_out.append(f"f {count+2-n_cols} {count+2} {count+1}\n")

            count += 1

    # Add vertices along top edge
    for col in range(n_cols):
        lines_out.append(f"v {(col+0.5)*block_size} {0.5*block_size} 0\n")
    for col in range(n_cols-1):
        lines_out.append(f"f {col+1} {col+2} {col+1+n_heights}\n")
        lines_out.append(f"f {col+2} {col+1+n_heights} {col+2+n_heights}\n")
    
    # Add vertices along bottom edge
    offset_hi = n_heights - n_cols
    offset_lo = n_cols + n_heights
    for col in range(n_cols):
        lines_out.append(f"v {(col+0.5)*block_size} {(n_rows-0.5)*block_size} 0\n")
    for col in range(n_cols-1):
        top = col+offset_hi
        bot = col+offset_lo
        lines_out.append(f"f {top+1} {top+2} {bot+1}\n")
        lines_out.append(f"f {top+2} {bot+1} {bot+2}\n")

    # Left edge
    offset_hi = 1
    offset_lo = n_heights + n_cols * 2
    for row in range(n_rows):
        lines_out.append(f"v {0.5*block_size} {(row+0.5)*block_size} 0\n")
    for row in range(n_rows-1):
        lines_out.append(f"f {offset_hi} {offset_hi+n_cols} {row+offset_lo+1}\n")
        lines_out.append(f"f {offset_hi+n_cols} {row+offset_lo+1} {row+offset_lo+2}\n")
        offset_hi += n_cols
    
    # Right edge
    offset_hi = n_cols
    offset_lo = n_heights + n_cols * 2 + n_rows
    for row in range(n_rows):
        lines_out.append(f"v {(n_cols-0.5)*block_size} {(row+0.5)*block_size} 0\n")
    for row in range(n_rows-1):
        lines_out.append(f"f {offset_hi} {offset_hi+n_cols} {row+offset_lo+1}\n")
        lines_out.append(f"f {offset_hi+n_cols} {row+offset_lo+1} {row+offset_lo+2}\n")
        offset_hi += n_cols

    # Add bottom square
    offset_bottom = n_heights + n_rows*2 + n_cols*2
    lines_out.append(f"v {0.5*block_size} {0.5*block_size} 0\n")
    lines_out.append(f"v {(n_cols-0.5)*block_size} {0.5*block_size} 0\n")
    lines_out.append(f"v {0.5*block_size} {(n_rows-0.5)*block_size} 0\n")
    lines_out.append(f"v {(n_cols-0.5)*block_size} {(n_rows-0.5)*block_size} 0\n")
    lines_out.append(f"f {offset_bottom+1} {offset_bottom+2} {offset_bottom+3}\n")
    lines_out.append(f"f {offset_bottom+2} {offset_bottom+3} {offset_bottom+4}\n")

    return lines_out