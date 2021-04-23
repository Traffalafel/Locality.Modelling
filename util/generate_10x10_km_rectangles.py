import re
import geopandas
from shapely.geometry import Polygon
from rasterio.crs import CRS
import os

OUTPUT_DIR_PATH = r"D:\data\shapes\10x10\rectangles"

BLOCKS_FILE_PATH = r"D:\data\metadata\10x10 km blocks.csv"
TILE_SIZE_METRES = 10000
ETRS89_UTM32N = 25832

def main():
    
    with open(BLOCKS_FILE_PATH, 'r') as fd:
        content = fd.read()
        
    pattern = re.compile("(\d+)_(\d+)")
    for x, y in pattern.findall(content):
        
        x = int(x)
        y = int(y)

        bound_w = x * TILE_SIZE_METRES
        bound_e = (x+1) * TILE_SIZE_METRES
        bound_s = y * TILE_SIZE_METRES
        bound_n = (y+1) * TILE_SIZE_METRES

        polygon = Polygon([
            (bound_w, bound_s),
            (bound_w, bound_n),
            (bound_e, bound_n),
            (bound_e, bound_s)
        ])
        df_polygon = geopandas.GeoDataFrame([1], geometry=[polygon], crs=CRS.from_epsg(ETRS89_UTM32N))

        file_name_shp = f"{x}_{y}.shp"
        print(file_name_shp)

        # Save shp file
        file_path_shp = os.path.join(OUTPUT_DIR_PATH, file_name_shp)
        df_polygon.to_file(file_path_shp)

main()