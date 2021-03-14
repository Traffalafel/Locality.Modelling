import sys
import re
import numpy as np
from Core import Bounds, Plane, Polygon
from ObjFileFactory import ObjFileFactory
from ObjFile import ObjFile
from VertexDictionary import VertexDictionary
from deduplication import polygons_to_file

def generate_planes(bounds:Bounds):
    west = Plane(1.0, 0.0, 0.0, -bounds.west)
    north = Plane(0.0, 0.0, -1.0, bounds.north)
    east = Plane(-1.0, 0.0, 0.0, bounds.east)
    south = Plane(0.0, 0.0, 1.0, -bounds.south)
    return [west, north, south, east]

def plane_distance(point:np.ndarray, plane:Plane):
    assert(len(point) == 3)
    D = plane.d
    N = plane.get_normal()
    return np.dot(N, point) + D

def segment_intersection(A:np.ndarray, B:np.ndarray, plane:Plane):
    assert(len(A) == 3)
    assert(len(B) == 3)
    D = plane.d
    N = plane.get_normal()
    t = (- D - np.dot(N,A)) / np.dot(N,B-A)
    Q = A + t * (B-A)
    return Q

def clip_face(file, idxs_global_inside, face, clipping_plane):
    
    # Get the face vertices inside and outside
    vs_idxs_inside = [idx for idx in face.vs if idx in idxs_global_inside]
    vs_idxs_outside = [idx for idx in face.vs if idx not in vs_idxs_inside]
    count_inside = len(vs_idxs_inside)

    polygons_new = []
    boundary_edge = None

    if count_inside == 0:
        # 3 outside
        return polygons_new, boundary_edge

    # Get vertices
    vertices_inside = [file.vertices[idx] for idx in vs_idxs_inside]
    vertices_outside = [file.vertices[idx] for idx in vs_idxs_outside]

    if count_inside == 1:
        # 1 inside, 2 outside
        A = vertices_inside[0]
        B = vertices_outside[0]
        C = vertices_outside[1]
        B_new = segment_intersection(A, B, clipping_plane)
        C_new = segment_intersection(A, C, clipping_plane)
        p = Polygon(
            vs=[A, B_new, C_new],
            material=face.material
        )
        polygons_new.append(p)
        boundary_edge = [B_new, C_new]

    if count_inside == 2:
        # 2 inside, 1 outside
        A = vertices_inside[0]
        B = vertices_inside[1]
        C = vertices_outside[0]
        A_new = segment_intersection(A, C, clipping_plane)
        B_new = segment_intersection(B, C, clipping_plane)
        p1 = Polygon(
            vs=[A, A_new, B_new],
            material=face.material
        )
        p2 = Polygon(
            vs=[B, A, B_new],
            material=face.material
        )
        polygons_new.append(p1)
        polygons_new.append(p2)
        boundary_edge = [A_new, B_new]
    
    if count_inside == 3:
        # 3 inside
        p = Polygon(
            vs=vertices_inside,
            material=face.material
        )
        polygons_new.append(p)

    return polygons_new, boundary_edge

def clip_file(file, clipping_plane:Plane):

    # Find out which vertices are inside clipping plane
    idxs_global_inside = set()
    for idx, vertex in enumerate(file.vertices):
        if plane_distance(vertex, clipping_plane) >= 0:
            idxs_global_inside.add(idx)

    # Get new face vertices and boundary edges
    polygons_new = []
    boundary_edges_new = []
    for face in file.get_faces():
        polygons, boundary_edge = clip_face(file, idxs_global_inside, face, clipping_plane)
        for polygon in polygons:
            polygons_new.append(polygon)
        if boundary_edge is not None:
            boundary_edges_new.append(boundary_edge)

    # Deduplicate
    file_clipped = polygons_to_file(polygons_new)
    file_clipped.details = file.details
    return file_clipped

def preprocess(file, bounds):

            
    material_faces_new = dict()
    for material in file.material_faces:
        for face in file.material_faces[material]:
            vertices = [file.vertices[v] for v in face.vs]

            # Skip if outside one of the bounds
            if all(v[0] < bounds.west for v in vertices):
                continue
            if all(v[0] > bounds.east for v in vertices):
                continue
            if all(v[2] < bounds.south for v in vertices):
                continue
            if all(v[2] > bounds.north for v in vertices):
                continue

            # Add face
            if material in material_faces_new:
                material_faces_new[material].append(face)
            else:
                material_faces_new[material] = [face]

    return ObjFile(
        file.vertices,
        material_faces_new,
        file.textures,
        file.normals,
        file.details
    )

def main():

    # Load args
    file_path = sys.argv[1]
    try:
        clipping_north = float(sys.argv[2])
        clipping_west = float(sys.argv[3])
        clipping_south = float(sys.argv[4])
        clipping_east = float(sys.argv[5])
    except Exception as e:
        raise Exception(f"Error: could not parse input bounds. Error: {e}")

    # Generate clipping planes
    clipping_bounds = Bounds(
        north = clipping_north,
        west = clipping_west,
        south = clipping_south,
        east = clipping_east
    )
    clipping_planes = generate_planes(clipping_bounds)

    # Load model data
    file = ObjFileFactory.from_file(file_path)

    file = preprocess(file, clipping_bounds)

    # Clip model
    for plane in clipping_planes:
        file = clip_file(file, plane)

    file.print()

main()
