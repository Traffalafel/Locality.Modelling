import numpy as np

def remove_strings(heights):
    remove_strings_x(heights)
    remove_strings_y(heights)

def remove_strings_x(heights):

    n_rows, n_cols = heights.shape
    for row in range(n_rows):

        col = 0

        while col < n_cols-3:

            interval = heights[row,col:col+4]
            if all(h == -1 for h in interval):
                # No building
                col += 3
                continue

            if not any(h == -1 for h in interval):
                # Only building
                col += 3
                continue

            if interval[0] == -1 and interval[3] == -1:
                heights[row, col+1:col+3] = -1
                col += 3
                continue

            col += 1

def remove_strings_y(heights):

    n_rows, n_cols = heights.shape
    for col in range(n_cols):

        row = 0

        while row < n_rows-3:

            interval = heights[row:row+4,col]
            if all(h == -1 for h in interval):
                # No building
                row += 3
                continue

            if not any(h == -1 for h in interval):
                # Only building
                row += 3
                continue

            if interval[0] == -1 and interval[3] == -1:
                heights[row+1:row+3, col] = -1
                row += 3
                continue

            row += 1
