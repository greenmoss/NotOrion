import unittest

import models.galaxy.worm_holes
import models.galaxy.stars
import models.galaxy.orbitals

class TestWormHoles(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        orbitals = models.galaxy.orbitals.Orbitals()
        self.stars = models.galaxy.stars.Stars(orbitals)
        self.stars.add((0,0), 'yellow')
        self.stars.add((10,0), 'yellow')
        self.stars.add((20,0), 'yellow')
        self.stars.add((30,0), 'yellow')
        self.stars.add((40,0), 'yellow')
        self.stars.add((50,0), 'yellow')
    
    def test_list_length(self):
        "Creating worm holes should produce a list length equalling the requested amount of worm holes."
        self.wormholes = models.galaxy.worm_holes.WormHoles(2, self.stars)
        self.assertEqual(len(self.wormholes.list), 2)

class TestWormHole(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        orbitals = models.galaxy.orbitals.Orbitals()
        self.star1 = models.galaxy.stars.Star((0,0), 'Sol', orbitals)
        self.star2 = models.galaxy.stars.Star((10,10), 'Alpha Centauri', orbitals)
        self.wormhole = models.galaxy.worm_holes.WormHole(self.star1, self.star2)

    def test_existing_wormholes(self):
        "If a worm hole is created using a star which already has a worm hole, should raise an exception."
        self.assertRaises(Exception, models.galaxy.worm_holes.WormHole, self.star1, self.star2)
    
    def test_endpoints(self):
        "After creating a worm hole, the worm hole endpoints should match the given stars."
        self.assertEqual(self.wormhole.endpoints, (self.star1, self.star2))
    
    def test_star_refs(self):
        "After creating a worm hole, refs to star1 and star2 should match given stars."
        self.assertEqual(self.wormhole.star1, self.star1)
        self.assertEqual(self.wormhole.star2, self.star2)
