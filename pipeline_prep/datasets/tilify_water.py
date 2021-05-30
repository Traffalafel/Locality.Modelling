import re
import geopandas
from shapely.geometry import Polygon
from rasterio.crs import CRS
import os

INPUT_FILE_PATH = r"D:\data\datasets\raw\OSM_water\water_union.shp"
OUTPUT_DIR_PATH = r"D:\data\datasets\OSM_water\10x10"

BLOCKS_FILE_PATH = r"D:\data\metadata\10x10 km blocks.csv"
TILE_SIZE_METRES = 10000
ETRS89_UTM32N = 25832

def main():

    print("Reading shapefile")
    df = geopandas.read_file(INPUT_FILE_PATH)
    df = df.to_crs(ETRS89_UTM32N)
    print("Done")
    
    with open(BLOCKS_FILE_PATH, 'r') as fd:
        content = fd.read()
        
    pattern = re.compile("(\d+)_(\d+)")
    for x, y in pattern.findall(content):
        
        x = int(x)
        y = int(y)

        file_name_shp = f"{x}_{y}.shp"
        file_path_shp = os.path.join(OUTPUT_DIR_PATH, file_name_shp)
        if os.path.exists(file_path_shp):
            # print(f"{file_path_shp} already exists. Skipping...")
            continue 

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

        # Clip file
        try:
            df_block = geopandas.clip(df, df_polygon)
        except:
            print(f"Error trying to clip {file_name_shp}. Skipping...")
    
        if len(df_block) == 0:
            print(f"{x}_{y} has no shapes. Skipping...")
            continue

        # Save shp file
        df_block.to_file(file_path_shp)

        print(file_name_shp)

main()