import numpy as np
from ObjFileFactory import ObjFileFactory
from ObjFile import ObjFile
import sys

def normalize(file:ObjFile, new_max):

    x_min = min(v[0] for v in file.vertices)
    x_max = max(v[0] for v in file.vertices)
    transform_x = -x_min
    scale = (1 / (x_max - x_min)) * new_max

    z_min = min(v[2] for v in file.vertices)
    z_max = max(v[2] for v in file.vertices)
    transform_z = -z_min
    scale = (1 / (z_max - z_min)) * new_max

    y_min = min(v[1] for v in file.vertices)
    transform_y = -y_min

    def normalize(v):
        return np.array([(v[0]+transform_x)*scale, (v[1]+transform_y)*scale, (v[2]+transform_z)*scale])
    
    file.vertices = [normalize(vertex) for vertex in file.vertices]
