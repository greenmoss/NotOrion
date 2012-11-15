import unittest
import os
import sys

import models.setup

class TestSetup(unittest.TestCase):
	def setUp(self):
		unittest.TestCase.setUp(self)
		self.setup = models.setup.Setup()
	
	def test_init(self):
		"New Setup object should have empty settings."
		self.assertEqual(self.setup.galaxy_settings, {})
	
	def test_set_galaxy_from_difficulty_invalid_difficulty(self):
		"Setting galaxy difficulty with an invalid difficulty should raise an exception."
		self.assertRaises(Exception, self.setup.set_galaxy_from_difficulty, 'blah')

	def test_set_galaxy_from_difficulty_default_parameters(self):
		"Setting galaxy difficulty without a difficulty should have default settings."
		self.setup.set_galaxy_from_difficulty()
		self.assertEqual(self.setup.galaxy_settings['age'], 'Mature')
		self.assertEqual(
			self.setup.galaxy_settings['size'],
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
