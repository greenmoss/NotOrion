import unittest

import models.galaxy.black_holes

class TestBlackHoles(unittest.TestCase):
	def setUp(self):
		unittest.TestCase.setUp(self)
		self.black_holes = models.galaxy.black_holes.BlackHoles()
	
	def test_new_empty(self):
		"A new BlackHoles object should be empty."
		self.assertEqual([], self.black_holes.list)
	
	def test_add_black_hole(self):
		"Adding a black hole should increment the count."
		self.black_holes.add((0,0))
		self.assertEqual(1, len(self.black_holes.list))
