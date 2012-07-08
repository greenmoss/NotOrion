#! python -O
import os

from globals import g

import masses

class BlackHole(masses.Mass):
	"""A black hole. It consumes objects that wander too close."""

	def __init__(self, coordinates):
		super(BlackHole, self).__init__(coordinates)
