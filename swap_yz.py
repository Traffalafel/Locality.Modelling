import numpy as np
from ObjFile import ObjFile
from ObjFileFactory import ObjFileFactory
import sys

def swap_yz(file:ObjFile) -> ObjFile:

    vs_new = []
    for v in file.vertices:
        v_new = np.array([v[0], v[2], v[1]])
        vs_new.append(v_new)

    vts_new = []
    for vt in file.textures:
        vt_new = np.array([vt[0], vt[2], vt[1]])
        vts_new.append(vt_new)

    vns_new = []
    for vn in file.textures:
        vn_new = np.array([vn[0], vn[2], vn[1]])
        vns_new.append(vn_new)

    return ObjFile(
        vs_new,
        file.material_faces,
        textures=[],
        normals=[],
        details=file.details
    )

# def main():
#     file_path = sys.argv[1]
#     file = ObjFileFactory.from_file(file_path)
#     file = swap_yz(file)
#     file.print()

# main()