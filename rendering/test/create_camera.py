import bpy

location = (100, 100, 100)

# Create camera object linked to scene
scene = bpy.context.scene
camera = bpy.data.cameras.new("Camera")
camera_obj = bpy.data.objects.new("Camera", camera)
scene.collection.objects.link(camera_obj)

# Set camera params
camera_obj.location = location
camera_obj.rotation_euler = (0, 0, 0)
