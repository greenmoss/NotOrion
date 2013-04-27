import unittest

import jsonpickle
import pyglet

import models.galaxy.nebulae

class TestNebulae(unittest.TestCase):
    def test_new_empty(self):
        "A new Nebulae object with zero amount should be empty."
        self.assertEqual([], models.galaxy.nebulae.Nebulae(0, None).list)
    
    def test_add_nebula(self):
        "Adding Nebulae should populate the list of nebulae."
        nebulae = models.galaxy.nebulae.Nebulae(2, (-1000, -1000, 1000, 1000))
        self.assertEqual(2, len(nebulae.list))
    
    def test_nebulae_color_cycle(self):
        "Adding multiple nebulae should produce different primary colors."
        nebulae = models.galaxy.nebulae.Nebulae(3, (-1000, -1000, 1000, 1000))
        self.assertNotEqual(
            nebulae.list[0].primary_color_name,
            nebulae.list[1].primary_color_name,
        )
        self.assertNotEqual(
            nebulae.list[1].primary_color_name,
            nebulae.list[2].primary_color_name,
        )
        self.assertNotEqual(
            nebulae.list[2].primary_color_name,
            nebulae.list[0].primary_color_name,
        )

class TestNebula(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.nebula = models.galaxy.nebulae.Nebula((0, 0))
    
    def test_invalid_color(self):
        "Creating a nebula with invalid primary color should raise an exception."
        self.assertRaises(
            Exception,
            models.galaxy.nebulae.Nebula, 
            (0, 0),
            'mauve'
        )
    
    def test_new_no_color(self):
        "Creating a nebula without a color should set a random color."
        self.assertIsNotNone(self.nebula.primary_color_name)
    
    def test_new_has_lobes(self):
        "Creating a nebula should generate lobes."
        self.assertGreaterEqual(len(self.nebula.lobes), 3)

    def test_lobe_color_cycle(self):
        "Lobe images should cycle."
        self.assertNotEqual(
            self.nebula.lobes[0].pyglet_image_resource_file_name,
            self.nebula.lobes[1].pyglet_image_resource_file_name,
        )
        self.assertNotEqual(
            self.nebula.lobes[1].pyglet_image_resource_file_name,
            self.nebula.lobes[2].pyglet_image_resource_file_name,
        )
        self.assertNotEqual(
            self.nebula.lobes[2].pyglet_image_resource_file_name,
            self.nebula.lobes[0].pyglet_image_resource_file_name,
        )

class TestLobe(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.lobe = models.galaxy.nebulae.Lobe((0, 0), 'red')
    
    def test_invalid_color(self):
        "Creating a lobe with invalid primary color should raise an exception."
        self.assertRaises(
            Exception,
            models.galaxy.nebulae.Lobe, 
            (0, 0),
            'mauve'
        )
    
    def test_new_lobe_coordinates(self):
        "Setting a lobe with coordinates should set the lobe's coordinates."
        self.assertEqual((0,0), self.lobe.coordinates)
    
    def test_secondary_color(self):
        "Secondary color should be derived from primary color."
        self.assertIn(self.lobe.secondary_color_name, models.galaxy.nebulae.Lobe.color_names['red'])
    
    def test_getstate(self):
        "Running __getstate__ should strip pyglet_image_resource."
        self.assertNotIn('pyglet_image_resource', self.lobe.__getstate__().keys())
    
    def test_setstate(self):
        "Running __setstate__ should add a pyglet image texture."
        # this is a complete decoded object as of git 06a92146ed3df48e73313500959e13a169c916a5
        """{
            "py/object": "models.galaxy.nebulae.Lobe", 
            "py/state": {
                "coordinates": {
                    "py/tuple": [0, 0]
                }, 
                "image_selector": 2,
                "primary_color_name": "red", 
                "pyglet_image_resource_file_name": "red_pink_nebula_2.png", 
                "rotation": 151, 
                "scale": 0.9287506766119162, 
                "secondary_color_name": "pink"
            }
        }"""
        # but simplicity is good, so use the bare minimum instead:
        lobe = jsonpickle.decode("""{
            "py/object": "models.galaxy.nebulae.Lobe", 
            "py/state": { "pyglet_image_resource_file_name": "red_pink_nebula_2.png" }
        }""")
        self.assertIsInstance(lobe.pyglet_image_resource, pyglet.image.Texture)
