from Range import Range
import numpy as np

class Surface():

    def __init__(self, data: np.ndarray, range: Range):
        self.data = data
        self.range = range
