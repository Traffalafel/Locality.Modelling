import numpy as np
import geopandas
import rasterio
import rasterio.features
from rasterio.crs import CRS
import os
from polygonize import polygonize
from clip import clip

# Args
FILE_IN_PATH = r"C:\data\OSM\landuse_cph.shp"
SHP_DIR_OUT_PATH = r"C:\data\shapes\green"
TIF_DIR_OUT_PATH = r"C:\data\masks\green"

ALL_TOUCHED = True
OFFSET_HALF = True

BOUNDS_W = 723
BOUNDS_E = 728
BOUNDS_S = 6175
BOUNDS_N = 6180

# Constants
TILE_SIZE = 1000
PIXEL_SIZE = 0.4
N_PIXELS_1x1 = int(TILE_SIZE / PIXEL_SIZE)
N_PIXELS_2x2 = int(TILE_SIZE / (PIXEL_SIZE * 2))

FCLASSES_GREEN = [
    "forest",
    "park",
    "allotments",
    "meadow",
    "nature_reserve",
    "recreation_ground",
    "orchard",
    "vineyard",
    "scrub",
    "grass",
    "heath",
    "national_park",
    "village_green",
    "plant_nursery",
    "farmland",
    "farmyard"
]

ETRS89_UTM32N = 25832

def filter_by_fclass(dataframe, fclasses):
    df_out = geopandas.GeoDataFrame(columns=['geometry', 'fclass'], crs=dataframe.crs)
    for idx, row in dataframe.iterrows():
        fclass = row['fclass']
        if fclass not in fclasses:
            continue
        geometry = row['geometry']
        df_out.loc[len(df_out)] = [geometry, fclass]
    return df_out

def rasterize(dataframe, n_pixels, x, y, offset):
    transform = rasterio.transform.from_bounds(
        west = x * TILE_SIZE + offset,
        east = (x+1) * TILE_SIZE + offset,
        south = y * TILE_SIZE + offset,
        north = (y+1) * TILE_SIZE + offset,
        height = n_pixels,
        width = n_pixels
    )
    pixels = rasterio.features.rasterize(
        shapes=dataframe['geometry'],
        out_shape=(n_pixels, n_pixels),
        fill=0,
        transform=transform,
        all_touched=ALL_TOUCHED,
        default_value=1,
        dtype=np.uint8
    )
    return pixels, transform

def save_raster(values, file_path, transform):
    dataset = rasterio.open(
        file_path,
        mode="w",
        driver="GTiff",
        width=values.shape[1],
        height=values.shape[0],
        count=1,
        crs=CRS.from_epsg(ETRS89_UTM32N),
        transform=transform,
        dtype=values.dtype
    )
    dataset.write(values, 1)

def main():

    if not os.path.exists(SHP_DIR_OUT_PATH):
        os.mkdir(SHP_DIR_OUT_PATH)
    if not os.path.exists(TIF_DIR_OUT_PATH):
        os.mkdir(TIF_DIR_OUT_PATH)

    df = geopandas.read_file(FILE_IN_PATH)
    df = df.to_crs(ETRS89_UTM32N)

    # Compute offset
    if OFFSET_HALF:
        offset = PIXEL_SIZE/2
    else:
        offset = 0

    for y in range(BOUNDS_S, BOUNDS_N):
        for x in range(BOUNDS_W, BOUNDS_E):
            
            file_name = f"{x}_{y}"
            
            # Define bounds and clip
            bounds = (
                x*TILE_SIZE + offset,
                (x+1)*TILE_SIZE + offset,
                y*TILE_SIZE + offset,
                (y+1)*TILE_SIZE + offset
            )
            df_tile = clip(df, bounds)
                
            df_tile = filter_by_fclass(df_tile, FCLASSES_GREEN)

            if len(df_tile) == 0:
                print(f"skipping {file_name}")
                continue

            # Save shp file
            file_name_shp = f"{file_name}.shp"
            file_path_shp = os.path.join(SHP_DIR_OUT_PATH, file_name_shp)
            df_tile.to_file(file_path_shp)

            file_name_tif = f"{file_name}.tif"

            # Rasterize and save 1x1 
            file_path_1x1 = os.path.join(TIF_DIR_OUT_PATH, "1x1", file_name_tif)
            pixels_1x1, transform_1x1 = rasterize(df_tile, N_PIXELS_1x1, x, y, offset)
            save_raster(pixels_1x1, file_path_1x1, transform_1x1)
            
            # Rasterize and save 2x2 
            file_path_2x2 = os.path.join(TIF_DIR_OUT_PATH, "2x2", file_name_tif)
            pixels_2x2, transform_2x2 = rasterize(df_tile, N_PIXELS_2x2, x, y, offset)
            save_raster(pixels_2x2, file_path_2x2, transform_2x2)

            print(f"saved {file_name}")

main()