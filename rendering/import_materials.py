import bpy

def import_materials(blend_file_path):

    with bpy.data.libraries.load(blend_file_path) as (data_from, data_to):
        
        data_to.materials = data_from.materials

        for mat in data_from.materials:
            if mat is not None:
                print(mat)

materials_file_path = r"C:\Users\traff\Documents\blender\Materials.blend"
import_materials(materials_file_path)