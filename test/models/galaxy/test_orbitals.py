import unittest

import models.galaxy.stars
import models.galaxy.orbitals

class TestOrbitals(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.orbitals = models.galaxy.orbitals.Orbitals()
        self.star = models.galaxy.stars.Star((0,0), 'Sol')
    
    def test_new_empty(self):
        "A new Orbitals object should be empty."
        self.assertEqual([], self.orbitals.planets)
        self.assertEqual([], self.orbitals.asteroid_belts)
        self.assertEqual([], self.orbitals.gas_giants)
        self.assertEqual({}, self.orbitals.star_orbits)
    
    def test_add_invalid_type(self):
        "Adding an orbital with an invalid type should raise an exception."
        self.assertRaises(Exception, self.orbitals.add, self.star, 1, 'invalid')
    
    def test_add_twice(self):
        "Adding an orbital for a star which already has that orbital number should raise an exception."
        self.orbitals.add(self.star, 1, 'planet')
        self.assertRaises(Exception, self.orbitals.add, self.star, 1, 'planet')
    
    def test_add_planet(self):
        "Adding a planet orbital should increment the planet count."
        self.orbitals.add(self.star, 1, 'planet')
        self.assertEqual(1, len(self.orbitals.planets))
