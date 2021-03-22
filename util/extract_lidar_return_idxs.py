import numpy as np
import pylas
import os

FILE_IN = r"C:\data\lidar\723_6175.las"
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

las = pylas.read(FILE_IN)

returns = las['number_of_returns']
print(type(returns))
print(returns.shape)

returns = np.unique(returns)
print(returns.shape)
print(returns)

for n_return in returns:

    las = pylas.read(FILE_IN)
    las.points = las.points[las.classification == 5]
    las.points = las.points[las['number_of_returns'] == n_return]

    file_out_path = os.path.join(DIR_OUT, f"{n_return}.las")
    las.write(file_out_path)

# for class_key in CLASSES:
#     class_name = CLASSES[class_key]
#     print(class_name)
#     las = pylas.read(FILE_IN)
#     las.points = las.points[las.classification == class_key]
#     file_out_path = os.path.join(DIR_OUT, class_name + ".las")
#     las.write(file_out_path)
