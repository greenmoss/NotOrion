import unittest

import models.galaxy
import models.galaxy.black_holes
import models.galaxy.orbitals
import models.galaxy.stars
import models.setup

class TestOrbitals(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.galaxy = models.galaxy.Galaxy()
        setup = models.setup.Setup()
        setup.set_galaxy_from_difficulty()
        config = setup.get_galaxy_config()
        self.galaxy.generate(config)
    
    def test_add_close_objects(self):
        "Adding two objects too close together should raise an exception."
        test_stars = models.galaxy.stars.Stars(models.galaxy.orbitals.Orbitals())
        test_stars.add((0,0), 'yellow')
        self.galaxy.stars = test_stars

        test_black_holes = models.galaxy.black_holes.BlackHoles()
        test_black_holes.add((0,0))
        self.galaxy.black_holes = test_black_holes

        self.galaxy.derive_bounding_lines()
        self.galaxy.normalize()

        self.assertRaises(Exception, self.galaxy.derive_min_max_distances)
    
    def test_equidistant_bounding_lines(self):
        "Bounding top should match bottom, and left should match right."
        self.assertEqual(-self.galaxy.left_bounding_x, self.galaxy.right_bounding_x)
        self.assertEqual(-self.galaxy.bottom_bounding_y, self.galaxy.top_bounding_y)
    
    def test_min_max_distances(self):
        "Given a known set of stars and black holes, should have known min and max distances."
        test_stars = models.galaxy.stars.Stars(models.galaxy.orbitals.Orbitals())
        test_stars.add((0,0), 'yellow')
        test_stars.add((0,10), 'yellow')
        self.galaxy.stars = test_stars

        test_black_holes = models.galaxy.black_holes.BlackHoles()
        test_black_holes.add((0,20))
        self.galaxy.black_holes = test_black_holes

        self.galaxy.derive_bounding_lines()
        self.galaxy.normalize()
        self.galaxy.derive_min_max_distances()

        self.assertEqual(self.galaxy.min_distance, 10.0)
        self.assertEqual(self.galaxy.max_distance, 20.0)

    def test_save(self):
        "Saved galaxy should be identical object as galaxy."
        self.assertEqual(self.galaxy.save(), self.galaxy)
