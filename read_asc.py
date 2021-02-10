import sys
import re
import argparse
import pickle

HEADER_LENGTH = 6

def read_heights(file_path):
    with open(file_path, "rb") as fd:
        return pickle.load(fd)

def write_heights(file_path, heights):
    with open(file_path, "wb+") as fd:
        pickle.dump(heights, fd)

def read_asc(file_path_in):
    
    with open(file_path_in, 'r') as fd:
        lines = fd.readlines()

    heights = []
    n_rows = len(lines)

    for row_idx in range(n_rows-1, 0, -1):
        line = lines[row_idx]
        line = line.replace('\n', '')
        line = re.sub(" +", " ", line)
        line = line.strip()

        # Skip header
        if row_idx < HEADER_LENGTH:
            continue

        heights.append([])

        line_heights = line.split(' ')
        for height in line_heights:
            height = float(height)
            heights[-1].append(height)

    return heights

def aggregate(heights, aggreg_size, aggreg_method):
    grid_size = len(heights)
    n_steps = grid_size // aggreg_size
    heights_aggregated = []

    # Aggregate neighbouring heights
    for row in range(n_steps):
        heights_aggregated.append([])
        for col in range(n_steps):
            i_idxs = range(row*aggreg_size, (row*aggreg_size)+aggreg_size)
            j_idxs = range(col*aggreg_size, (col*aggreg_size)+aggreg_size)

            if aggreg_method == "min":
                h = min(heights[i][j] for i in i_idxs for j in j_idxs)
            if aggreg_method == "max":
                h = max(heights[i][j] for i in i_idxs for j in j_idxs)
            if aggreg_method == "avg":
                h = sum(heights[i][j] for i in i_idxs for j in j_idxs) / (aggreg_size**2)

            heights_aggregated[row].append(h)

    return heights_aggregated

def boost_y(heights, boost):
    n_rows = len(heights)
    n_cols = len(heights[0])
    for i in range(n_rows):
        for j in range(n_cols):
            heights[i][j] *= boost