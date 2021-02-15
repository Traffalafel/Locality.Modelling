import geopandas
from shapely.geometry import Point
import matplotlib.pyplot as plt

SIZE = 10

def main():
    df = geopandas.GeoDataFrame(columns=['geometry', 'fclass'], crs=3044)
    circle = Point(700000, 6170000).buffer(SIZE)
    df.loc[0] = [circle, 'test']
    df.plot()
    plt.show()

main()