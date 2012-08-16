#! python -O
import os
import random

from globals import g

import masses

class Stars(object):
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
	
	def __init__(self):
		self.available_names = []
		with open(os.path.join(g.paths['resources_dir'], 'star_names.txt')) as star_names_file:
			for line in star_names_file:
				self.available_names.append(line.rstrip())

		self.list = []
	
	def add(self, coordinate, color):
		self.list.append(
			Star(
				coordinate, 
				self.available_names.pop(
					random.randint(0, len(self.available_names)-1)
				), 
				color
			),
		)

class Star(masses.Mass):
	"""A star that may have orbiting planets, gas giants, etc."""

	def __init__(self, coordinates, name, type='yellow'):
		if (len(name) > Stars.max_name_length) or (len(name) < Stars.min_name_length):
			raise RangeException, "name must be %d to %d characters long"%(Stars.max_name_length,Stars.min_name_length)
		self.name = name

		if not type in Stars.available_colors:
			raise DataError, 'unknown star type: %s'%type
		self.type = type

		super(Star, self).__init__(coordinates)

		self.worm_hole = None
