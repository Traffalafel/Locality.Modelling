import rasterio
import rasterio.merge

FILES_IN_PATH = [
    r"D:\PrintCitiesData\DHM_overflade\DSM_1km_6172_721.tif",
    r"D:\PrintCitiesData\DHM_overflade\DSM_1km_6172_722.tif",
    r"D:\PrintCitiesData\DHM_overflade\DSM_1km_6172_723.tif"
]
FILE_OUT_PATH = r"C:\Users\traff\source\repos\PrintCities.Modelling\tifs\merged.tif"

def main():

    datasets = []
    for file_path in FILES_IN_PATH:
        ds = rasterio.open(file_path)
        datasets.append(ds)

    contents, transform  = rasterio.merge.merge(datasets)

    heights = contents[0,:,:]

    height = heights.shape[0]
    width = heights.shape[1]

    dataset_out = rasterio.open(
        FILE_OUT_PATH,
        mode='w',
        driver='GTiff',
        width=width,
        height=height,
        count=1,
        transform=transform,
        dtype=heights.dtype
    )

    dataset_out.write(heights, 1)

main()