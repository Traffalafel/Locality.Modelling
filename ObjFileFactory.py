import numpy as np
import re
from ObjFile import ObjFile, ObjFileDetails
from Core import Face

class ObjFileFactory():
    def __init__(self):
        pass

    @staticmethod
    def from_file(file_path):

        def clean_line(line:str) -> str:
            line = line.replace('\n', '')
            line = re.sub(' +', ' ', line)
            line = line.strip()
            return line

        def parse_vertex(line):
            return np.array([float(v) for v in line.split(' ')])

        def parse_face(line):
            element_strings = line.split(' ')
            vertices_idxs = []
            for es in element_strings:
                terms = es.split('/')
                v = int(terms[0])
                if v > 0:
                    v -= 1
                if v < 0:
                    v = count_v + v
                vertices_idxs.append(v)
            if material_state is not None:
                material = material_state
            else:
                material = material_state 
            return Face(vertices_idxs, material)

        count_v = 0
        vertices = []
        faces = []
        details = ObjFileDetails()
        material_state = None

        with open(file_path, 'r') as fd:
            lines = fd.readlines()

        for line in lines:
            line = clean_line(line)

            # Whitespace and comments
            if len(line) == 0:
                continue
            if line == " ":
                continue
            if line[0] == "#":
                continue

            # Vertex
            if line[:2] == "v ":
                v = parse_vertex(line[2:])
                vertices.append(v)
                count_v += 1
                continue

            # Face
            if line[:2] == "f ":
                f = parse_face(line[2:])
                faces.append(f)
                continue
            
            # MTL file path
            if line[:6] == "mtllib":
                mtl_path = line.split(' ')[1]
                details.mtl_path = mtl_path
                continue

            if line[:6] == "usemtl":
                material_state_new = line.split(' ')[1]
                material_state = material_state_new
                continue

        return ObjFile(vertices, faces, details)