import unittest

from globals import g
import models.galaxy.stars
import models.galaxy.orbitals

class TestStar(unittest.TestCase):
	def setUp(self):
		unittest.TestCase.setUp(self)
		self.orbitals = models.galaxy.orbitals.Orbitals()

	def test_name_too_long(self):
		"If a star is created with a name that is too long, should raise an exception."
		self.assertRaises(Exception, models.galaxy.stars.Star, (0,0), 'floccinoccinihilipilification', self.orbitals)

	def test_name_too_short(self):
		"If a star is created with a name that is too short, should raise an exception."
		self.assertRaises(Exception, models.galaxy.stars.Star, (0,0), 'a', self.orbitals)

	def test_invalid_color(self):
		"If a star is created with an invalid color, should raise an exception."
		self.assertRaises(Exception, models.galaxy.stars.Star, (0,0), 'Alpha Centauri', self.orbitals, 'mauve')

	def test_orbit_count(self):
		"Stars should have 5 orbitals."
		star = models.galaxy.stars.Star((0,0), 'Alpha Centauri', self.orbitals)
		self.assertEqual(len(star.orbits), 5)
