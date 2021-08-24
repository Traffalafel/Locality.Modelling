import bpy

# Arguments
X = 0
Y = 0
Z = 0

scene = bpy.data.scenes[0]
scene.camera.location.x = X
scene.camera.location.y = Y
scene.camera.location.z = Z

