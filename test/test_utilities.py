import unittest

import utilities

class TestRandomDispersedCoordinates(unittest.TestCase):

    def testReversedBounds(self):
        "Top should be greater than bottom, and right should be greater than left."
        self.assertRaises(utilities.RangeException, utilities.random_dispersed_coordinates, bottom=5, top=-5)
        self.assertRaises(utilities.RangeException, utilities.random_dispersed_coordinates, left=5, right=-5)

    def testTooNarrow(self):
        "If there is insufficient horizontal space, should raise an exception."
        self.assertRaises(utilities.RangeException, utilities.random_dispersed_coordinates, 0, 0, 10, 1, 2, 2)

    def testTooShort(self):
        "If there is insufficient vertical space, should raise an exception."
        self.assertRaises(utilities.RangeException, utilities.random_dispersed_coordinates, 0, 0, 1, 10, 2, 2)

    def testTooSmall(self):
        "If there is insufficient area, should raise an exception."
        self.assertRaises(utilities.RangeException, utilities.random_dispersed_coordinates, 0, 0, 1, 1, 5, 0)
    
    def testDivisionLimits(self):
        "If we request too many coordinates/divisions, or <= 0, should raise an error."
        self.assertRaises(utilities.RangeException, utilities.random_dispersed_coordinates, amount=132000)
        self.assertRaises(utilities.RangeException, utilities.random_dispersed_coordinates, amount=0)

    def testCoordinateCount(self):
        "The number of coordinates returned should equal the number requested."
        coordinates = utilities.random_dispersed_coordinates( amount=5133, dispersion=1 )
        self.assertEqual(len(coordinates), 5133)
    
    def testRectangleDivisions(self):
        "Divisions of rectangles with known inputs should produce known results."
        rectangles = []
        utilities.recurse_into_rectangle(-10, -10, 10, 10, 1, 2, rectangles)
        self.assertEqual(rectangles, [(-10, -10, 10, 10)])

    def testMinimumLength(self):
        "When recursing into a rectangle, a length < 1 should raise an exception."
        rectangles = []
        self.assertRaises(utilities.RangeException, utilities.recurse_into_rectangle, -10, -10, 10, 10, 1, 0, rectangles)
    
    def testCoordinatesWithinMargin(self):
        "Given an evenly-divisible rectangle and maximum margins, coordinates should be known."
        coordinates = utilities.random_dispersed_coordinates( 0, 0, 2, 5, amount=2, dispersion=2 )
        self.assertEqual(coordinates, [(1, 1), (4, 1)])

class TestCircleVertices(unittest.TestCase):
    def testVertices(self):
        "Given a radius, vertices should match a known amount."
        vertices = utilities.circle_vertices(2)
        self.assertEqual(
            vertices, 
            [
                (2.0, 0.0), (1.7321, -1.0), (1.0, -1.7321), 
                (0.0, -2.0), (-1.0, -1.7321), (-1.7321, -1.0), 
                (-2.0, -0.0), (-1.7321, 1.0), (-1.0, 1.7321),
                (-0.0, 2.0), (1.0, 1.7321), (1.7321, 1.0), 
                (2.0, 0.0)
            ]
        )

class TestChooseFromProbability(unittest.TestCase):
    def test_total_0(self):
        "If probabilities total zero, result should be the (alpha-sort) first probability."
        table = {'c': 0, 'a':0, 'b': 0}
        self.assertEqual(utilities.choose_from_probability(table), 'a')
    
    def test_zeroed_key(self):
        "If a key has value zero, it should never be the return value."
        table = {'a': 0, 'b': 1}
        self.assertEqual(utilities.choose_from_probability(table), 'b')
    

