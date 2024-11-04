import numpy as np
from pyproj import Transformer
import os
import rasterio.merge
from meshify import meshify_surface
import argparse
from File import File
from Surface import Surface
from Range import Range
import re
import rasterio
from skimage.util import view_as_blocks

# Constants
OUTPUT_FORMAT = "stl"
DEFAULT_PIXEL_SIZE = 0.4
CRS_WGS84 = 4326
CRS_ETRS89 = 25832
HEIGHTS_EXTRA = 5
HEIGHTS_MULTIPLIER = 1
FILE_PATTERN = r"DSM_1km_(\d+)_(\d+)\.tif"

# Splits the 2-d surface array into surface tiles
def get_tiles(surface: Surface, num_tiles_x: int, num_tiles_y: int) -> np.ndarray:
    tiles_shape = (surface.data.shape[0] // num_tiles_x, surface.data.shape[1] // num_tiles_y)
    reshaped = surface.data.reshape(num_tiles_x, tiles_shape[0], num_tiles_y, tiles_shape[1])
    tiles = reshaped.swapaxes(1, 2)
    return tiles

# Aggregates surface by taking the max of these
def aggregate(surface: Surface, aggregate_size: int) -> Surface:
    block_size = (aggregate_size, aggregate_size)
    blocks = view_as_blocks(surface.data, block_size)
    max_values = np.max(blocks, axis=(2, 3))
    return Surface(max_values, surface.range)

# Gets surface 2-d array from coordinate range
def get_surface(data_dir: str, range: Range, pixel_size: float) -> Surface:
    files = parse_data_dir(data_dir)
    files = [file for file in files if file.range.is_overlapping(range)]
    data = read_files_data(files)

    files_x_min = min(file.range.x_min for file in files)
    files_y_min = min(file.range.y_min for file in files)

    idx_x_min = int((range.x_min - files_x_min) / pixel_size)
    idx_x_max = idx_x_min + int(range.width / pixel_size)
    idx_y_min = int((range.y_min - files_y_min) / pixel_size)
    idx_y_max = idx_y_min + int(range.height / pixel_size)

    data = data[idx_x_min:idx_x_max, idx_y_min:idx_y_max]

    return Surface(data, range)

def read_files_data(files: list[File]) -> np.ndarray:
    datasets = []
    for file in files: 
        ds = rasterio.open(file.path)
        datasets.append(ds)
    contents, _  = rasterio.merge.merge(datasets)
    data = contents[0,:,:]
    data = np.flip(data, axis=0)
    data = np.transpose(data)
    return data

# Gets all files in a directory path which match the FILE_PATTERN
# and creates File object containing data on their coordinate ranges
def parse_data_dir(dir_path: str) -> list[File]:
    data_dir_files = os.listdir(dir_path)
    files = []
    for file_name in data_dir_files:

        match = re.match(FILE_PATTERN, file_name)
        if match is None:
            continue

        y_min_km = int(match.group(1))
        y_min_m = y_min_km * 1000

        x_min_km = int(match.group(2))
        x_min_m = x_min_km * 1000

        file_path = os.path.join(dir_path, file_name)
        file = File(file_path, x_min_m, y_min_m)
        files.append(file)

    return files

def convert_coordinates(center_lat: float, center_lng: float, width: int, height: int) -> Range:
    transformer = Transformer.from_crs(CRS_WGS84, CRS_ETRS89)
    center_x, center_y = transformer.transform(center_lat, center_lng)
    x_min = int(center_x - width/2)
    x_max = int(center_x + width/2)
    y_min = int(center_y - height/2)
    y_max = int(center_y + height/2)
    return Range(x_min, x_max, y_min, y_max)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir", help="Path to directory containing height models", type=str)
    parser.add_argument("center_lat", help="Latitude of center point", type=float)
    parser.add_argument("center_lng", help="Longtitude of center point", type=float)
    parser.add_argument("width", help="Width of model in metres", type=int)
    parser.add_argument("height", help="Height of model in metres", type=int)
    parser.add_argument("aggreg_size", help="How many pixels are aggregated using max method", type=int)
    parser.add_argument("num_tiles_x", help="Number files to split into on x-axis", type=int)
    parser.add_argument("num_tiles_y", help="Number files to split into on y-axis", type=int)
    parser.add_argument("dir_out", help="Path to output directory", type=str)
    parser.add_argument("model_name", help="Name of output model", type=str)
    parser.add_argument("--pixel_size", help="Pixel size in metres", type=str)

    args = parser.parse_args()

    surface_range = convert_coordinates(args.center_lat, args.center_lng, args.width, args.height) 

    pixel_size = args.pixel_size or DEFAULT_PIXEL_SIZE
    surface = get_surface(args.data_dir, surface_range, pixel_size)

    surface = aggregate(surface, args.aggreg_size)
    surface.data *= HEIGHTS_MULTIPLIER
    surface.data += HEIGHTS_EXTRA

    tiles = get_tiles(surface, args.num_tiles_x, args.num_tiles_y)

    os.makedirs(args.dir_out, exist_ok=True)

    for idx_x in range(args.num_tiles_x):
        for idx_y in range(args.num_tiles_y):

            tile = tiles[idx_x, idx_y]
            mesh = meshify_surface(tile)

            file_out = f"{args.model_name} {idx_x}_{idx_y}.{OUTPUT_FORMAT}"
            file_out_path = os.path.join(args.dir_out, file_out)
            mesh.save_current_mesh(file_out_path)

main()
