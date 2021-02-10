from ObjFileFactory import ObjFileFactory
import sys

file_path = sys.argv[1]
file = ObjFileFactory.from_file(file_path)

vertices = list(file.vertices)
faces = list(file.faces)

print(f"number of vertices: {len(vertices)}")
print(f"number of faces: {len(faces)}")
print(f"min_x: {min(v[0] for v in vertices)}")
print(f"max_x: {max(v[0] for v in vertices)}")
print(f"min_y: {min(v[1] for v in vertices)}")
print(f"max_y: {max(v[1] for v in vertices)}")
print(f"min_z: {min(v[2] for v in vertices)}")
print(f"max_z: {max(v[2] for v in vertices)}")
