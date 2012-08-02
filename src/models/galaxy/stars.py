#! python -O
import os

from globals import g

import masses

class Star(masses.Mass):
	"""A star that may have orbiting planets, gas giants, etc."""

	max_name_length = 18
	min_name_length = 2

	available_colors = [
		'blue',
		'brown',
		'green',
		'orange',
		'red',
		'white',
		'yellow',
	]

	available_names = []
	with open(os.path.join(g.paths['resources_dir'], 'star_names.txt')) as star_names_file:
		for line in star_names_file:
			available_names.append(line.rstrip())

	def __init__(self, coordinates, name, type='yellow'):
		if (len(name) > self.max_name_length) or (len(name) < self.min_name_length):
			raise RangeException, "name must be %d to %d characters long"%(self.max_name_length,self.min_name_length)
		self.name = name

		if not type in self.available_colors:
			raise DataError, 'unknown star type: %s'%type
		self.type = type

		super(Star, self).__init__(coordinates)

		self.worm_hole = None
