import geopandas
from shapely.geometry import Polygon
import matplotlib.pyplot as plt

# Args
FILE_IN_PATH = r"D:\PrintCitiesData\OpenStreetMap\gis_osm_roads_free_1.shp"
FILE_OUT_PATH = r"C:\Users\traff\source\repos\PrintCities.Modelling\shps\roads_cph.shp"
BOUNDS_W = 700000
BOUNDS_E = 731000
BOUNDS_S = 6170000
BOUNDS_N = 6201000

# Constants
ETRS89_UTM32N = 3044

def clip(dataframe, bounds):
    
    dataframe = dataframe.to_crs(ETRS89_UTM32N)

    bounds_w, bounds_e, bounds_s, bounds_n = bounds
    polygon = Polygon([
        (bounds_w, bounds_s),
        (bounds_w, bounds_n),
        (bounds_e, bounds_n),
        (bounds_e, bounds_s)
    ])
    poly_gdf = geopandas.GeoDataFrame([1], geometry=[polygon], crs=dataframe.crs)

    return geopandas.clip(dataframe, poly_gdf)
    
def main():
    df = geopandas.read_file(FILE_IN_PATH)
    bounds = (
        BOUNDS_W,
        BOUNDS_E,
        BOUNDS_S,
        BOUNDS_N
    )
    df = clip(df, bounds)
    df.to_file(FILE_OUT_PATH)

main()