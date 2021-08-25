import os
import bpy 

mesh_position = "1_1"
mappings = {
    'terrain': 'terrain',
    'buildings': 'buildings',
    'water': 'water',
    'roads': 'roads',
    'green': 'green',
    'trees': 'green'
}

for type_mesh, type_material in mappings.items():
    
    mesh_name = f"{mesh_position} {type_mesh}"
    object = bpy.data.objects.get(mesh_name)

    material_name = f"plastic_{type_material}"
    material = bpy.data.materials.get(material_name)

    # Assign material to object
    if object.data.materials:
        # assign to 1st material slot
        object.data.materials[0] = material
    else:
        # no slots
        object.data.materials.append(material)