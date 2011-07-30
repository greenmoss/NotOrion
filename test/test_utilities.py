import unittest
import sys
sys.path.append('../src')
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

	def testKnownResults(self):
		"Given a specific seed, random dispersion should produce known set of coordinates."
		coordinates = utilities.random_dispersed_coordinates(
			-5, -5, 5, 5,
			amount=4, dispersion=3, seed=5322
		)
		self.assertEqual(coordinates, [(5, -1), (5, -5), (-4, -2), (2, 2)])
		coordinates = utilities.random_dispersed_coordinates(
			-20, -30, 10, 35,
			amount=10, dispersion=10, seed=330
		)
		self.assertEqual(coordinates, 
			[
				(22, 3), (-23, -18), (-13, -13), (-8, 7), (11, 5),
				(7, -19), (-29, -1), (-18, 8), (31, -8), (26, -20)
			]
		)

if __name__ == "__main__":
	unittest.main()
