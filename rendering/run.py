import bpy
import math
import os

file_extension = "ply"
model_name = "blendertest"
mesh_position = "1_1"
width = 300
height = 300
models_dir_path = r"C:\Users\traff\source\repos\Locality.Modelling\data\models"
materials_file_path = r"C:\Users\traff\Documents\blender\Materials.blend"
mesh_types = [
    'terrain',
    'buildings',
    'trees',
    'green',
    'water',
    'roads'
]
material_mappings = {
    'terrain': 'terrain',
    'buildings': 'buildings',
    'water': 'water',
    'roads': 'roads',
    'green': 'green',
    'trees': 'green'
}
camera_rotation_euler = (0, 0, 0) # Down

def clear_objects():
    for obj in bpy.data.objects:
        obj.select_set(True)
    bpy.ops.object.delete()

def import_mesh(path):
    bpy.ops.import_mesh.ply(filepath=path)

def import_materials(blend_file_path):

    with bpy.data.libraries.load(blend_file_path) as (data_from, data_to):
        
        data_to.materials = data_from.materials

        for mat in data_from.materials:
            if mat is not None:
                print(mat)

def assign_materials(material_mappings):

    for type_mesh, type_material in material_mappings.items():
    
        mesh_name = f"{mesh_position} {type_mesh}"
        object = bpy.data.objects.get(mesh_name)

        material_name = f"plastic_{type_material}"
        material = bpy.data.materials.get(material_name)

        if object.data.materials:
            object.data.materials[0] = material
        else:
            object.data.materials.append(material)

def create_light_sun(energy, rotation_euler):
    light_data = bpy.data.lights.new(name="light_sun", type='SUN')
    light_data.energy = energy
    light_object = bpy.data.objects.new(name="light_sun", object_data=light_data)
    bpy.context.collection.objects.link(light_object)
    bpy.context.view_layer.objects.active = light_object
    light_object.rotation_euler = rotation_euler

def create_light_spot(energy, rotation_euler, location):
    light_data = bpy.data.lights.new(name="light_spot", type='SPOT')
    light_data.energy = energy
    light_object = bpy.data.objects.new(name="light_spot", object_data=light_data)
    bpy.context.collection.objects.link(light_object)
    bpy.context.view_layer.objects.active = light_object
    light_object.location = location
    light_object.rotation_euler = rotation_euler

clear_objects()

# Import meshes
mesh_dir_path = os.path.join(models_dir_path, f"{model_name}_{file_extension}")
for mesh_type in mesh_types:
    
    mesh_name = f"{model_name} {mesh_position}_{mesh_type}"
    mesh_file_name = f"{mesh_name}.{file_extension}"  
    mesh_file_path = os.path.join(mesh_dir_path, mesh_file_name)

    import_mesh(mesh_file_path)
    
    mesh_name_new = f"{mesh_position} {mesh_type}"
    bpy.data.objects.get(mesh_name).name = mesh_name_new

import_materials(materials_file_path)
assign_materials(material_mappings)

# Create camera object linked to scene
scene = bpy.context.scene
camera = bpy.data.cameras.new("Camera")
camera_obj = bpy.data.objects.new("Camera", camera)
scene.collection.objects.link(camera_obj)

# Set camera params
camera_x = width / 200
camera_y = height / 200
camera_z = max(camera_x, camera_y) * 7
camera_obj.location = (camera_x, camera_y, camera_z)
camera_obj.rotation_euler = camera_rotation_euler

# Create sun light
sun_rotation = (0, -math.pi * 0.1, 0)
sun_energy = 1.25
create_light_sun(sun_energy, sun_rotation)

# Create spot light
spot_rotation = (0, math.pi * 0.1, 0)
spot_energy = 400
spot_location_x = camera_x * 2.5
spot_location_y = camera_y
spot_location_z = camera_z * 2 / 3
spot_location = (spot_location_x, spot_location_y, spot_location_z)
create_light_spot(spot_energy, spot_rotation, spot_location)