import os
import bpy 

file_extension = "ply"
model_name = "aarhus"
mesh_position = "1_1"
mesh_file_dir = r"C:\Users\traff\source\repos\Locality.Modelling\data\models\aarhus_ply"
mesh_types = [
    'terrain',
    'buildings',
    'trees',
    'green',
    'water',
    'roads'
]

def import_mesh(path):
    bpy.ops.import_mesh.ply(filepath=path)

for mesh_type in mesh_types:
    
    mesh_file_name = f"{model_name} {mesh_position}_{mesh_type}.{file_extension}"    
    mesh_file_path = os.path.join(mesh_file_dir, mesh_file_name)
    print(mesh_file_name)
    
    import_mesh(mesh_file_path)
    bpy.data.objects[0].name = mesh_type
    