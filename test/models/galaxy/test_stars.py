import unittest

import models.galaxy.stars
import models.galaxy.orbitals

class TestStars(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        orbitals = models.galaxy.orbitals.Orbitals()
        self.stars = models.galaxy.stars.Stars(orbitals)
    
    def test_new_has_available_names(self):
        "On Stars creation, there should be star names."
        self.assertGreater(len(self.stars.available_names), 0)
    # TODO: testing with a smaller number of star names, and running out
    
    def test_new_empty_list(self):
        "On Stars creation, list of stars should be empty."
        self.assertEqual([], self.stars.list)
    
    def test_add_star_increments_list(self):
        "Adding a Star should increment the number of stars."
        self.stars.add((0,0), 'yellow')
        self.assertEqual(len(self.stars.list), 1)

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
