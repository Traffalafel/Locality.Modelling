import sys

blender_render_path = r"C:\Users\traff\source\repos\Locality.Modelling\rendering"
sys.path.append(blender_render_path)
from blender_render import clear_objects, render, import_materials

def main():

    if len(sys.argv) != 4+4:
        print("-----\nERROR\n-----")
        print("Usage: blender -b -P run_render.py -- <model_name> <model_width> <model_height>")
        return

    model_name = sys.argv[5]
    model_width = int(sys.argv[6])
    model_height = int(sys.argv[7])

    clear_objects()
    import_materials()
    render(model_name, model_width, model_height)

main()
