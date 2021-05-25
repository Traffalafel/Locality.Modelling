import re
import geopandas
from shapely.geometry import Polygon
from rasterio.crs import CRS
import os

INPUT_FILE_PATH = r"D:\data\datasets\GeoDanmark\BYGNINGER\BYGNING.shp"
OUTPUT_DIR_PATH = r"D:\data\datasets\GeoDanmark_buildings\10x10"

BLOCKS_FILE_PATH = r"D:\data\metadata\10x10 km blocks.csv"
TILE_SIZE_METRES = 10000
ETRS89_UTM32N = 25832
CLIP_MARGIN_EXTRA = 500

def main():

    with open(BLOCKS_FILE_PATH, 'r') as fd:
        content = fd.read()
        
    pattern = re.compile("(\d+)_(\d+)")
    for x, y in pattern.findall(content):
        
        x = int(x)
        y = int(y)

        file_name_shp = f"{x}_{y}.shp"
        file_path_shp = os.path.join(OUTPUT_DIR_PATH, file_name_shp)
        if os.path.exists(file_path_shp):
            print(f"{file_path_shp} already exists. Skipping...")
            continue 

        bound_w = x * TILE_SIZE_METRES - CLIP_MARGIN_EXTRA
        bound_e = (x+1) * TILE_SIZE_METRES + CLIP_MARGIN_EXTRA
        bound_s = y * TILE_SIZE_METRES - CLIP_MARGIN_EXTRA
        bound_n = (y+1) * TILE_SIZE_METRES + CLIP_MARGIN_EXTRA

        bbox = (bound_w, bound_s, bound_e, bound_n)
        df = geopandas.read_file(
            INPUT_FILE_PATH,
            bbox=bbox
        )
    
        if len(df) == 0:
            print(f"{x}_{y} has no shapes. Skipping...")
            continue

        # Save shp file
        df.to_file(file_path_shp)

        print(f"Saved {file_name_shp}")

main()