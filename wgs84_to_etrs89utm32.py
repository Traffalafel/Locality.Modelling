import sys
from pyproj import Transformer

WSG84_EPSG = 4326
ETRS89_UTM32_EPSG = 3044

input_lat = sys.argv[1]
input_lon = sys.argv[2]

transformer = Transformer.from_crs(WSG84_EPSG, ETRS89_UTM32_EPSG)

output_y, output_x = transformer.transform(input_lat, input_lon)

print(f"X: {output_x}, Y: {output_y}")
