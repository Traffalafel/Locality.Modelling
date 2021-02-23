import re
import os
import sys
from shutil import copyfile
import re

def get_dir_files(dir_path):
    contents = os.listdir(dir_path)
    files = [c for c in contents if os.path.isfile(os.path.join(dir_path, c))]
    files_tif = [f for f in files if f.split(".")[1] == "tif"]
    return files_tif

def main():
    dir_path = sys.argv[1]
    files = get_dir_files(dir_path)

    pattern = re.compile(r"^DTM_1km_(\d+)_(\d+)\.tif$")


    for file in files:

        match = pattern.search(file)

        if match is None:
            continue

        y = match.group(1)
        x = match.group(2)
        file_name_new = f"{x}_{y}.tif"
        file_path_new = os.path.join(dir_path, file_name_new)
        file_path_old = os.path.join(dir_path, file)
        
        copyfile(file_path_old, file_path_new)
        os.remove(file_path_old)

        print(file_name_new)

main()
