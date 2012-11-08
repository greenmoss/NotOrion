import unittest
import os
import sys

sys.path.append(
	os.path.join(
		os.path.dirname(os.path.abspath( __file__ )), os.path.pardir, 'src'
	)
)

from globals import g
import application
import models.setup

class TestSetup(unittest.TestCase):
	
	def test_init(self):
		"New Setup object should have empty settings."
		setup = models.setup.Setup()
		self.assertEqual(setup.galaxy_settings, {})
	
	def test_set_galaxy_from_difficulty_invalid_difficulty(self):
		"Setting galaxy difficulty with an invalid difficulty should raise an exception."
		setup = models.setup.Setup()
		self.assertRaises(Exception, setup.set_galaxy_from_difficulty, 'blah')

	def test_set_galaxy_from_difficulty_default_parameters(self):
		"Setting galaxy difficulty without a difficulty should have default settings."
		setup = models.setup.Setup()
		setup.set_galaxy_from_difficulty()
		self.assertEqual(setup.galaxy_settings['age'], 'Mature')
		self.assertEqual(
			setup.galaxy_settings['size'],
			models.setup.Setup.difficulty_preset_sizes['Normal']
		)

	def test_set_galaxy_from_difficulty_beginner_worm_holes(self):
		"Setting galaxy difficulty to beginner should have known worm hole count."
		setup = models.setup.Setup()
		setup.set_galaxy_from_difficulty('Beginner')
		self.assertEqual(
			setup.galaxy_settings['worm_hole_count'], 
			models.setup.Setup.difficulty_custom_settings['Beginner']['worm_hole_count']
		)

	def test_set_galaxy_from_difficulty_beginner_nebulae(self):
		"Setting galaxy difficulty to beginner should have known nebula count."
		setup = models.setup.Setup()
		setup.set_galaxy_from_difficulty('Beginner')
		self.assertEqual(
			setup.galaxy_settings['nebulae_count'], 
			models.setup.Setup.difficulty_custom_settings['Beginner']['nebulae_count']
		)
	
	def test_generate_galaxy_with_empty(self):
		"Generating a galaxy without any settings should raise an exception."
		setup = models.setup.Setup()
		self.assertRaises(Exception, setup.generate_galaxy)
	
	def test_generate_galaxy_with_empty(self):
		"Generating a galaxy without setting an object pool should create the default object pool."
		setup = models.setup.Setup()
		setup.set_galaxy_from_difficulty()
		setup.generate_galaxy()
		self.assertEqual(
			setup.galaxy_settings['object_pool'], 
			models.setup.Setup.age_defaults['Mature']['object_pool']
		)
