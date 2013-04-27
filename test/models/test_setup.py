import unittest
import os
import sys

import models.setup

class TestGalaxyConfig(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.config = models.setup.GalaxyConfig()
    
    def test_initial_empty_settings(self):
        "New GalaxyConfig object should have empty settings."
        self.assertEqual(self.config.limits, None)
    
    def test_merge_invalid_config(self):
        "When merging into a GalaxyConfig, an invalid merge key should raise an exception."
        self.assertRaises(Exception, self.config.merge, {'blah':1})
    
    def test_merge_config(self):
        "When merging into a GalaxyConfig, attribute values should become merged values."
        self.config.merge({'age': 'Mature'})
        self.assertEqual(self.config.age, 'Mature')
    
    def test_is_set_invalid_config(self):
        "In a GalaxyConfig, checking for an invalid configuration should raise an exception."
        self.assertRaises(Exception, self.config.is_set, 'blah')
    
    def test_is_set_with_set_config(self):
        "In a GalaxyConfig, checking for a set config should return true."
        self.config.star_count = 5
        self.assertIs(self.config.is_set('star_count'), True)
    
    def test_is_set_with_unset_config(self):
        "In a GalaxyConfig, checking for an unset config should return false."
        self.assertIs(self.config.is_set('limits'), False)

class TestSetup(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.setup = models.setup.Setup()
    
    def test_set_galaxy_from_difficulty_invalid_difficulty(self):
        "Setting galaxy difficulty with an invalid difficulty should raise an exception."
        self.assertRaises(Exception, self.setup.set_galaxy_from_difficulty, 'blah')

    def test_set_galaxy_from_difficulty_default_parameters(self):
        "Setting galaxy difficulty without a difficulty should have default settings."
        self.setup.set_galaxy_from_difficulty()
        self.assertEqual(self.setup.galaxy_config.age, 'Mature')
        self.assertEqual(
            self.setup.galaxy_config.size,
            models.setup.Setup.difficulty_preset_sizes['Normal']
        )

    def test_set_galaxy_from_difficulty_beginner_worm_holes(self):
        "Setting galaxy difficulty to beginner should have known worm hole count."
        self.setup.set_galaxy_from_difficulty('Beginner')
        self.assertEqual(
            self.setup.galaxy_config.worm_hole_count, 
            models.setup.Setup.difficulty_custom_settings['Beginner']['worm_hole_count']
        )

    def test_set_galaxy_from_difficulty_beginner_nebulae(self):
        "Setting galaxy difficulty to beginner should have known nebula count."
        self.setup.set_galaxy_from_difficulty('Beginner')
        self.assertEqual(
            self.setup.galaxy_config.nebulae_count, 
            models.setup.Setup.difficulty_custom_settings['Beginner']['nebulae_count']
        )
    
    def test_get_galaxy_config_with_empty(self):
        "Generating a galaxy without any settings should raise an exception."
        self.assertRaises(Exception, self.setup.get_galaxy_config)

    def test_get_galaxy_config_with_missing_object_pool(self):
        "Generating a galaxy without setting an object pool should create the default object pool."
        self.setup.set_galaxy_from_difficulty()
        self.assertEqual(
            self.setup.get_galaxy_config().object_pool, 
            models.setup.Setup.age_defaults['Mature']['object_pool']
        )
