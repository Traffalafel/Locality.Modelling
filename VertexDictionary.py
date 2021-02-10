import numpy as np

class VertexDictionary():
    def __init__(self, rounding_val=8):
        self.vertices = dict()
        self.rounding_val = rounding_val

    def set(self, vertex:np.ndarray, value):
        x = round(vertex[0], self.rounding_val)
        y = round(vertex[1], self.rounding_val)
        z = round(vertex[2], self.rounding_val)
        if x not in self.vertices:
            self.vertices[x] = dict()
        if y not in self.vertices[x]:
            self.vertices[x][y] = dict()
            
        self.vertices[x][y][z] = value
    
    def get(self, vertex:np.ndarray):
        x = round(vertex[0], self.rounding_val)
        y = round(vertex[1], self.rounding_val)
        z = round(vertex[2], self.rounding_val)
        if x not in self.vertices:
            return None
        if y not in self.vertices[x]:
            return None
        if z not in self.vertices[x][y]:
            return None
        else:
            return self.vertices[x][y][z]

    def contains(self, vertex:np.ndarray):
        x = round(vertex[0], self.rounding_val)
        y = round(vertex[1], self.rounding_val)
        z = round(vertex[2], self.rounding_val)
        if x not in self.vertices:
            return False
        if y not in self.vertices[x]:
            return False
        if z not in self.vertices[x][y]:
            return False
        else:
            return True

    def keys(self):
        keys = []
        xs = self.vertices.keys()
        for x in xs:
            ys = self.vertices[x].keys()
            for y in ys:
                zs = self.vertices[x][y].keys()
                for z in zs:
                    keys.append(np.array([x,y,z]))
        return keys