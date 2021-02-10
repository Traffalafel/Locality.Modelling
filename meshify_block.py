import sys
import re

HEADER_LENGTH = 6
N_AGGREGATE = 2
Y_BOOST = 1.0

file_path_in = sys.argv[1]
file_path_out = sys.argv[2]

with open(file_path_in, 'r') as fd:
    lines = fd.readlines()

heights = []
n_rows = 0

for row_idx, line in enumerate(lines):

    line = line.replace('\n', '')
    line = re.sub(" +", " ", line)
    line = line.strip()

    # Skip header
    if row_idx < HEADER_LENGTH:
        continue

    heights.append([])

    line_heights = line.split(' ')
    for col_idx, height in enumerate(line_heights):
        height = float(height)
        heights[n_rows].append(height)

    n_rows += 1

grid_size = len(heights)
n_steps = grid_size // N_AGGREGATE
heights_aggregated = []

for row in range(n_steps):
    heights_aggregated.append([])
    for col in range(n_steps):
        i_idxs = range(row*N_AGGREGATE, (row*N_AGGREGATE)+N_AGGREGATE)
        j_idxs = range(col*N_AGGREGATE, (col*N_AGGREGATE)+N_AGGREGATE)
        h = max(heights[i][j] for i in i_idxs for j in j_idxs)
        heights_aggregated[row].append(h)

grid_aggregated_size = len(heights_aggregated)
lines_out = []

# Generate vertices
block_size = 0.4 * N_AGGREGATE
for row in range(grid_aggregated_size):
    for col in range(grid_aggregated_size):
        height = heights_aggregated[row][col] * Y_BOOST
        lines_out.append(f"v {col*block_size} {height} {row*block_size}\n")
        lines_out.append(f"v {(col+1)*block_size} {height} {row*block_size}\n")
        lines_out.append(f"v {col*block_size} {height} {(row+1)*block_size}\n")
        lines_out.append(f"v {(col+1)*block_size} {height} {(row+1)*block_size}\n")

# Generate faces
count = 0
for row in range(grid_aggregated_size):
    for col in range(grid_aggregated_size):
        lines_out.append(f"f {count+1} {count+2} {count+3}\n")
        lines_out.append(f"f {count+2} {count+3} {count+4}\n")
        if col != 0 and col != grid_aggregated_size-1:
            lines_out.append(f"f {count+2} {count+4} {count+7}\n")
            lines_out.append(f"f {count+2} {count+5} {count+7}\n")
        if row != 0 and row != grid_aggregated_size-1:
            next_row_offset = N_AGGREGATE*grid_aggregated_size
            lines_out.append(f"f {count+3} {count+4} {count+1+next_row_offset}\n")
            lines_out.append(f"f {count+4} {count+1+next_row_offset} {count+2+next_row_offset}\n")
        count += 4

# Write output
with open(file_path_out, 'w+') as fd:
    fd.writelines(lines_out)