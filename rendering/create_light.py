import bpy

light_location = (5,5,5)
light_energy = 30

# create light datablock, set attributes
light_data = bpy.data.lights.new(name="light_sun", type='SUN')
light_data.energy = light_energy

# create new object with our light datablock
light_object = bpy.data.objects.new(name="light_sun", object_data=light_data)

# link light object
bpy.context.collection.objects.link(light_object)

# make it active 
bpy.context.view_layer.objects.active = light_object

#change location
light_object.location = light_location
