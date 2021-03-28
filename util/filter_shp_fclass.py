import geopandas
import sys
from os.path import join

FILE_IN_PATH = r"C:\Users\traff\source\repos\PrintCities.Modelling\shps\roads_cph.shp"
DIR_OUT_PATH = r"C:\Users\traff\source\repos\PrintCities.Modelling\shps\fclasses"

# Constants
FCLASSES = [
    'motorway', 
    'trunk', 
    'primary', 
    'secondary', 
    'tertiary', 
    'unclassified', 
    'residential', 
    'living_street', 
    'pedestrian', 
    'motorway_link', 
    'trunk_link', 
    'primary_link', 
    'secondary_link', 
    'service', 
    'track', 
    'bridleway', 
    'cycleway', 
    'footway', 
    'Path', 
    'steps', 
    'unkown',
]

def filter(dataframe, fclass_filter):
    df_out = geopandas.GeoDataFrame(columns=['geometry', 'fclass'], crs=dataframe.crs)
    for idx, row in dataframe.iterrows():
        fclass = row['fclass']
        if fclass != fclass_filter:
            continue
        geometry = row['geometry']
        df_out.loc[len(df_out)] = [geometry, fclass]
    return df_out

def main():
    df = geopandas.read_file(FILE_IN_PATH)
    for fclass_filter in FCLASSES:
        print(f"filtering {fclass_filter}")
        df_filtered = filter(df, fclass_filter)
        n_rows = len(df_filtered)
        print(f"no. of rows: {n_rows}")
        if n_rows == 0:
            continue
        file_name = f"roads_{fclass_filter}.shp"
        file_path = join(DIR_OUT_PATH, file_name)
        df_filtered.to_file(file_path)

main()