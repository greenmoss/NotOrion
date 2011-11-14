import unittest

# path to our code (in unix): "../src"
import os
import sys
sys.path.append(
	os.path.join(
		os.path.dirname(os.path.abspath( __file__ )), os.path.pardir, 'src'
	)
)
import application
application.set_paths()

import utilities

class TestRandomDispersedCoordinates(unittest.TestCase):

	def testReversedBounds(self):
		"Top should be greater than bottom, and right should be greater than left."
		self.assertRaises(utilities.RangeException, utilities.random_dispersed_coordinates, bottom=5, top=-5)
		self.assertRaises(utilities.RangeException, utilities.random_dispersed_coordinates, left=5, right=-5)

	def testOverCrowding(self):
		"If we pass in too many, too-widely-dispersed coordinates for the given area, should raise an exception."
		self.assertRaises(utilities.RangeException, utilities.random_dispersed_coordinates, -5, -5, 5, 5, 200)
		self.assertRaises(utilities.RangeException, utilities.random_dispersed_coordinates, -5, -5, 5, 5, 10, 15)
	
	def testDivisionLimits(self):
		"If we request too many coordinates/divisions, or <= 0, should raise an error."
		self.assertRaises(utilities.RangeException, utilities.random_dispersed_coordinates, amount=132000)
		self.assertRaises(utilities.RangeException, utilities.random_dispersed_coordinates, amount=0)

	def testCoordinateCount(self):
		"The number of coordinates returned should equal the number requested."
		coordinates = utilities.random_dispersed_coordinates( amount=4, dispersion=3 )
		self.assertEqual(len(coordinates), 4)
		coordinates = utilities.random_dispersed_coordinates( amount=5133, dispersion=1 )
		self.assertEqual(len(coordinates), 5133)
	
	def testRectangleDivisions(self):
		"Divisions of rectangles with known inputs should produce known results."
		rectangles = []
		utilities.recurse_into_rectangle(-10, -10, 10, 10, 1, 2, rectangles)
		self.assertEqual(rectangles, [(-10, -10, 10, 10)])
		rectangles = []
		utilities.recurse_into_rectangle(-10, -10, 10, 10, 3, 2, rectangles, seed=1)
		self.assertEqual(rectangles, [(-10, -1, -2, 10), (-10, -10, -2, -2), (-1, -10, 10, 10)])

	def testMinimumLength(self):
		"When recursing into a rectangle, a length < 1 should raise an exception."
		rectangles = []
		self.assertRaises(utilities.RangeException, utilities.recurse_into_rectangle, -10, -10, 10, 10, 1, 0, rectangles)
	
	def testCoordinatesWithinMargin(self):
		"Given an evenly-divisible rectangle and maximum margins, coordinates should be known."
		coordinates = utilities.random_dispersed_coordinates( -1, -3, 2, 4, amount=2, dispersion=3 )
		self.assertEqual(coordinates, [(-2, 0), (2, 0)])
		coordinates = utilities.random_dispersed_coordinates( 10, 10, 15, 15, amount=4, dispersion=2 )
		self.assertEqual(coordinates, [(14, 11), (11, 11), (11, 14), (14, 14)])

if __name__ == "__main__":
	unittest.main()
