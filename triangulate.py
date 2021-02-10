import sys
import re
from Core import Face
from ObjFile import ObjFile
from ObjFileFactory import ObjFileFactory

def add(material_faces, face):
    material = face.material
    if material in material_faces:
        material_faces[material].append(face)
    else:
        material_faces[material] = [face]

def triangulate(file:ObjFile) -> ObjFile:
    
    material_faces_new = dict()
    for material in file.material_faces:
        for face in file.material_faces[material]:
            
            if len(face.vs) == 3:
                add(material_faces_new, face)

            if len(face.vs) == 4:
                
                vs1 = [v for i,v in enumerate(face.vs) if i != 0]
                if face.vts is not None:
                    vts1 = [v for i,v in enumerate(face.vts) if i != 0]
                else:
                    vts1 = None
                if face.vns is not None:
                    vns1 = [v for i,v in enumerate(face.vns) if i != 0]
                else:
                    vns1 = None
                face1 = Face(vs=vs1, vts=vts1, vns=vns1, material=material)
                
                vs2 = [v for i,v in enumerate(face.vs) if i != 2]
                if face.vts is not None:
                    vts2 = [v for i,v in enumerate(face.vts) if i != 2]
                else:
                    vts2 = None
                if face.vns is not None:
                    vns2 = [v for i,v in enumerate(face.vns) if i != 2]
                else:
                    vns2 = None
                face2 = Face(vs=vs2, vts=vts2, vns=vns2, material=material)

                # Set new faces
                add(material_faces_new, face1)
                add(material_faces_new, face2)
                continue
        
    return ObjFile(
        file.vertices, 
        material_faces_new, 
        file.textures, 
        file.normals, 
        file.details
    )

# def main():
#     file_path = sys.argv[1]
#     file = ObjFileFactory.from_file(file_path)
#     file = triangulate(file)
#     file.print()

# main()