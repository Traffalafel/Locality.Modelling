import unittest
from locality.core.Coordinate import Coordinate, CoordinateFactory

class CoordinateTest(unittest.TestCase):

    def setUp(self):
        self.coord = Coordinate(720000, 6170000)

    def testIsSetup(self):
        self.assertEqual(1, 2)
