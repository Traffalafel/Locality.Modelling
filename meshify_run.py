import argparse
from read_asc import read_asc, aggregate, boost_y
from meshify import meshify

GROUND_DEPTH = 20

def main():

    # Define arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('file_in', metavar='i', type=str, help='Input file')
    parser.add_argument('file_out', metavar='o', type=str, help='Output file')
    parser.add_argument('aggreg_size', metavar='as', type=int, help="Aggregation size")
    parser.add_argument('aggreg_method', metavar='am', type=str, choices=['min', 'max', 'avg'], help="Aggregation method")
    parser.add_argument('y_boost', metavar='yb', type=float, help="Y boost")

    # Parse arguments
    args = parser.parse_args()
    file_path_in = args.file_in
    file_path_out = args.file_out
    AGGREG_SIZE = args.aggreg_size
    Y_BOOST = args.y_boost
    AGGREG_METHOD = args.aggreg_method

    # Read and prerprocess ASC file
    heights = read_asc(file_path_in)
    heights = aggregate(heights, AGGREG_SIZE, AGGREG_METHOD)
    boost_y(heights, Y_BOOST)

    # Meshify
    block_size = 0.4 * AGGREG_SIZE
    lines_out = meshify(heights, block_size, GROUND_DEPTH)

    # Write output
    with open(file_path_out, 'w+') as fd:
        fd.writelines(lines_out)

main()