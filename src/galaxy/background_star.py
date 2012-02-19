#! python -O
from __future__ import division

from globals import g

class BackgroundStar(object):
	"""A simplified star for the background, to be drawn only as a point source."""

	def __init__(self, coordinates, color):
		self.coordinates = (coordinates[0], coordinates[1], 0)
		self.color = color
