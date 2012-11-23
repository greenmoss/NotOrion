import unittest

import models.galaxy.masses

class TestMass(unittest.TestCase):
	def test_add_invalid_coordinate(self):
		"Adding a mass with an out-of-range coordinate should raise an exception."
		bignum = 100000000 
		self.assertRaises(Exception, models.galaxy.masses.Mass, (0,-bignum))
		self.assertRaises(Exception, models.galaxy.masses.Mass, (0,bignum))
		self.assertRaises(Exception, models.galaxy.masses.Mass, (-bignum,0))
		self.assertRaises(Exception, models.galaxy.masses.Mass, (bignum,0))
	
	def test_coordinate(self):
		"Adding a mass with a coordinate should set that coordinate."
		mass = models.galaxy.masses.Mass((10,10))
		self.assertEqual((10,10), mass.coordinates)
