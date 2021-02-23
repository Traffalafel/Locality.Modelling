import rasterio
import sys
import os

def get_dir_files(dir_path):
    contents = os.listdir(dir_path)
    files = [c for c in contents if os.path.isfile(os.path.join(dir_path, c))]
    files_tif = [f for f in files if f.split(".")[1] == "tif"]
    return files_tif

def subtract_datasets(ds_1, ds_2):
    heights_1 = ds_1.read(1)
    heights_2 = ds_2.read(1)
    if heights_1.shape != heights_2.shape:
        print(f"Heights do not match!")
        return None
    else:
        return heights_1 - heights_2

def main():
    dir_in_1_path = sys.argv[1]
    dir_in_2_path = sys.argv[2]
    dir_out_path = sys.argv[3]

    files_in = get_dir_files(dir_in_1_path)

    for file in files_in:

        file_in_1_path = os.path.join(dir_in_1_path, file)
        file_in_2_path = os.path.join(dir_in_2_path, file)

        if not os.path.exists(file_in_2_path):
            print(f"skipping {file}")
            continue 

        dataset_1 = rasterio.open(file_in_1_path)
        dataset_2 = rasterio.open(file_in_2_path)

        heights_out = subtract_datasets(dataset_1, dataset_2)

        if heights_out is None:
            print(f"error with {file}. skipping")
            continue
        
        file_out_path = os.path.join(dir_out_path, file)
        dataset_out = rasterio.open(
            file_out_path,
            "w",
            driver="GTiff",
            width=heights_out.shape[1],
            height=heights_out.shape[0],
            count=1,
            crs=dataset_1.crs,
            transform=dataset_1.transform,
            dtype=heights_out.dtype
        )
        dataset_out.write(heights_out, 1)

        print(f"saved {file}")

main()