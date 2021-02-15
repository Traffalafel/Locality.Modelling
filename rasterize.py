from osgeo import ogr, gdal
import matplotlib.pyplot as plt
import geopandas

SHP_IN_PATH = r'.\shps\roads_etrs89.shp'
TIF_OUT_PATH = r'.\tifs\roads.tiff'

def rasterize(df, file_out_path):

    # Define pixel_size and NoData value of new raster
    pixel_size = 1
    NoData_value = 255

    # Open the data source and read in the extent
    source_ds = ogr.Open(df.to_json())
    source_layer = source_ds.GetLayer()
    source_srs = source_layer.GetSpatialRef()
    x_min, x_max, y_min, y_max = source_layer.GetExtent()

    # Create the destination data source
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)

    mem_driver = gdal.GetDriverByName('GTiff')
    target_ds = mem_driver.Create(TIF_OUT_PATH, x_res, y_res, gdal.GDT_Byte)
    target_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))
    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(NoData_value)

    # Rasterize
    gdal.RasterizeLayer(target_ds, [1], source_layer, burn_values=[1])

def main():
    df = geopandas.read_file(SHP_IN_PATH)
    rasterize(df, TIF_OUT_PATH)

main()