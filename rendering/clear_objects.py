import bpy

# Delete all existing objects
def clear_objects():
    for obj in bpy.data.objects:
        obj.select_set(True)
    bpy.ops.object.delete()
    
clear_objects()