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
		self.assertEqual(self.config.age, None)
		self.assertEqual(self.config.limits, None)
	
	def test_initial_dispersion(self):
		"New GalaxyConfig object should have dispersion of 100."
		self.assertEqual(self.config.dispersion, 100)
	
	def test_merge_invalid_config(self):
		"When merging into a GalaxyConfig, an invalid merge key should raise an exception."
		self.assertRaises(Exception, self.config.merge, {'blah':1})
	
	def test_merge_config(self):
		"When merging into a GalaxyConfig, attribute values should become merged values."
		self.config.merge({'age': 'Mature'})
		self.assertEqual(self.config.age, 'Mature')

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
			self.setup.galaxy_settings['worm_hole_count'], 
			models.setup.Setup.difficulty_custom_settings['Beginner']['worm_hole_count']
		)

	def test_set_galaxy_from_difficulty_beginner_nebulae(self):
		"Setting galaxy difficulty to beginner should have known nebula count."
		self.setup.set_galaxy_from_difficulty('Beginner')
		self.assertEqual(
			self.setup.galaxy_settings['nebulae_count'], 
			models.setup.Setup.difficulty_custom_settings['Beginner']['nebulae_count']
		)
	
	def test_generate_galaxy_with_empty(self):
		"Generating a galaxy without any settings should raise an exception."
		self.assertRaises(Exception, self.setup.generate_galaxy)
	
	# need to move generate_galaxy() out of setup
	# and to do that, need to turn galaxy_settings into an object
	#def test_generate_galaxy_without_object_pool(self):
	#	"Generating a galaxy without setting an object pool should create the default object pool."
	#	self.setup.set_galaxy_from_difficulty()
	#	self.setup.generate_galaxy()
	#	self.assertEqual(
	#		self.setup.galaxy_settings['object_pool'], 
	#		models.setup.Setup.age_defaults['Mature']['object_pool']
	#	)
