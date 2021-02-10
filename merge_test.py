import numpy as np
import sys
from ObjFile import ObjFile
from ObjFileFactory import ObjFileFactory
from merge import merge_two
from normalize import normalize

def main():
    file1_path = sys.argv[1]
    file2_path = sys.argv[2]
    file_out_path = sys.argv[3]
    
    file1 = ObjFileFactory.from_file(file1_path)
    file1_offset = np.array([0, 0, 0])
    
    file2 = ObjFileFactory.from_file(file2_path)
    file2_offset = np.array([10000, 0, 0])
    
    file_out = merge_two(file1, file2, file1_offset, file2_offset)
    file_out.save(file_out_path)

main()