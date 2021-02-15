import argparse
from read_asc import read_heights, boost_z
from meshify import meshify

HEIGHTS_FILE_PATH = r"D:\PrintCitiesData\DHM_overflade_bins\DSM_1km_6170_715.bin"
OBJ_OUT_PATH = r".\models\color.obj"
MTLLIB_VALUE = r".\blackwhite.mtl"
AGGREG_SIZE = 4
Z_MIN = 20
Z_BOOST = 1.5

def main():

    # Read and prerprocess ASC file
    heights = read_heights(HEIGHTS_FILE_PATH)
    boost_z(heights, Z_BOOST)

    materials = [[0 if i % 2 == (row_idx%2) else 1 for i in range(len(row)-1)] for row_idx,row in enumerate(heights[:-1])]
    material_names = {
        0: "white",
        1: "black"
    }

    # Meshify
    block_size = 0.4 * AGGREG_SIZE
    lines_out = meshify(heights, block_size, Z_MIN, materials, material_names, MTLLIB_VALUE)

    # Write output
    with open(OBJ_OUT_PATH, 'w+') as fd:
        fd.writelines(lines_out)

main()