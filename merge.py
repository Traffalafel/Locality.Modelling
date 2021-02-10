import numpy as np
from Core import Face
from ObjFile import ObjFile

def merge_two(file1:ObjFile, file2:ObjFile, file1_vertexoffset:np.ndarray, file2_vertexoffset:np.ndarray) -> ObjFile:

    assert(len(file1_vertexoffset) == 3)
    assert(len(file2_vertexoffset) == 3)

    # Merge vertices
    vertices_new = []
    for vertex in file1.vertices:
        vertices_new.append(vertex + file1_vertexoffset)
    for vertex in file2.vertices:
        vertices_new.append(vertex + file2_vertexoffset)

    # Merge faces
    file2_idxoffset = len(file1.vertices)
    faces_new = file1.faces.copy()
    for face in file2.faces:
        face.vertices_idxs = [v + file2_idxoffset for v in face.vertices_idxs]
        faces_new.append(face)
    
    return ObjFile(vertices_new, faces_new)

# def merge(files, vertexoffsets):

#     # Make sure inputs have right sizes
#     assert(len(files) == len(vertexoffsets))
#     for vertexoffset in vertexoffsets:
#         assert(len(vertexoffset) == 3)

#     # Vertices
#     vertices_new = []
#     for idx, file in enumerate(files):
#         vertexoffset = vertexoffsets[idx]
#         for vertex in file.vertices:
#             vertices_new.append(vertex + vertexoffset)

#     # Faces
#     idxoffset = 0
#     faces_new = []
#     for idx, file in enumerate(files):
#         for face in file.faces:
#             vs = [v + idxoffset for v in face.vs]
#             if face.vts is not None:
#                 vts = face.vts.copy()
#             else:
#                 vts = None
#             if face.vns is not None:
#                 vns = face.vns.copy()
#             else:
#                 vns = None
#             face_new = Face(vs, vts, vns)
#             faces_new.append(face_new)
#         idxoffset += len(file.vertices)

#     return ObjFile(vertices_new, faces_new)