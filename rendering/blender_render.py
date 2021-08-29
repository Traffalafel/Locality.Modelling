import bpy
import math
import os

MODELS_DIR_PATH = r"C:\Users\traff\source\repos\Locality.Modelling\data\models"
MATERIALS_FILE_PATH = r"C:\Users\traff\Documents\blender\Materials.blend"
RENDER_DIR_PATH = r"C:\Users\traff\Documents\Locality\Graphics\Renders\output"
MESH_TYPES = [
    'terrain',
    'buildings',
    'trees',
    'green',
    'water',
    'roads'
]
MATERIAL_MAPPINGS = {
    'terrain': 'terrain',
    'buildings': 'buildings',
    'water': 'water',
    'roads': 'roads',
    'green': 'green',
    'trees': 'green'
}
FRAME_MATERIAL_NAME = "frame_black"

def clear_objects():
    for obj in bpy.data.objects:
        obj.select_set(True)
    bpy.ops.object.delete()

def import_mesh(path):
    bpy.ops.import_mesh.ply(filepath=path)

def import_materials():

    with bpy.data.libraries.load(MATERIALS_FILE_PATH) as (data_from, data_to):
        
        data_to.materials = data_from.materials

        for mat in data_from.materials:
            if mat is not None:
                print(mat)

def assign_material(object, material):
    if object.data.materials:
        object.data.materials[0] = material
    else:
        object.data.materials.append(material)

def assign_model_materials(MATERIAL_MAPPINGS, mesh_position):

    for type_mesh, type_material in MATERIAL_MAPPINGS.items():
    
        mesh_name = f"{mesh_position} {type_mesh}"
        object = bpy.data.objects.get(mesh_name)

        material_name = f"plastic_{type_material}"
        material = bpy.data.materials.get(material_name)
        
        assign_material(object, material)

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

def create_frame_cube(name, location, size):
    bpy.ops.mesh.primitive_cube_add(size=1)
    cube = bpy.context.selected_objects[0]
    cube.name = name
    cube.location = location
    cube.scale = size
    frame_material = bpy.data.materials.get(FRAME_MATERIAL_NAME)
    assign_material(cube, frame_material)

# Create camera object linked to scene
def create_camera(name, location, rotation):
    scene = bpy.context.scene
    camera = bpy.data.cameras.new(name)
    camera_obj = bpy.data.objects.new(name, camera)
    scene.collection.objects.link(camera_obj)
    camera_obj.location = location
    camera_obj.rotation_euler = rotation
    return camera_obj

def render_image(camera, file_name):
    bpy.context.scene.camera = camera
    render_out_path = os.path.join(RENDER_DIR_PATH, f"{file_name}.png")
    bpy.context.scene.render.filepath = render_out_path
    bpy.ops.render.render(write_still = True)


def render(model_name, model_width, model_height, mesh_position="1_1", file_extension="ply"):

    width = model_width / 100
    height = model_height / 100

    # Import meshes
    mesh_dir_path = os.path.join(MODELS_DIR_PATH, f"{model_name}_{file_extension}")
    for mesh_type in MESH_TYPES:
        
        mesh_name = f"{model_name} {mesh_position}_{mesh_type}"
        mesh_file_name = f"{mesh_name}.{file_extension}"  
        mesh_file_path = os.path.join(mesh_dir_path, mesh_file_name)

        import_mesh(mesh_file_path)
        
        mesh_name_new = f"{mesh_position} {mesh_type}"
        bpy.data.objects.get(mesh_name).name = mesh_name_new

    assign_model_materials(MATERIAL_MAPPINGS, mesh_position)

    # Create camera 1
    camera1_x = width / 2
    camera1_y = height / 2
    camera1_z = max(camera1_x, camera1_y) * 3
    camera1_location = (camera1_x, camera1_y, camera1_z)
    camera1_rotation = (0, 0, 0) # Down
    camera1 = create_camera("Camera 1", camera1_location, camera1_rotation)

    # Create camera 2
    camera2_x = 0.1 * max(width, height)
    camera2_y = height/2
    camera2_z = (5/3) * max(width, height)
    camera2_location = (camera2_x, camera2_y, camera2_z)
    camera2_rotation = (0, -math.pi/14, 0)
    camera2 = create_camera("Camera 2", camera2_location, camera2_rotation)

    # Create sun light
    sun_rotation = (0, -math.pi * 0.1, 0)
    sun_energy = 1.25
    create_light_sun(sun_energy, sun_rotation)

    # Create spot light
    spot_rotation = (0, math.pi * 0.1, 0)
    spot_energy = 400
    spot_location_x = camera1_x * 2.5
    spot_location_y = camera1_y
    spot_location_z = camera1_z * 2 / 3
    spot_location = (spot_location_x, spot_location_y, spot_location_z)
    create_light_spot(spot_energy, spot_rotation, spot_location)

    # Set render settings
    bpy.context.scene.render.resolution_x = 2000
    bpy.context.scene.render.resolution_y = 2000
    bpy.context.scene.render.image_settings.color_mode = "RGBA"
    bpy.context.scene.render.film_transparent = True

    # Create frame from 4 rectangular cubes
    frame_width = 0.2
    frame_depth = 0.15
    center_x = width/2
    center_y = height/2
    horizontal_frame_scale = (width + frame_width*2, frame_width, frame_depth)
    vertical_frame_scale = (frame_width, height, frame_depth)
    create_frame_cube("Top", (center_x, height + frame_width/2, frame_depth/2), horizontal_frame_scale)
    create_frame_cube("Bot", (center_x, -frame_width/2, frame_depth/2), horizontal_frame_scale)
    create_frame_cube("Left", (-frame_width/2, center_y, frame_depth/2), vertical_frame_scale)
    create_frame_cube("Right", (width + frame_width/2, center_y, frame_depth/2), vertical_frame_scale)

    # Render images
    render_image(camera1, f"{model_name} render 1")
    render_image(camera2, f"{model_name} render 2")