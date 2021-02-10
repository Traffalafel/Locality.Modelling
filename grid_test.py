from Grid import Grid, Cell
from read_asc import read_asc, aggregate, boost_y
from meshify import meshify
import sys

AGGREG_SIZE = 4
AGGREG_METHOD = "max"
Y_BOOST = 1.0
GROUND_DEPTH = 30

file_path_in_1 = sys.argv[1]
file_path_in_2 = sys.argv[2]
file_path_in_3 = sys.argv[3]
file_path_in_4 = sys.argv[4]
file_path_out = sys.argv[5]

x_min = int(sys.argv[6])
x_max = int(sys.argv[7])
z_min = int(sys.argv[8])
z_max = int(sys.argv[9])

def prep_asc(file_path):
    heights = read_asc(file_path)
    heights = aggregate(heights, AGGREG_SIZE, AGGREG_METHOD)
    boost_y(heights, Y_BOOST)
    return heights

def main():

    heights1 = prep_asc(file_path_in_1)
    heights2 = prep_asc(file_path_in_2)
    heights3 = prep_asc(file_path_in_3)
    heights4 = prep_asc(file_path_in_4)
    
    cell_size = len(heights1)
    grid = Grid(cell_size)

    cell1 = Cell(heights1, (0,0))
    grid.add_cell(cell1)
    
    cell2 = Cell(heights2, (1,0))
    grid.add_cell(cell2)

    cell3 = Cell(heights3, (0,1))
    grid.add_cell(cell3)

    cell4 = Cell(heights4, (1,1))
    grid.add_cell(cell4)
    
    new_heights = grid.get_heights(x_min, x_max, z_min, z_max)

    block_size = 0.4 * AGGREG_SIZE
    lines_out = meshify(new_heights, block_size, GROUND_DEPTH)

    with open(file_path_out, 'w+') as fd:
        fd.writelines(lines_out)

main()