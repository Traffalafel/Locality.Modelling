import os
import geopandas
import rasterio
import rasterio.features
import shapely.geometry
import numpy as np
from rasterio.crs import CRS
from . import constants

def get_file_name(file_path):
    _, file_name = os.path.split(file_path)
    file_name = file_name.split('.')[0]
    return file_name

def get_file_bounds(file_name):
    file_name = file_name.split('.')[0]
    min_x = int(file_name.split('_')[0]) * constants.TILE_SIZE
    max_x = min_x + constants.TILE_SIZE
    min_y = int(file_name.split('_')[1]) * constants.TILE_SIZE
    max_y = min_y + constants.TILE_SIZE
    return (min_x, max_x, min_y, max_y)

def get_file_extension(file):
    return file.split('.')[1]

def get_directory_file_paths(dir_path, extension=None):
    contents = os.listdir(dir_path)
    files = [c for c in contents if os.path.isfile(os.path.join(dir_path, c))]
    file_paths = [os.path.join(dir_path, f) for f in files]

    if extension is not None:
        file_paths = [path for path in file_paths if get_file_extension(path) == extension]
    
    return file_paths

def get_directory_file_names(dir_path):
    contents = os.listdir(dir_path)
    files = [c for c in contents if os.path.isfile(os.path.join(dir_path, c))]
    return files

def clip(dataframe, bounds):
    bounds_w, bounds_e, bounds_s, bounds_n = bounds
    polygon = shapely.geometry.Polygon([
        (bounds_w, bounds_s),
        (bounds_w, bounds_n),
        (bounds_e, bounds_n),
        (bounds_e, bounds_s)
    ])
    poly_gdf = geopandas.GeoDataFrame([1], geometry=[polygon], crs=dataframe.crs)
    df_out = geopandas.clip(dataframe, poly_gdf)
    return df_out

def rasterize(dataframe, n_pixels, bounds, all_touched=False):
    x_min, x_max, y_min, y_max = bounds
    transform = rasterio.transform.from_bounds(
        west = x_min,
        east = x_max,
        south = y_min,
        north = y_max,
        height = n_pixels,
        width = n_pixels
    )
    pixels = rasterio.features.rasterize(
        shapes=dataframe['geometry'],
        out_shape=(n_pixels, n_pixels),
        fill=0,
        transform=transform,
        all_touched=all_touched,
        default_value=1,
        dtype=np.uint8
    )
    return pixels, transform

def save_raster(values, file_path_out, transform):
    dataset = rasterio.open(
        file_path_out,
        mode="w",
        driver="GTiff",
        width=values.shape[1],
        height=values.shape[0],
        count=1,
        crs=CRS.from_epsg(constants.ETRS89_UTM32N),
        transform=transform,
        dtype=values.dtype
    )
    dataset.write(values, 1)

def filter_by_fclass(dataframe, fclasses):
    df_out = geopandas.GeoDataFrame(columns=['geometry', 'fclass'], crs=dataframe.crs)
    for _, row in dataframe.iterrows():
        fclass = row['fclass']
        if fclass not in fclasses:
            continue
        geometry = row['geometry']
        df_out.loc[len(df_out)] = [geometry, fclass]
    return df_out

def filter_by_geometry(dataframe, geometry):
    return dataframe[dataframe['geometry'].apply(lambda x: x.type == geometry)]