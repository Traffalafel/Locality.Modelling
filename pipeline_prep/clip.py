import geopandas
from shapely.geometry import Polygon

def clip(dataframe, bounds):
    
    bounds_w, bounds_e, bounds_s, bounds_n = bounds
    polygon = Polygon([
        (bounds_w, bounds_s),
        (bounds_w, bounds_n),
        (bounds_e, bounds_n),
        (bounds_e, bounds_s)
    ])
    poly_gdf = geopandas.GeoDataFrame([1], geometry=[polygon], crs=dataframe.crs)

    df_out = geopandas.clip(dataframe, poly_gdf)

    # Filter out non-polygon rows
    # df_out = df_out[df_out['geometry'].apply(lambda x: x.type == "Polygon")]

    return df_out