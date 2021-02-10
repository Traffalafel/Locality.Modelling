import numpy as np
from VertexDictionary import VertexDictionary
from Core import Face
from ObjFile import ObjFile

def find_unique_idxs(polygons, get_vertices_fn):

    # Find all unique vertices and keep track of which faces reference them
    idx = 0
    unique_vertices = VertexDictionary()
    for polygon in polygons:
        vertices = get_vertices_fn(polygon)
        if vertices is None:
            continue
        for vertex in vertices:
            if (unique_vertices.contains(vertex)):
                values = unique_vertices.get(vertex)
                values.append(idx)
            else:
                unique_vertices.set(vertex, [idx])
            idx += 1

    # Set an index for each unique vertex
    idx = 0
    unique_idxs = VertexDictionary()
    for key in unique_vertices.keys():
        unique_idxs.set(key, idx)
        idx += 1

    return unique_idxs

def polygons_to_file(polygons):

    # Get unique vs and the idxs of faces that reference them
    def get_vs(polygon):
        return polygon.vs
    vs_idxs = find_unique_idxs(polygons, get_vs)
    vs_unique = vs_idxs.keys()
    
    # Get unique vts and the idxs of faces that reference them
    def get_vts(polygon):
        return polygon.vts
    vts_idxs = find_unique_idxs(polygons, get_vts)
    vts_unique = vts_idxs.keys()
    
    # Get unique vts and the idxs of faces that reference them
    def get_vns(polygon):
        return polygon.vns
    vns_idxs = find_unique_idxs(polygons, get_vns)
    vns_unique = vns_idxs.keys()
    
    # Construct new faces for these unique vertices
    material_faces = dict()
    for polygon in polygons:
        vertices = [vs_idxs.get(vertex) for vertex in polygon.vs]

        if polygon.vts is not None:
            vts = [vts_idxs.get(vt) for vt in polygon.vts]
        else:
            vts = None
        
        if polygon.vns is not None:
            vns = [vns_idxs.get(vn) for vn in polygon.vns]
        else:
            vns = None

        face = Face(vertices, vts, vns, polygon.material)

        if face.material in material_faces:
            material_faces[face.material].append(face)
        else:
            material_faces[face.material] = [face]

    file = ObjFile(vs_unique, material_faces, vts_unique, vns_unique)
    return file