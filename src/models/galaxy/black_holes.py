#! python -O
import os

from globals import g

import masses

class BlackHoles(object):

	def __init__(self):
		self.list = []
	
	def add(self, coordinates):
		self.list.append(BlackHole(coordinates))

class BlackHole(masses.Mass):
	"""A black hole. It consumes objects that wander too close."""

	def __init__(self, coordinates):
		super(BlackHole, self).__init__(coordinates)
