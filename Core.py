import numpy as np

Vertex = np.ndarray

class Face():
    def __init__(self, vertices_idxs, material=None):
        self.vertices_idxs = vertices_idxs
        self.material = material

class Bounds():
    def __init__(self, north, west, south, east):
        self.north = north
        self.west = west
        self.south = south
        self.east = east

