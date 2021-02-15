import sys
import os
from pyproj import Transformer
from read_asc import read_heights
from Grid import Grid, Cell
from meshify import meshify
from math import floor, ceil

WSG84_EPSG = 4326
ETRS89_UTM32_EPSG = 3044
KM_TO_POINTS_RATIO = 625
ASC_FILE_METRES = 1000
AGGREG_SIZE = 4
AGGREG_METHOD = "max"
Z_BOOST = 1.5
GROUND_DEPTH = 30

def main():

    if len(sys.argv) != 7:
        print("Usage: <bins_dir> <lat> <lng> <length_x> <length_y> <file_out>")
        return
    
    bins_dir_path = sys.argv[1]
    input_lat = float(sys.argv[2])
    input_lon = float(sys.argv[3])
    length_metres_x = int(sys.argv[4])
    length_metres_y = int(sys.argv[5])
    file_out_path = sys.argv[6]

    # Compute SW and NE coordinates 
    transformer = Transformer.from_crs(WSG84_EPSG, ETRS89_UTM32_EPSG)
    sw_y, sw_x = transformer.transform(input_lat, input_lon)
    ne_x = sw_x + length_metres_x
    ne_y = sw_y + length_metres_y

    # Compute coordinates for files containing SW and NE points
    sw_file_x = int(sw_x // ASC_FILE_METRES)
    sw_file_y = int(sw_y // ASC_FILE_METRES)
    ne_file_x = int(ne_x // ASC_FILE_METRES)
    ne_file_y = int(ne_y // ASC_FILE_METRES)

    grid = Grid(KM_TO_POINTS_RATIO)

    for file_y in range(sw_file_y, ne_file_y+1):
        for file_x in range(sw_file_x, ne_file_x+1):
            file_name = f"DSM_1km_{file_y}_{file_x}.bin"
            heights_file_path = os.path.join(bins_dir_path, file_name)
            heights = read_heights(heights_file_path)
            position = (int(file_x-sw_file_x), int(file_y-sw_file_y))
            cell = Cell(heights, position)
            grid.add_cell(cell)

    x_min_metres = sw_x - (sw_file_x * ASC_FILE_METRES)
    x_max_metres = ne_x - (sw_file_x * ASC_FILE_METRES)
    z_min_metres = sw_y - (sw_file_y * ASC_FILE_METRES)
    z_max_metres = ne_y - (sw_file_y * ASC_FILE_METRES)
    x_min = floor(x_min_metres * KM_TO_POINTS_RATIO / 1000)
    x_max = ceil(x_max_metres * KM_TO_POINTS_RATIO / 1000)
    z_min = floor(z_min_metres * KM_TO_POINTS_RATIO / 1000)
    z_max = ceil(z_max_metres * KM_TO_POINTS_RATIO / 1000)

    heights_out = grid.get_heights(x_min, x_max, z_min, z_max)

    for i in range(len(heights_out)):
        for j in range(len(heights_out[0])):
            heights_out[i][j] *= Z_BOOST

    block_size = 0.4 * AGGREG_SIZE
    lines_out = meshify(heights_out, block_size, GROUND_DEPTH)

    with open(file_out_path, 'w+') as fd:
        fd.writelines(lines_out)

main()