import os
from Range import Range

class File():

    def __init__(self, path, x_min: int, y_min: int, size_metres=1000):
        
        self.path = path
        self.file_name = os.path.basename(path)
        
        x_max = x_min + size_metres - 1
        y_max = y_min + size_metres - 1
        self.range = Range(x_min, x_max, y_min, y_max)
