import numpy as np
import sys
from ObjFile import ObjFile
from ObjFileFactory import ObjFileFactory
from merge import merge_two
from normalize import normalize

def main():
    file_in_path = sys.argv[1]
    file_out_path = sys.argv[2]
    new_max = float(sys.argv[3])
    
    file = ObjFileFactory.from_file(file_in_path)
    normalize(file, new_max)
    file.save(file_out_path)

main()