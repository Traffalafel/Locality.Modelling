class Range():

    def __init__(self, x_min: int, x_max: int, y_min: int, y_max: int):

        assert(x_min <= x_max)
        assert(y_min <= y_max)

        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

        self.width = x_max - x_min
        self.height = y_max - y_min

    def is_within(self, x: int, y: int) -> bool:
        return (self.x_min <= x and x <= self.x_max) and (self.y_min <= y and y <= self.y_max)

    # Determines whether another 2-d range is overlapping the 2-d range contained by this file
    def is_overlapping(self, other: 'Range') -> bool:
        return other.x_min <= self.x_max and other.x_max >= self.x_min and other.y_min <= self.y_max and other.y_max >= self.y_min