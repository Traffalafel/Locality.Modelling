import numpy as np
import re
from Core import Vertex, Face

class ObjFileDetails():
    def __init__(self, mtl_path=None):
        self.mtl_path = mtl_path

class ObjFile():
    def __init__(self, vertices, faces, details=None):
        self.vertices = vertices
        self.faces = faces
        self.details = details

    def generate_lines(self):
        lines = []

        # Path to MTL file
        if self.details is not None:
            if self.details.mtl_path is not None:
                lines.append(f'mtllib {self.details.mtl_path}')

        def format_idxs(idxs):
            return [idx+1 if idx>=0 else idx for idx in idxs]
            
        for vertex in self.vertices:
            line = "v "
            line += ' '.join(str(v) for v in vertex)
            lines.append(line)

        # Get all materials and their corresponding faces
        material_faces = dict()
        for face in self.faces:
            if face.material in material_faces:
                material_faces[face.material].append(face)
            else:
                material_faces[face.material] = [face]

        for material in material_faces:
            
            if material is not None:
                line = f"usemtl {material}"
                lines.append(line)
            
            for face in material_faces[material]:
                idxs = format_idxs(face.vertices_idxs)
                line = f"f {idxs[0]} {idxs[1]} {idxs[2]}"
                lines.append(line)

        return lines

    def save(self, file_path):
        lines = self.generate_lines()
        with open(file_path, 'w+') as fd:
            fd.write('\n'.join(lines))

    def print(self):
        lines = self.generate_lines()
        for line in lines:
            print(line)