import sys
from get_heights import get_heights
from meshify import meshify

# ARGS
HEIGHTS_BOOST = 1.5

# Constants
MIN_DEPTH = 30
ORIGINAL_BLOCK_SIZE = 0.4
AGGREG_SIZE = 4
BLOCK_SIZE = ORIGINAL_BLOCK_SIZE * AGGREG_SIZE

def main():
    
    # Parse args
    tifs_dir_path = sys.argv[1]
    file_out_path = sys.argv[2]
    bound_w = float(sys.argv[3])
    bound_e = float(sys.argv[4])
    bound_s = float(sys.argv[5])
    bound_n = float(sys.argv[6])
    bounds = (bound_w, bound_e, bound_s, bound_n)

    heights, _ = get_heights(tifs_dir_path, bounds)

    # Heights boost
    for i in range(heights.shape[0]):
        for j in range(heights.shape[1]):
            heights[i][j] *= HEIGHTS_BOOST

    lines = meshify(heights, BLOCK_SIZE, MIN_DEPTH)

    with open(file_out_path, 'w+') as fd:
        fd.writelines(lines)

main()