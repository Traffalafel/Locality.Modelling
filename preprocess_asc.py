from read_asc import read_asc, write_heights, aggregate, boost_z
import sys

AGGREG_SIZE = 4
AGGREG_METHOD = "max"

def main():

    file_in_path = sys.argv[1]
    file_out_path = sys.argv[2]

    heights = read_asc(file_in_path)
    heights = aggregate(heights, AGGREG_SIZE, AGGREG_METHOD)

    write_heights(file_out_path, heights)

main()