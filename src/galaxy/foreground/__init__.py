#! python -O
from __future__ import division

from globals import g

class Foreground(object):
	"""All foreground objects that appear in the galaxy window, eg stars, black holes, and nebulae."""

	def __init__(self, coordinates):
		if not (-10000 < coordinates[0] < 10000) or not (-10000 < coordinates[1] < 10000):
			raise Exception, "coordinates must be between -10000 and 10000"

		self.coordinates = coordinates
