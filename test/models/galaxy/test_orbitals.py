import unittest

import models.galaxy.stars
import models.galaxy.orbitals

class TestOrbitals(unittest.TestCase):
	def setUp(self):
		unittest.TestCase.setUp(self)
		self.orbitals = models.galaxy.orbitals.Orbitals()
	
	def test_new_empty(self):
		"A new Orbitals object should be empty."
		self.assertEqual([], self.orbitals.planets)
		self.assertEqual([], self.orbitals.asteroid_belts)
		self.assertEqual([], self.orbitals.gas_giants)
	
	def test_add_invalid_type(self):
		"Adding an orbital with an invalid type should raise an exception."
		star = models.galaxy.stars.Star((0,0), 'Sol')
		self.assertRaises(Exception, self.orbitals.add, star, 1, 'invalid')
	
	def test_add_twice(self):
		"Adding the an orbital for a star which already has one should riase an exception."
		star = models.galaxy.stars.Star((0,0), 'Sol')
		self.assertRaises(Exception, self.orbitals.add, star, 1, 'planet')
