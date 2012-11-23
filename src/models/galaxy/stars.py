import os
import random
import logging
logger = logging.getLogger(__name__)

from globals import g

import masses
import orbitals

class Stars(object):
	max_name_length = 18
	min_name_length = 2

	colors = [
		'blue',
		'brown',
		'green',
		'orange',
		'red',
		'white',
		'yellow',
	]

	max_orbits = 5
	
	def __init__(self, orbitals):
		self.orbitals = orbitals

		self.available_names = []
		with open(os.path.join(g.paths['resources_dir'], 'star_names.txt')) as star_names_file:
			for line in star_names_file:
				self.available_names.append(line.rstrip())

		self.list = []
	
	def add(self, coordinate, color):
		name = self.available_names.pop( random.randint(0, len(self.available_names)-1)) 
		self.list.append( Star( coordinate, name, self.orbitals, color) )

class Star(masses.Mass):
	"""A star that may have orbiting planets, gas giants, etc."""

	def __init__(self, coordinates, name, orbitals=None, type='yellow'):
		if (len(name) > Stars.max_name_length) or (len(name) < Stars.min_name_length):
			raise Exception, "name must be %d to %d characters long"%(Stars.max_name_length,Stars.min_name_length)
		self.name = name

		if not type in Stars.colors:
			raise Exception, 'unknown star type: %s'%type
		self.type = type

		super(Star, self).__init__(coordinates)

		self.worm_hole = None

		self.orbits = []
		if orbitals is not None:
			self.set_orbits(orbitals)

	def set_orbits(self, orbitals):
		"Set objects that orbit this star."
		logger.debug("%s: %s", self.name, self.type)
		for orbit_number in range(0,Stars.max_orbits):
			orbital = orbitals.add(self, orbit_number)
			self.orbits.append(orbital)
