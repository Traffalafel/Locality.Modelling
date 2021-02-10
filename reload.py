import sys
from ObjFileFactory import ObjFileFactory

def main():
    file_path_in = sys.argv[1]
    file_path_out = sys.argv[2]
    file = ObjFileFactory.from_file(file_path_in)
    file.save(file_path_out)

main()