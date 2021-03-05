import numpy as np
import pylas
import os

FILE_IN = r"D:\PrintCitiesData\lidar\ryde.las"
DIR_OUT = r"C:\Users\traff\source\repos\PrintCities.Modelling\data\lidar"
CLASSES = {
    1: "unclassified",
    2: "ground",
    3: "low_vegetation",
    4: "medium_vegetation",
    5: "high_vegetation",
    6: "building",
    7: "noise",
    9: "water"
}

for class_key in CLASSES:
    class_name = CLASSES[class_key]
    print(class_name)
    las = pylas.read(FILE_IN)
    las.points = las.points[las.classification == class_key]
    file_out_path = os.path.join(DIR_OUT, class_name + ".las")
    las.write(file_out_path)
